#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2021-3-31 16:40 
'''
from basicFuc.basic import *
import xlrd3 as xlrd
import os
from uplink import UeTransReceiver, GnbTransReceiver
from gnb.mac.schedule import PrachSchedule


class Schedule():
    def __init__(self, **kwargs):
        self.n_bwp_start = kwargs.get('bwpStart', 0)
        self.n_bwp_num = kwargs.get('bwpSize', 273)
        self.power_offset = kwargs.get('power_offset', 0)
        self.antnum = kwargs.get('antennaNum', 4)


class RrcSignalingAnalyze(Schedule):
    def __init__(self, **kwargs):
        super(RrcSignalingAnalyze, self).__init__(**kwargs)

        """high_layer_config"""
        # ssb实际发送数量
        self.ssbNum = kwargs.get('SSBNum', 8)

        # 终端收到的ssb索引
        self.ssbIdx = kwargs.get('SSBIndex', 1)

        # TDD FR1 prach配置表格索引
        prachConfigIdx = kwargs.get('prachConfigurationIndex', 10)
        assert prachConfigIdx in range(263), 'prachConfigurationIndex error!'
        self.prach_configuration(prachConfigIdx)

        # ssb与prach occasion映射比例
        idx = kwargs.get('SSBPerRachOccasion', 2)
        self.ssbPerRO = [1 / 8, 1 / 4, 1 / 2, 1, 2, 4, 8, 16][idx]

        # ssb对应的preambleId数量
        self.CBPreamblesPerssb = kwargs.get('CBPreamblesPerSSB', 56)
        avali_tab = [[4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64],
                     [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64],
                     [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64],
                     [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64],
                     [4, 8, 12, 16, 20, 24, 28, 32],
                     [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                     [1, 2, 3, 4, 5, 6, 7, 8],
                     [1, 2, 3, 4]]
        assert self.CBPreamblesPerssb in avali_tab[idx], "CBPreamblesPerSSB error!"

        # prach频分数量
        self.fdm = kwargs.get('msg1FDM', 4)

        # prach在bwp内的频域起始位置
        self.rb_start = kwargs.get('msg1FrequencyStart', 0)
        self.bwp_start_grid = kwargs.get('bwpFrequencyStart', 0)

        # 限制集
        self.restricted_type = kwargs.get('restrictedSetConfig', None)
        assert self.restricted_type in [None, 'typeA', 'typeB'], "restrictedSetConfig error!"

        # prach 逻辑根序列索引
        self.idx_logic = kwargs.get('prachRootSequenceIndex', 0)

        # prach子载波间隔
        if self.format_config in ['format0', 'format1', 'format2']:
            self.prach_scs = 1.25
            self.prach_lar = 839
        elif self.format_config == "format3":
            self.prach_scs = 5
            self.prach_lar = 839
        else:
            self.prach_scs = kwargs.get('msg1SubcarrierSpace', 15)
            self.prach_mu = int(np.log2(self.prach_scs / 15))
            self.prach_lar = 139

        # pusch子载波间隔
        self.pusch_scs = kwargs.get('puschSubcarrierSpace', 30)
        self.pusch_mu = int(np.log2(self.pusch_scs / 15))

        # zerosCorrelationZoneConfig配置，用于确定Ncs
        self.zero_corr = kwargs.get('zeroCorrelationZoneConfig', 0)
        assert self.zero_corr in range(16), "zeroCorrelationZoneConfig error!"
        self.ncs = self.prach_ncs()

        # prach前导ID
        self.preamble_idx = kwargs.get('preambleIndex', 0)

        # 高速标识，暂时不用
        self.speed_flag = kwargs.get('highSpeedFlag', 0)

        # UE发送prach的位置
        resu_dict = self.prach_occasion_pos()
        self.association_period_frame = resu_dict['time_period_frameNum']  # number of frame
        self.prach_pos_time = [resu_dict['frame'], resu_dict['subframe'], resu_dict['slot'], resu_dict['symb']]
        self.n_ra = resu_dict['freq_fdm_idx']

    def prach_configuration(self, config_idx):
        """prach configuration index"""
        filename = os.path.join(os.path.abspath('.'), 'lib', 'PrachTimeAndFrequencyConfigTable.xlsx')
        wb = xlrd.open_workbook(filename=filename)
        sh1 = wb.sheet_by_index(0)
        conftemp = sh1.row_values(config_idx + 3)
        self.format_config = 'format' + (str(int(conftemp[1])) if isinstance(conftemp[1], float) else conftemp[1])
        self.prach_period_frame = int(conftemp[2])
        self.prach_period_offsetframe = int(conftemp[3])
        self.prach_start_subframe = [int(conftemp[4])] if isinstance(conftemp[4], float) else list(eval(conftemp[4]))
        self.prach_start_symb = int(conftemp[5])
        self.prach_slotnum_per_subframe = int(conftemp[6]) if isinstance(conftemp[6], float) else 1
        self.prach_ROnum_per_slot = int(conftemp[7]) if isinstance(conftemp[7], float) else 1
        self.prach_duration = int(conftemp[8])

    def prach_occasion_pos(self):
        ro_time_num = len(self.prach_start_subframe) * self.prach_slotnum_per_subframe * self.prach_ROnum_per_slot
        ro_freq_num = self.fdm
        ronum_for_ssb = self.ssbNum / self.ssbPerRO

        table1 = [[1, 2, 4, 8, 16],
                  [1, 2, 4, 8],
                  [1, 2, 4],
                  [1, 2],
                  [1]]
        idx = [1, 2, 4, 8, 16].index(self.prach_period_frame)
        association_period_tab = table1[idx]

        association_period = None
        for value in association_period_tab:
            rate = ro_freq_num * ro_time_num * value / ronum_for_ssb
            if rate >= 1:
                association_period = value
                break

        if self.ssbPerRO >= 1:
            ro_idx = self.ssbIdx // self.ssbPerRO
            remain = self.ssbIdx % self.ssbPerRO
            preamble_start = remain * 64 // self.ssbPerRO
            assert self.preamble_idx in range(preamble_start,
                                              preamble_start + self.CBPreamblesPerssb), "preambleIndex error!"
        else:
            # FIXME 1对多时，随机选择一个occasion
            occnum_per_ssb = int(1 / self.ssbPerRO)
            ro_idx = self.ssbIdx * occnum_per_ssb + np.random.randint(0, occnum_per_ssb)
            assert self.preamble_idx in range(0, self.CBPreamblesPerssb), "preambleIndex error！"

        period_frame = self.prach_period_frame * association_period
        frame_idx = ro_idx // (ro_time_num * ro_freq_num)
        frameId = self.prach_period_offsetframe + frame_idx * self.prach_period_frame
        frame_remain = ro_idx % (ro_time_num * ro_freq_num)
        subframe_idx = frame_remain // (self.prach_slotnum_per_subframe * self.prach_ROnum_per_slot * self.fdm)
        subframeId = self.prach_start_subframe[subframe_idx]
        subframe_remain = frame_remain % (self.prach_slotnum_per_subframe * self.prach_ROnum_per_slot * self.fdm)
        slotId = subframe_remain // (self.prach_ROnum_per_slot * self.fdm)
        slot_remain = subframe_remain % (self.prach_ROnum_per_slot * self.fdm)
        symb_idx = slot_remain // self.fdm
        symbId = self.prach_start_symb + symb_idx * self.prach_duration
        freq_idx = slot_remain % self.fdm
        # rbnum, re_offset = self.prach_occasion_rbnum_offset()
        # freq_start_of_renum = (self.bwp_start_grid + self.n_ra_start + freq_idx * rbnum) * 12 + re_offset

        result = {'time_period_frameNum': period_frame, 'frame': frameId, 'subframe': subframeId, 'slot': slotId,
                  'symb': symbId, 'freq_fdm_idx': freq_idx}
        return result

    def prach_occasion_rbnum_offset(self):
        filename = os.path.join(os.path.abspath('.'), 'lib', 'SupportedCombinationsOfPrachAndPusch.dat')
        with open(filename, 'r') as fid:
            tab_s = fid.readlines()

        pattern_s = r'{}\t{}\t{}\t'.format(self.prach_lar, self.prach_scs, self.pusch_scs)
        prach_rb_num, prach_re_offset = None, None
        for col in tab_s:
            if re.match(pattern_s, col):
                result_t = re.findall(pattern_s + "(\d+)\\t(\d)\\n", col)
                prach_rb_num = int(result_t[0][0])
                prach_re_offset = int(result_t[0][1])
        return prach_rb_num, prach_re_offset

    def prach_ncs(self):
        filename = os.path.join(os.path.abspath('.'), 'lib', 'PrachNcsConfiguration.xlsx')
        wb = xlrd.open_workbook(filename=filename)
        if self.prach_scs == 1.25:
            sh = wb.sheet_by_index(0)
            col_idx = [None, 'typeA', 'typeB'].index(self.restricted_type)
            ncs = int(sh.row_values(self.zero_corr + 2)[1 + col_idx])
        elif self.prach_scs == 5:
            sh = wb.sheet_by_index(1)
            col_idx = [None, 'typeA', 'typeB'].index(self.restricted_type)
            ncs = int(sh.row_values(self.zero_corr + 2)[1 + col_idx])
        else:
            sh = wb.sheet_by_index(2)
            ncs = int(sh.row_values(self.zero_corr + 2)[1])
        return ncs


def run(tx_sinr, conf, duration, plot_enable=False):
    time_stamp = TimeStamp()
    prach_sched = RrcSignalingAnalyze()
    prach_occasion_pos_time = prach_sched.prach_pos_time
    ue_sched = PrachSchedule(**dict(prach_sched.__dict__, plot_enable=plot_enable))
    ue_tranmreceiver = UeTransReceiver(**prach_sched.__dict__)
    while time_stamp.system_slot() <= duration:
        time_list = time_stamp.show_list()
        time_list[0] = time_list[0] % prach_sched.association_period_frame
        if time_list == prach_occasion_pos_time[:3]:
            ue_tranmreceiver.send(tx_sinr, ue_sched)

        print(time_stamp)
        next(time_stamp)


if __name__ == '__main__':
    run(0, 0, 100)
    # schedule = PrachSchedule()
    # schedule.prach_occasion_rbnum_offset()
