#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-11-4 10:13 
'''
import scipy.fftpack as scf
import scipy.signal as sg
import numpy as np
from basicFuc.basic import Moudel
import matplotlib.pyplot as plt


class PrachDecoder(Moudel):

    def __init__(self, **kwargs):
        super(PrachDecoder, self).__init__(**kwargs)
        self.gnb_resample = kwargs.get('gnb_resample', 122.88e6)
        self.power_thresh_point = kwargs.get('power_thresh_point', 10)
        self.dectect_thresh = kwargs.get('dectect_thresh', 10)
        self.decoder_fftsize = kwargs.get('decoder_fftsize', 2048)

    def deframe(self, frame, ue_config):
        self.plot(abs(frame[0]), title='收端时域功率谱', xlable='功率')
        # frame, upsample_ratio = self.upsampling(frame, ue_config)

        ##提取有效数据
        upsample_ratio = int(self.gnb_resample / ue_config.ue_resample)
        cp_point = ue_config.cp_num * upsample_ratio
        data_len = ue_config.fftsize_ue * upsample_ratio
        repeat_num = ue_config.repeat_num
        l_ra = ue_config.l_ra
        re_pos = ue_config.re_pos
        vail_data = frame[:, cp_point:cp_point + data_len * repeat_num]
        vail_data_reshape = np.reshape(vail_data, [-1, repeat_num, data_len])
        ##移频
        vail_data_move, seq_len = self.move_frequency(vail_data_reshape, ue_config)
        ##DDC
        ddc_data, after_ddc_len = self.downsampling(vail_data_move, l_ra)
        self.after_ddc_len = after_ddc_len

        data_combine = self.data_combine(ddc_data)
        freq_data = scf.ifftshift(scf.fft(data_combine, axis=-1)) / np.sqrt(data_combine.shape[-1])  # FIXME 降采后的频谱
        freq_vail = freq_data[:, (after_ddc_len - seq_len) // 2:(after_ddc_len - seq_len) // 2 + l_ra]
        self.plot(abs(data_combine[0]), title='降采后时域功率谱', ylable='功率')
        freq_db = 20 * np.log10(abs(freq_data))
        self.plot(freq_db[0], title='降采后频域功率谱', ylable='功率/dBm')
        return freq_vail

    def decoder(self, freq_vail, sched_config_set):
        preamble_id_set = []
        for sched_config in sched_config_set:
            preamble_id_set.append(sched_config.preamble_idx)

        u_cv_table = sched_config.u_cv_table
        ncs = sched_config.ncs
        thread_point_num = self.power_thresh_point
        antnum = freq_vail.shape[0]  ###
        fftsize = self.decoder_fftsize
        detect_thread = self.dectect_thresh
        detect_flag = []
        preamble_idx = 0
        for u, cv_table in u_cv_table.items():
            base_seq = sched_config.generation_sequence(u, 0)
            seq_matrix = np.tile(base_seq[None, :], [antnum, 1])
            h = freq_vail * np.conj(seq_matrix)

            h_time = scf.ifft(h, fftsize, axis=-1) * np.sqrt(fftsize)
            power_spectr = np.mean(abs(h_time) ** 2, axis=0)
            power_spectr_sort = np.sort(power_spectr)
            power_thread = np.mean(power_spectr_sort[-thread_point_num:])
            self.plot(power_spectr, title='时域功率谱')
            for cv in cv_table:
                win_in_idx, win_out_idx, win_before_len = \
                    self.get_window_config(cv, fftsize, sched_config)
                data_in_win = power_spectr[win_in_idx]
                signal_idx = np.where(data_in_win >= power_thread)[0]
                data_out_win = power_spectr[win_out_idx]
                data_out_win[data_out_win >= power_thread] = 0
                noise_power_mean = np.sum(data_out_win) / len(win_out_idx)
                if len(signal_idx) != 0:
                    signal_power_sum = np.sum(data_in_win[np.ix_(signal_idx)])
                    signal_power_mean = signal_power_sum / len(signal_idx)
                    ta_idx = round(np.sum([idx * data_in_win[idx] for idx in signal_idx]) / \
                                   np.sum([data_in_win[idx] for idx in signal_idx]), 2)
                    sinr_linear = np.around(signal_power_mean / noise_power_mean)
                else:
                    # signal_power_sum = np.max(data_in_win)
                    # signal_power_mean = signal_power_sum
                    # ta_idx = np.where(data_in_win == signal_power_sum)[0][0]
                    sinr_linear = 0
                if sinr_linear >= detect_thread:
                    rx_sinr_linear = np.round(signal_power_sum / (noise_power_mean * fftsize)
                                              * self.ddc_ratio, 2)
                    rx_sinr_db = np.round(10 * np.log10(rx_sinr_linear), 2)
                    ta = self.cal_ta(ta_idx, win_before_len, fftsize)

                    print("\033[1;31;40m u:{},  preamble_id:{},  ta:{}Ta,  sinr:{}dB, sinr_linear:{}\033[0m".format(u,
                                                                                                                    preamble_idx,
                                                                                                                    ta,
                                                                                                                    rx_sinr_db,
                                                                                                                    rx_sinr_linear))
                    if preamble_idx in preamble_id_set:
                        detect_flag.append(True)
                    else:
                        detect_flag.append(False)

                elif sinr_linear > 0:
                    print("u:{},  preamble_id:{},  sinr_linear:{}".format(u, preamble_idx, sinr_linear))

                preamble_idx += 1

        if len(preamble_id_set) == len(detect_flag):
            print("======================检测成功======================")
            detect_result = 0
        elif len(preamble_id_set) < len(detect_flag):
            print("======================虚检======================")
            detect_result = 1
        elif len(preamble_id_set) > len(detect_flag):
            print("======================漏检======================")
            detect_result = -1

        return detect_result

    def upsampling(self, d_in, ue_sched):

        upsample_ratio = int(self.gnb_resample / ue_sched.ue_resample)
        coffec = [1]
        d_out = sg.upfirdn(coffec, d_in, up=upsample_ratio, axis=-1)
        d_out = np.concatenate([d_out, np.zeros([d_out.shape[0], upsample_ratio - 1], complex)], axis=-1)
        self.add_property('upsample_ratio', upsample_ratio)
        return d_out, upsample_ratio

    def downsampling(self, data, l_ra):

        if l_ra == 139:
            seq_len = 256
        elif l_ra == 839:
            seq_len = 1536
        coffec = [1]
        ddc_ratio = data.shape[-1] // seq_len
        ddc_data = sg.upfirdn(coffec, data, down=ddc_ratio, axis=-1)
        # ddc_data=data[:,:,1::ddc_ratio]
        self.add_property('ddc_ratio', ddc_ratio)
        return ddc_data, seq_len

    def data_combine(self, d_in):
        antnum, repeat_num = d_in.shape[:2]
        d_combine_repeat = np.mean(d_in, axis=1)
        return d_combine_repeat

    def get_window_config(self, cv, fftsize, sched_config):
        win_before = 1 / 4
        l_ra = sched_config.l_ra
        ncs = sched_config.ncs
        win_len = fftsize * ncs // l_ra
        win_pos = np.mod(fftsize - fftsize * cv // l_ra, fftsize)
        win_before_len = int(win_len * win_before)
        win_fore_len = win_len - win_before_len
        tmp_idx = np.arange(win_pos - win_before_len,
                            win_pos + win_fore_len)
        win_in_idx = np.mod(np.sort(tmp_idx), fftsize)
        win_out_idx = np.asarray(list(set(np.arange(fftsize)) - set(win_in_idx)))
        return win_in_idx, win_out_idx, win_before_len

    def cal_ta(self, ta_idx, win_before_len, fftsize):
        tc_ratio = self.after_ddc_len * self.ddc_ratio / fftsize

        ta = round((ta_idx - win_before_len) * tc_ratio, 2)

        return ta

    def move_frequency(self, data, sched_config):
        """
        :param data: shape ==> [ant,repeatNum,dataLen]
        :param sched_config:
        :return:
        """
        l_ra = sched_config.l_ra
        bwp_rbnum = 273
        k = int(sched_config.pusch_scs / sched_config.prach_scs)
        antnum, repeatnum, d_len = data.shape

        if l_ra == 839:
            seq_len = 840
        elif l_ra == 139:
            seq_len = 144
        else:
            raise
        d_center = sched_config.re_pos + seq_len // 2
        bwp_center = k * bwp_rbnum * 12 // 2
        freq_offset = bwp_center - d_center
        coe_phase = np.exp(2j * np.pi * freq_offset * np.arange(d_len) / d_len)
        d_comp = data * np.tile(coe_phase[None, None, :], [antnum, repeatnum, 1])

        return d_comp, seq_len
