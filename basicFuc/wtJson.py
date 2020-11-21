#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-11-19 11:49
'''

import json
import os
import numpy as np
from UplinkFlawJson import del_files

json_dict = {
    "BeamHeadParameter": {
        "TTICyclicNum": 200,
        "PlotEnable": False
    },
    "TTI_Parameter": [
        {
            "Slot_id": 1,
            "CellNum": 1,
            "CellParameter": [
                {
                    "PrachFormat": "B4",
                    "Ncs": 6,
                    "Prach_mu": 0,
                    "Pusch_mu": 1,
                    "U_logicIndex": 10,
                    "GnbSample": 122880000,
                    "FS": 3500000000,
                    "UeNum": 1,
                    "PrachConfig": 1,
                    "GnbAntennaNum": 4,
                    "PrachFFTSize": 2048,
                    "PrachRbStar": 2,
                    "PrachDecoder": {
                        "ThresholdPointNum": 10,
                        "DectectThreshold": 10,
                        "DecodeFFTSize": 2048,
                        "DecoderObject": "GnbTransReceiver"
                    }
                }
            ],
            "UeParameter": [
                {
                    "UeIdx": 0,
                    "Preamble_id": 5,
                    "TimeOffset": 0,
                    "FrequencyOffset": 0,
                    "UeAntennaNum": 4,
                    "UeSample": 30720000,
                    "RandSeed": 100,
                    "PowerOffset": 0,
                    "ChannelFade": "B",
                    "DelaySpredType": 2,
                    "UeSpeed": 3,
                    "MIMOChannelPolarieze": 0,
                    "MIMOChannelSpa": "low",
                    "ChannelType": "TDL"
                },
                {
                    "UeIdx": 1,
                    "Preamble_id": 10,
                    "TimeOffset": 0,
                    "FrequencyOffset": 0,
                    "UeAntennaNum": 4,
                    "UeSample": 30720000,
                    "RandSeed": 100,
                    "PowerOffset": 0,
                    "ChannelFade": "B",
                    "DelaySpredType": 2,
                    "UeSpeed": 3,
                    "MIMOChannelPolarieze": 0,
                    "MIMOChannelSpa": "low",
                    "ChannelType": "TDL"
                },
                {
                    "UeIdx": 2,
                    "Preamble_id": 60,
                    "TimeOffset": 0,
                    "FrequencyOffset": 0,
                    "UeAntennaNum": 4,
                    "UeSample": 30720000,
                    "RandSeed": 100,
                    "PowerOffset": 0,
                    "ChannelFade": "B",
                    "DelaySpredType": 2,
                    "UeSpeed": 3,
                    "MIMOChannelPolarieze": 0,
                    "MIMOChannelSpa": "low",
                    "ChannelType": "TDL"
                }
            ]
        }
    ]
}


def write(json_dict, folder_path, name, suff='.json'):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    filepath = os.path.join(folder_path, name + suff)
    json_str = json.dumps(json_dict, indent=4)
    with open(filepath, 'w') as fid:
        fid.write(json_str)

def gen_simu_json():
    folder_path = os.path.join(os.path.abspath('..'), r'demoJson')
    ttinum = 1
    uenum_set = [2]
    N_set = [10, 20, 30, 40]
    M_set = [5, 10, 15, 20]
    json_dict['BeamHeadParameter']['TTICyclicNum'] = ttinum
    for uenum in uenum_set:
        folder_path1 = os.path.join(folder_path, 'Ue{}'.format(uenum))
        if os.path.exists(folder_path1):
            del_files(folder_path1)
        for N in N_set:
            for M in M_set:
                json_dict['TTI_Parameter'][0]['CellParameter'][0]['UeNum'] = uenum
                json_dict['TTI_Parameter'][0]['CellParameter'][0]['PrachDecoder']['ThresholdPointNum'] = N
                json_dict['TTI_Parameter'][0]['CellParameter'][0]['PrachDecoder']['DectectThreshold'] = M
                # for ueidx in range(uenum):
                #     json_dict['TTI_Parameter'][0]['UeParameter'][ueidx]['PrachDecoder']

                write(json_dict, folder_path1, r'prach_B4_3km_N{}_M{}'.format(N, M))


if __name__ == '__main__':
    gen_simu_json()
