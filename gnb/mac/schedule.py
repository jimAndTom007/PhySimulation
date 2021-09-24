#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-11-4 10:14 
'''

import numpy as np
from basicFuc.basic import Moudel
import os


class PrachSchedule(Moudel):

    def __init__(self, **kwargs):
        super(PrachSchedule, self).__init__(**kwargs)
        prach_mu = kwargs.get('prach_mu', 0)
        format_config = kwargs.get('format_config', 'B4')
        coff = 2 ** prach_mu
        schedule_table = {'format0': [839, 1.25, 1, 24576, 3168],  # [l_ra, scs,reper,point,cp]
                          'format1': [839, 1.25, 2, 24576, 21024],
                          'formta2': [839, 1.25, 4, 24576, 4688],
                          'format3': [839, 5, 4, 6144, 3168],
                          'A1': [139, 15 * coff, 2, 2048 // coff, 288 // coff],
                          'A2': [139, 15 * coff, 4, 2048 // coff, 576 // coff],
                          'A3': [139, 15 * coff, 6, 2048 // coff, 864 // coff],
                          'B1': [139, 15 * coff, 2, 2048 // coff, 216 // coff],
                          'B2': [139, 15 * coff, 4, 2048 // coff, 360 // coff],
                          'B3': [139, 15 * coff, 6, 2048 // coff, 504 // coff],
                          'B4': [139, 15 * coff, 12, 2048 // coff, 936 // coff],
                          'C0': [139, 15 * coff, 1, 2048 // coff, 1240 // coff],
                          'C2': [139, 15 * coff, 4, 2048 // coff, 2048 // coff]
                          }
        l_ra, prach_scs, repeat_num, fftsize_ue, cp_num = schedule_table[format_config]
        self.prach_format = format_config
        self.l_ra = l_ra
        self.prach_scs = prach_scs
        pusch_mu = kwargs.get('pusch_mu', 1)
        self.pusch_scs = 15 * 2 ** pusch_mu
        self.repeat_num = repeat_num
        self.fftsize_ue = fftsize_ue
        self.cp_num = cp_num
        self.ncs = kwargs.get('ncs', 6)
        self.restricted_type = kwargs.get('restricted_type', None)
        self.preamble_idx = kwargs.get('preamble_idx', 1)
        self.idx_logic = kwargs.get('idx_logic', 1)
        self.ue_resample = kwargs.get('ue_resample', 30.72e6)
        self.bwp_start = kwargs.get('n_bwp_start',0)
        self.bwp_size = kwargs.get('n_bwp_num',273)
        self.ku_0 = 0 # 中心频点的频偏
        self.n_ra = kwargs.get('n_ra',0) # prach occasion频分索引
        self.sym_start = kwargs.get('prach_pos_time',[0])[-1] # prach occasion时域符号起始位置

    def __repr__(self):
        return 'prach schedule'

    def get_logic_index_table(self):
        "获取逻辑索引i与物理索引u的映射表"
        dir_path = os.path.abspath('.')
        file_path = os.path.join(dir_path, 'lib', 'MappingForL%sTable.dat' % self.l_ra)
        mapping_table = self.read_file(file_path, [self.l_ra - 1])
        return mapping_table

    def get_frequency_offset(self):
        supported_table = {'L839Scs1.25Scs15': [6, 7], 'L839Scs5Scs15': [24, 12],
                           'L839Scs1.25Scs30': [3, 1], 'L839Scs5Scs30': [12, 10],
                           'L839Scs1.25Scs60': [2, 133], 'L839Scs5Scs60': [6, 7],
                           'L139Scs15Scs15': [12, 2], 'L139Scs30Scs15': [24, 2],
                           'L139Scs15Scs30': [6, 2], 'L139Scs30Scs30': [12, 2],
                           'L139Scs15Scs60': [3, 2], 'L139Scs30Scs60': [6, 2],
                           }
        pusch_rbnum, re_offset = \
            supported_table['L{}Scs{}Scs{}'.format(self.l_ra, self.prach_scs, self.pusch_scs)]
        return pusch_rbnum, re_offset

    def _get_zc_parameter(self, idx_logic, u_cv_table_in):
        "获取ZC序列生成参数,"
        if self.l_ra in [139, 839]:
            l_table = self.get_logic_index_table()
        else:
            raise ("lenght of sequence is error!!!")

        u0 = l_table[idx_logic]
        cv_num, cv_range = self._cal_cyclic_shift(u0)
        if cv_num == 0:
            return self._get_zc_parameter(idx_logic + 1, u_cv_table_in)
        u_cv_table_in.update({u0: cv_range})
        seq_num = 0
        for value in u_cv_table_in.values():
            seq_num += value.size
        if seq_num > 64:
            seq_dif = 64 - seq_num
            u_cv_table_in.update({u0: cv_range[:seq_dif]})
            return u_cv_table_in
        if seq_num == 64:
            return u_cv_table_in
        elif seq_num < 64:
            return self._get_zc_parameter(idx_logic + 1, u_cv_table_in)

    def _cal_cyclic_shift(self, u):
        """计算限制集和非限制集的循环移位"""
        if self.restricted_type == None:
            if self.ncs == 0:
                cv_num = 1
                cv_range = np.array([0])
            else:
                cv_num = self.l_ra // self.ncs
                cv_range = np.arange(0, cv_num) * self.ncs
        elif self.l_ra == 839 and self.restricted_type != None:
            dir_path = os.path.abspath('.')
            file_path = os.path.join(dir_path, 'lib', 'prach_restrictedSetQ.dat')
            mapping_table = self.read_file(file_path, [self.l_ra - 1])
            q = mapping_table[u - 1]
            du = q if q < self.l_ra / 2 else self.l_ra - q

            if self.restricted_type == 'typeA' and self.l_ra == 839:
                if self.ncs <= du and du < self.l_ra / 3:
                    n_ra_shift = np.floor(du / self.ncs)
                    d_start = 2 * du + n_ra_shift * self.ncs
                    n_ra_group = np.floor(self.l_ra / d_start)
                    n_ra_shift1 = max(np.floor((self.l_ra - 2 * du - n_ra_group * d_start) / self.ncs), 0)
                elif self.l_ra / 3 <= du and du <= (self.l_ra - self.ncs) / 2:
                    n_ra_shift = np.floor((self.l_ra - 2 * du) / self.ncs)
                    d_start = self.l_ra - 2 * du + n_ra_shift * self.ncs
                    n_ra_group = np.floor(du / d_start)
                    n_ra_shift1 = min(max(np.floor((du - n_ra_group * d_start) / self.ncs), 0), n_ra_shift)
                else:
                    return 0, np.array([])
                w = n_ra_shift * n_ra_group + n_ra_shift1
                v = np.arange(0, w)
                cv_num = w
                cv_range = d_start * np.floor(v / n_ra_shift) + self.ncs * np.mod(v, n_ra_shift)
            elif self.restricted_type == 'typeB' and self.l_ra == 839:
                if self.ncs <= du and du < self.l_ra / 5:
                    n_ra_shift = np.floor(du / self.ncs)
                    d_start = 4 * du + n_ra_shift * self.ncs
                    n_ra_group = np.floor(self.l_ra / d_start)
                    n_ra_shift1 = max(np.floor((self.l_ra - 4 * du - n_ra_group * d_start) / self.ncs), 0)
                    d_start2 = 0
                    n_ra_shift2 = 0
                    d_start3 = 0
                    n_ra_shift3 = 0

                elif self.l_ra / 5 <= du and du <= (self.l_ra - self.ncs) / 4:
                    n_ra_shift = np.floor((self.l_ra - 4 * du) / self.ncs)
                    d_start = self.l_ra - 4 * du + n_ra_shift * self.ncs
                    n_ra_group = np.floor(du / d_start)
                    n_ra_shift1 = min(max(np.floor((du - n_ra_group * d_start) / self.ncs), 0), n_ra_shift)
                    d_start2 = 0
                    n_ra_shift2 = 0
                    d_start3 = 0
                    n_ra_shift3 = 0

                elif (self.l_ra + self.ncs) / 4 <= du and du < 2 * self.l_ra / 7:
                    n_ra_shift = np.floor((4 * du - self.l_ra) / self.ncs)
                    d_start = 4 * du - self.l_ra + n_ra_shift * self.ncs
                    n_ra_group = np.floor(du / d_start)
                    n_ra_shift1 = max(np.floor((self.l_ra - 3 * du - n_ra_group * d_start) / self.ncs), 0)
                    d_start2 = self.l_ra - 3 * du + n_ra_group * d_start + n_ra_shift1 * self.ncs
                    n_ra_shift2 = np.floor(
                        min(du - n_ra_group * d_start, 4 * du - self.l_ra - n_ra_shift1 * self.ncs) / self.ncs)
                    d_start3 = self.l_ra - 2 * du + n_ra_group * d_start + n_ra_shift2 * self.ncs
                    n_ra_shift3 = np.floor(((1 - min(1, n_ra_shift1)) * (du - n_ra_group * d_start) + min(1,
                                                                                                          n_ra_shift1) * (
                                                    4 * du - self.l_ra - n_ra_shift1 * self.ncs)) / self.ncs) - n_ra_shift2

                elif 2 * self.l_ra / 7 <= du and du <= (self.l_ra - self.ncs) / 3:
                    n_ra_shift = np.floor((self.l_ra - 3 * du) / self.ncs)
                    d_start = self.l_ra - 3 * du + n_ra_shift * self.ncs
                    n_ra_group = np.floor(du / d_start)
                    n_ra_shift1 = max(np.floor((4 * du - self.l_ra - n_ra_group * d_start) / self.ncs), 0)
                    d_start2 = du + n_ra_group * d_start + n_ra_shift1 * self.ncs
                    n_ra_shift2 = np.floor(
                        min(du - n_ra_group * d_start, self.l_ra - 3 * du - n_ra_shift1 * self.ncs) / self.ncs)
                    d_start3 = 0
                    n_ra_shift3 = 0
                elif (self.l_ra + self.ncs) / 3 <= du and du < 2 * self.l_ra / 5:
                    n_ra_shift = np.floor((-self.l_ra + 3 * du) / self.ncs)
                    d_start = -self.l_ra + 3 * du + n_ra_shift * self.ncs
                    n_ra_group = np.floor(du / d_start)
                    n_ra_shift1 = max(np.floor((-2 * du + self.l_ra - n_ra_group * d_start) / self.ncs), 0)
                    d_start2 = 0
                    n_ra_shift2 = 0
                    d_start3 = 0
                    n_ra_shift3 = 0
                elif 2 * self.l_ra / 5 <= du and du <= (self.l_ra - self.ncs) / 2:
                    n_ra_shift = np.floor((self.l_ra - 2 * du) / self.ncs)
                    d_start = 2 * self.l_ra - 4 * du + n_ra_shift * self.ncs
                    n_ra_group = np.floor((self.l_ra - du) / d_start)
                    n_ra_shift1 = max(np.floor((3 * du - self.l_ra - n_ra_group * d_start) / self.ncs), 0)
                    d_start2 = 0
                    n_ra_shift2 = 0
                    d_start3 = 0
                    n_ra_shift3 = 0
                else:
                    return 0, np.array([])
                w = n_ra_shift * n_ra_group + n_ra_shift1
                v1 = np.arange(0, w)
                cv_num = w
                cv_range = d_start * np.floor(v1 / n_ra_shift) + self.ncs * np.mod(v1, n_ra_shift)
                if n_ra_shift2 > 0:
                    v2 = np.arange(w, w + n_ra_shift2)
                    cv_range2 = d_start2 + (v2 - w) * self.ncs
                    cv_range = np.concatenate([cv_range, cv_range2])
                    cv_num += n_ra_shift2
                if n_ra_shift3 > 0:
                    v3 = np.arange(w + n_ra_shift2, w + n_ra_shift2 + n_ra_shift3)
                    cv_range3 = d_start3 + (v3 - w - n_ra_shift2) * self.ncs
                    cv_num += n_ra_shift3
                    cv_range = np.concatenate([cv_range, cv_range3])
        else:
            raise ValueError("prach short format con not support restricted set！")
        return cv_num, cv_range

    def _get_u_and_cyclic_shift(self, u_cv_table):
        diff_temp = self.preamble_idx
        cv_search_table = np.array([])
        for u, cv_table in u_cv_table.items():
            cv_search_table = np.concatenate([cv_search_table, cv_table])
            try:
                cv = cv_search_table[diff_temp]
                return u, int(cv)
            except:
                continue

    def get_preamble_sequence(self):
        u_cv_table = self._get_zc_parameter(self.idx_logic, u_cv_table_in={})
        u, cv = self._get_u_and_cyclic_shift(u_cv_table)
        sequcence = self.generation_sequence(u, cv)
        self.add_property('u_cv_table', u_cv_table)
        # seq1 = self.generation_sequence(u,0)
        # h = sequcence * np.conj(seq1)
        # import matplotlib.pyplot as plt
        # import scipy.fftpack as scf
        # plt.figure()
        # plt.plot(abs(scf.ifft(h)))
        # plt.show()
        return sequcence

    def generation_sequence(self, u, cv):
        tmp = np.arange(0, self.l_ra)
        idx = np.mod(tmp+cv , self.l_ra)
        s = np.exp(np.pi * u * idx * (idx + 1) / self.l_ra * (-1j))
        m = 2 * np.pi * np.arange(0, self.l_ra) / self.l_ra * (-1j)
        mn = np.tile(m[:, None], [1, self.l_ra]) * np.tile(np.arange(0, self.l_ra)[None, :], [self.l_ra, 1])
        x = np.sum(np.tile(s[:, None], [1, self.l_ra]) * np.exp(mn), axis=0) / np.sqrt(self.l_ra)
        return x

    @staticmethod
    def generation_sequence_copy(u, cv):
        idx = np.arange(0, 139)
        n = np.pi * u * idx * (idx + 1) / 139 * (-1j)
        s = np.exp(np.roll(n, cv))
        m = 2 * np.pi * idx / 139 * (-1j)
        mn = np.tile(m[:, None], [1, 139]) * np.tile(idx[None, :], [139, 1])
        x = np.sum(np.tile(s[:, None], [1, 139]) * np.exp(mn), axis=0) / np.sqrt(139)
        return x