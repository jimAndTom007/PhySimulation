#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-10-28 15:32 
'''

import numpy as np
import matplotlib.pyplot as plt
import os
import re
from functools import reduce
import scipy.fftpack as scf
import scipy.signal as sg
from basicFuc.basic import Moudel


class PrachIncoder(Moudel):

    def __init__(self, **kwargs):
        super(PrachIncoder, self).__init__(**kwargs)
        self.power_offset = kwargs.get('power_offset', 0)
        self.rb_start = kwargs.get('rb_start', 0)
        self.antnum = kwargs.get('antnum', 0)

    def incoder(self, sinr, ue_sched):
        sequence = ue_sched.get_preamble_sequence()
        resource_grid, re_pos, rb_num = self.frequency_resource_mapping(ue_sched, sequence)
        resource_grid = self.tx_power_update(resource_grid, sinr)
        time_data = self.freq_time_trans(resource_grid, ue_sched)
        frame= time_data
        # frame = self.data_frame_format(time_data, ue_sched)

        ue_sched.add_property('re_pos', re_pos)
        ue_sched.add_property('rb_num', rb_num)

        resource_plot = resource_grid.copy()
        resource_plot[resource_plot == 0] = 0.001
        power_db = 20 * np.log10(abs(resource_plot[0]))
        # self.plot(power_db, title='发端信号频域功率谱', ylable='功率/dBm')
        # self.plot(abs(frame[0]), title='发端信号时域功率谱', ylable='功率')
        return frame, ue_sched

    def incoder_copy(self, sinr, ue_sched):
        sequence = ue_sched.get_preamble_sequence()
        fftsize = ue_sched.fftsize_ue * 4
        cpsize = ue_sched.cp_num * 4
        k = ue_sched.pusch_scs // ue_sched.prach_scs
        phase_com = np.exp(1j * 2 * np.pi * ue_sched.ku_0 * ue_sched.prach_scs * k)
        rb_num, re_offset_prach = ue_sched.get_frequency_offset()
        idx_start = k * (self.rb_start + ue_sched.bwp_start + rb_num * ue_sched.n_ra) * 12 + re_offset_prach
        time_temp = scf.ifft(sequence,fftsize,axis=-1)*np.sqrt(fftsize)
        d_time = time_temp * np.exp(1j*2*np.pi*idx_start*np.arange(fftsize)/fftsize)
        d_time = scf.ifftshift(d_time)

        fmt_time_mapping = {'format0': 1,
                            'format1': 3,
                            'format2': 3.5,
                            'format3': 1}

        cp_data = d_time[-ue_sched.cp_num:]
        d_out = np.concatenate([cp_data, np.tile(d_time, [ue_sched.repeat_num])], axis=-1)
        duration = fmt_time_mapping[ue_sched.prach_format]
        np.zeros([duration*122880],complex)

        freq = scf.fft(d_time[::4], fftsize//4) / np.sqrt(fftsize//4)
        plt.figure()
        plt.plot(abs(freq))








    def frequency_resource_mapping(self, ue_sched, sequence):
        ############################
        # seq1=ue_sched.generation_sequence_copy(100,50)
        # sequence[100:100+seq1.size] += seq1
        bwp_rbnum = 273
        rb_num, re_offset_prach = ue_sched.get_frequency_offset()
        k = int(ue_sched.pusch_scs / ue_sched.prach_scs)
        resource_grid = np.zeros([self.antnum, k * bwp_rbnum * 12], complex)
        idx_start = k * self.rb_start * 12 + re_offset_prach
        resource_grid[:, idx_start:idx_start + ue_sched.l_ra] = np.tile(sequence[None, :], [self.antnum, 1])
        return resource_grid, idx_start, rb_num

    def tx_power_update(self, d_in, sinr):
        d_out = d_in * 10 ** ((self.power_offset + sinr) / 20)
        return d_out

    def freq_time_trans(self, d_in, ue_sched):

        # d_in_shift = d_in
        length_time = ue_sched.fftsize_ue * 4
        grid_res = np.zeros([self.antnum, ue_sched.fftsize_ue * 4], complex)
        length_freq = d_in.shape[1]
        grid_res[:,(length_time-length_freq)//2:(length_time+length_freq)//2]=d_in.copy()

        d_time = scf.ifft(scf.fftshift(grid_res,axes=-1), axis=-1) * np.sqrt(length_time)
        cp_data = d_time[:, -ue_sched.cp_num*4:]
        d_out = np.concatenate([cp_data, np.tile(d_time, [1, ue_sched.repeat_num])], axis=-1)
        # tti_num = np.ceil(1 / ue_sched.ue_resample * d_out.shape[-1] / 5e-4)
        # length = int(tti_num * ue_sched.ue_resample * 5e-4)
        # frame = np.zeros([d_out.shape[0], length], complex)
        # frame[:, :d_out.shape[-1]] = d_out
        return d_out

    def data_frame_format(self, d_in, ue_sched):
        """将prach信号填充到同步帧资源内"""
        fmt_time_mapping = {'format0': 1,
                            'format1': 3,
                            'format2': 3.5,
                            'format3': 1}

        if ue_sched.prach_format in fmt_time_mapping.keys():
            duration = fmt_time_mapping[ue_sched.prach_format]
            gnb_sample = 122880
            frame = np.zeros([self.antnum, gnb_sample * duration], complex)
            pusch_point_start = ue_sched.sym_start*(4096+288) + (64 if ue_sched.sym_start >0 else 0)
            k = int(ue_sched.pusch_scs // ue_sched.prach_scs)
            frame[:,pusch_point_start*k:pusch_point_start*k+d_in.shape[-1]] = d_in



