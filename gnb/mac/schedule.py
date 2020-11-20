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

        self.l_ra = l_ra
        self.prach_scs = prach_scs
        pusch_mu = kwargs.get('pusch_mu', 1)
        self.pusch_scs = 15 * 2 ** pusch_mu
        self.repeat_num = repeat_num
        self.fftsize_ue = fftsize_ue
        self.cp_num = cp_num
        self.ncs = kwargs.get('ncs', 6)
        self.preamble_idx = kwargs.get('preamble_idx', 1)
        self.idx_logic = kwargs.get('idx_logic', 1)
        self.ue_resample = kwargs.get('ue_resample', 30.72e6)

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
        "获取ZC序列生成参数"
        if self.l_ra in [139, 839]:
            l_table = self.get_logic_index_table()
        else:
            raise ("lenght of sequence is error!!!")

        u0 = l_table[idx_logic]
        cv_num = self.l_ra // self.ncs
        cv_range = np.arange(0, cv_num) * self.ncs
        u_cv_table_in.update({u0: cv_range})  # FIXME 暂时只支持无限制集
        seq_num = 0
        for value in u_cv_table_in.values():
            seq_num += value.size
        if seq_num >= 64:
            seq_dif = 64 - seq_num
            u_cv_table_in.update({u0: cv_range[:seq_dif]})
            return u_cv_table_in
        elif seq_num < 64:
            return self._get_zc_parameter(idx_logic + 1, u_cv_table_in)

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
        return sequcence

    def generation_sequence(self, u, cv):
        idx = np.arange(0, self.l_ra)
        n = np.pi * u * idx * (idx + 1) / self.l_ra * (-1j)
        s = np.exp(np.roll(n, cv))
        m = 2 * np.pi * idx / self.l_ra * (-1j)
        mn = np.tile(m[:, None], [1, self.l_ra]) * np.tile(idx[None, :], [self.l_ra, 1])
        x = np.sum(np.tile(s[:, None], [1, self.l_ra]) * np.exp(mn), axis=0) / np.sqrt(self.l_ra)
        return x
