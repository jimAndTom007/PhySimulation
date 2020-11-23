#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-11-4 10:14 
'''
import numpy as np
import json
from channel.multiChannel import MultiChannel

from gnb.phy.prachrx import PrachDecoder
from ue.phy.prachtx import PrachIncoder
from gnb.mac.schedule import PrachSchedule
import matplotlib.pyplot as plt
from UplinkFlawJson import *
import os
from timeit import default_timer as timer


class GnbTransReceiver(MultiChannel):

    def __init__(self, **kwargs):
        super(GnbTransReceiver, self).__init__(**kwargs)
        self.prachdecoder = PrachDecoder(**kwargs)

    def send(self, sched_config):
        pass

    def receiver(self, frame, ue_sched_list):
        frame = self.add_noise(frame)
        freq_vail = self.prachdecoder.deframe(frame, ue_sched_list[0])
        msg_result = self.prachdecoder.decoder(freq_vail, ue_sched_list)
        return msg_result

    def add_noise(self, d_in):
        row, col = d_in.shape
        noise = np.random.randn(row, col) + np.random.randn(row, col) * 1j
        noise = noise / np.sqrt(2)
        d_out = d_in + noise
        return d_out


class UeTransReceiver(MultiChannel):

    def __init__(self, **kwargs):
        super(UeTransReceiver, self).__init__(**kwargs)
        self.prachindecoder = PrachIncoder(**kwargs)

    def send(self, sinr, ue_sched):
        frame, ue_sched = self.prachindecoder.incoder(sinr, ue_sched)
        frame = self.tunel(frame, ue_sched)
        return frame, ue_sched

    def receiver(self, data, sched_config):
        pass


def main(sinr_set, config_path, fileIndex=0):
    """主进程"""
    with open(config_path, 'r', encoding='utf-8') as fid:
        json_config = json.load(fid)

    filename = os.path.splitext(os.path.basename(config_path))[0]
    head_dict = json_config['BeamHeadParameter']
    config_dict = json_config['TTI_Parameter']
    tti_num = head_dict.get('TTICyclicNum', 1)
    plot_enable = head_dict['PlotEnable']
    json_obj = ReadJson()
    simu_result = np.zeros([len(sinr_set), tti_num])
    for sinr_idx, sinr in enumerate(sinr_set):
        for tti_idx in range(tti_num):
            print("开始检测: {} fileIndex:{} ==> sinr:{},  ttiIndex:{}".format(filename, fileIndex, sinr, tti_idx))
            config_tti = config_dict[0]
            cell_num = config_tti.get('CellNum', 1)
            slot_id = config_tti.get('Slot_id', 1)
            for cell_idx in range(cell_num):
                ttiIndex = 0
                config = json_obj.config_read(json_config, ttiIndex, cell_idx)
                gnb_tranmreceiver = GnbTransReceiver(**dict(config['cell_config'], plot_enable=plot_enable))
                uenum = config_tti['CellParameter'][cell_idx].get('UeNum', 1)
                ue_sched_list = []
                for ue_idx in range(uenum):
                    ue_config_id = config['ue_config'][ue_idx]
                    chan_config_id = config['channel_config'][ue_idx]
                    ue_sched = PrachSchedule(**dict(ue_config_id, plot_enable=plot_enable))
                    ue_trans_config_id = dict(**ue_config_id, **chan_config_id, plot_enable=plot_enable)
                    ue_tranmreceiver = UeTransReceiver(**ue_trans_config_id)
                    frame_id, ue_sched = ue_tranmreceiver.send(sinr, ue_sched)
                    if ue_idx == 0:
                        frame = np.zeros(frame_id.shape, complex)
                    frame += frame_id
                    ue_sched_list.append(ue_sched)
                msg_result = gnb_tranmreceiver.receiver(frame, ue_sched_list)
                simu_result[sinr_idx, tti_idx] = msg_result

    result_save(simu_result, config_path)
    if plot_enable:
        plt.show()


if __name__ == '__main__':
    tic = timer()
    folder = os.path.join(os.path.dirname(__file__), r'demoJson', 'Ue1')
    # json_path = os.path.join(folder, 'demoJson', 'prach_test.json')
    file_set = os.listdir(folder)
    sinr_set = [-15, -10, -5, 5]
    path_set = []
    for filename in file_set:
        if os.path.splitext(filename)[1] == '.json':
            json_path = os.path.join(folder, filename)
            path_set.append(json_path)

    for json_path, idx in path_set:
        main(sinr_set, json_path, idx)
    toc = timer()
    print("运行时间为：{}s".format(toc - tic))
