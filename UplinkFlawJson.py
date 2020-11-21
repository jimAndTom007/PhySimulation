#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-11-19 18:51 
'''
import scipy.io as sio
import os


def result_save(d_in, config_path):
    folder = os.path.splitext(config_path)[0]
    filename = os.path.splitext(os.path.basename(config_path))[0]

    if not os.path.exists(folder):
        os.mkdir(folder)
    else:
        del_files(folder)

    file_path = os.path.join(folder, filename + '.mat')
    sio.savemat(file_path, {'data': d_in})


def del_files(path_file):
    ls = os.listdir(path_file)
    for i in ls:
        f_path = os.path.join(path_file, i)
        # 判断是否是一个目录,若是,则递归删除
        if os.path.isdir(f_path):
            del_files(f_path)
        else:
            os.remove(f_path)

class ReadJson():
    def __init__(self):
        pass

    def config_read(self, json_config, tti_idx, cell_idx):
        """读取配置参数"""
        config = {}
        config_temp = json_config['TTI_Parameter'][tti_idx]
        cell_config = config_temp['CellParameter'][cell_idx]
        ue_config_list = config_temp['UeParameter']

        cell_dist = self._get_cell_prach_config(cell_config)
        config['cell_config'] = cell_dist
        uenum = cell_config.get('UeNum', 1)
        ue_dist_list = []
        chan_dist_list = []
        for idx in range(uenum):
            ue_config = ue_config_list[idx]
            ue_dist = self._get_ue_prach_config(cell_config, ue_config)
            ue_dist_list.append(ue_dist)
            chan_dist = self._get_channel_config(cell_config, ue_config)
            chan_dist_list.append(chan_dist)
        config['ue_config'] = ue_dist_list
        config['channel_config'] = chan_dist_list
        return config

    @staticmethod
    def _get_cell_prach_config(cell_config):
        gnb_resample = cell_config.get('GnbSample', 122.88e6)
        prach_decoder_config = cell_config.get('PrachDecoder')
        if prach_decoder_config is not None:
            power_thresh_point = prach_decoder_config.get('ThresholdPointNum', 10)
            dectect_thresh = prach_decoder_config.get('DectectThreshold', 10)
            decoder_fftsize = prach_decoder_config.get('DecodeFFTSize', 2048)
        else:
            power_thresh_point, dectect_thresh, decoder_fftsize = 10, 10, 2048

        config_dist = {'gnb_resample': gnb_resample, 'power_thresh_point': power_thresh_point,
                       'dectect_thresh': dectect_thresh, 'decoder_fftsize': decoder_fftsize}
        return config_dist

    @staticmethod
    def _get_ue_prach_config(cell_config, ue_config):
        slot_id = cell_config.get('Slot_id', 1)
        power_offset = ue_config.get('power_offset', 0)
        format_config = cell_config.get('PrachFormat', "B4")
        prach_config = cell_config.get('PrachConfig', 1)
        ncs = cell_config.get('Ncs', 1)
        prach_mu = cell_config.get('Prach_mu', 1)
        pusch_mu = cell_config.get('Pusch_mu', 1)
        idx_logic = cell_config.get('U_logicIndex', 1)
        rb_start = cell_config.get('PrachRbStar', 1)

        preamble_idx = ue_config.get('Preamble_id', 0)
        tx_antenna = ue_config.get('UeAntennaNum', 0)
        ue_resample = ue_config.get('UeSample', 30.72e6)
        config_dist = {'slot_id': slot_id, 'power_offset': power_offset, 'format_config': format_config,
                       'prach_config': prach_config, 'ncs': ncs, 'prach_mu': prach_mu,
                       'pusch_mu': pusch_mu, 'idx_logic': idx_logic, 'rb_start': rb_start,
                       'preamble_idx': preamble_idx, 'ue_resample': ue_resample,
                       'antnum': tx_antenna}
        return config_dist

    @staticmethod
    def _get_channel_config(cell_config, ue_config):
        time_offset = ue_config.get('TimeOffset', 0)
        channel_type = ue_config.get('ChannelType', 'by_pass')
        fre_offset = ue_config.get('FrequencyOffset', 0)
        rand_seed = ue_config.get('RandSeed', 100)
        tx_antenna = ue_config.get('UeAntennaNum', 1)
        rx_antenna = cell_config.get('GnbAntennaNum', 1)
        fading_type = ue_config.get('ChannelFade', 'A')
        delay_type = ue_config.get('DelaySpredType', 2)
        ue_speed = ue_config.get('UeSpeed', 2)
        channel_corr = ue_config.get('MIMOChannelSpa', 'low')
        fc = cell_config.get('FS', 3.5e9)
        gnbsample = cell_config.get('GnbSample', 122.88e6)
        uesample = cell_config.get('UeSample', 30.72e6)

        config_dist = {'time_offset': time_offset, 'fre_offset': fre_offset, 'tx_antenna': tx_antenna,
                       'rx_antenna': rx_antenna, 'channel_type': channel_type, 'rand_seed': rand_seed,
                       'fading_type': fading_type, 'delay_type': delay_type, 'ue_speed': ue_speed,
                       'channel_corr': channel_corr, 'fc': fc, 'gnbsample': gnbsample,
                       'uesample': uesample}
        return config_dist
