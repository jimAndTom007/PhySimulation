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
from UplinkFlawJson import ReadJson


class GnbTransReceiver(MultiChannel):

    def __init__(self, **kwargs):
        super(GnbTransReceiver, self).__init__(**kwargs)
        self.prachdecoder = PrachDecoder(**kwargs)

    def send(self, sched_config):
        pass

    def receiver(self, frame, ue_sched_list):
        frame = self.add_noise(frame)
        freq_vail = self.prachdecoder.deframe(frame, ue_sched_list[0])
        msg_result = self.prachdecoder.decoder(freq_vail, ue_sched_list[0])
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


def main(sinr, config_path):
    """主进程"""
    with open(config_path, 'r', encoding='utf-8') as fid:
        json_config = json.load(fid)

    head_dict = json_config['BeamHeadParameter']
    config_dict = json_config['TTI_Parameter']
    tti_num = head_dict.get('TTICyclicNum', 1)
    plot_enable = head_dict['PlotEnable']
    json_obj = ReadJson()

    for tti_idx in range(tti_num):
        config_tti = config_dict[0]
        cell_num = config_tti.get('CellNum', 1)
        slot_id = config_tti.get('Slot_id', 1)
        for cell_idx in range(cell_num):
            config = json_obj.config_read(json_config, tti_idx, cell_idx)
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

            if len(msg_result) != 0:
                for msg in msg_result:
                    print(msg)
            else:
                print('未检测到用户！！！')
    plt.show()


if __name__ == '__main__':
    config_path = r'D:\workspace\amazing\simulation\demoJson\Ue1\prach_B4_3km_N5_M4.json'
    main(0,config_path)
