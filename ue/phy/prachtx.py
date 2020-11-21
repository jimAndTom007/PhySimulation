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

    def incoder(self, sinr,ue_sched):
        sequence = ue_sched.get_preamble_sequence()
        resource_grid, re_pos, rb_num = self.frequency_resource_mapping(ue_sched, sequence)
        resource_grid = self.tx_power_update(resource_grid,sinr)
        frame = self.freq_time_trans(resource_grid, ue_sched)

        ue_sched.add_property('re_pos', re_pos)
        ue_sched.add_property('rb_num', rb_num)

        resource_plot = resource_grid.copy()
        resource_plot[resource_plot == 0] = 0.001
        power_db = 20 * np.log10(abs(resource_plot[0]))
        # self.plot(power_db, title='发端信号频域功率谱', ylable='功率/dBm')
        # self.plot(abs(frame[0]), title='发端信号时域功率谱', ylable='功率')
        return frame, ue_sched

    def frequency_resource_mapping(self, ue_sched, sequence):
        rb_num, re_offset_prach = ue_sched.get_frequency_offset()
        k = int(ue_sched.pusch_scs / ue_sched.prach_scs)
        resource_grid = np.zeros([self.antnum, ue_sched.fftsize_ue], complex)
        idx_start = k * self.rb_start * 12 + re_offset_prach
        resource_grid[0, idx_start:idx_start + ue_sched.l_ra] = sequence
        return resource_grid, idx_start, rb_num

    def tx_power_update(self, d_in, sinr):
        d_out = d_in * 10 ** ((self.power_offset + sinr) / 20)
        return d_out

    def freq_time_trans(self, d_in, ue_sched):
        d_in_shift = scf.ifftshift(d_in, axes=1)
        # d_in_shift = d_in
        d_time = scf.ifft(d_in_shift, ue_sched.fftsize_ue, -1) * np.sqrt(ue_sched.fftsize_ue)
        cp_data = d_time[:, -ue_sched.cp_num:]
        d_out = np.concatenate([cp_data, np.tile(d_time, [1, ue_sched.repeat_num])], axis=-1)
        tti_num = np.ceil(1 / ue_sched.ue_resample * d_out.shape[-1] / 5e-4)
        length = int(tti_num * ue_sched.ue_resample * 5e-4)
        frame = np.zeros([d_out.shape[0], length], complex)
        frame[:, :d_out.shape[-1]] = d_out
        return frame
