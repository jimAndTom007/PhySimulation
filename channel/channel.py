#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-11-4 10:18 
'''

import numpy as np
from basicFuc.basic import Moudel


class Channel(Moudel):

    def __init__(self, **kwargs):
        super(Channel, self).__init__(**kwargs)
        self.tx_antenna = kwargs.get('tx_antenna', 4)
        self.rx_antenna = kwargs.get('rx_antenna', 64)
        self.fre_offset = kwargs.get('fre_offset', 0)
        self.time_offset = kwargs.get('time_offset', 0)
        self.channel_type = kwargs.get('channel_type', 'by_pass')
        self.rand_seed = kwargs.get('rand_seed', 1)
        self.gnbsample = kwargs.get('gnbsample', 122.88e6)
        self.uesample = kwargs.get('uesample', 30.72e6)

    def tunel(self, d_in, sched_config):
        fuc = getattr(self, self.channel_type.lower())
        frame = fuc(d_in, sched_config)
        return frame

    def by_pass(self, d_in, sched_config):
        np.random.seed(self.rand_seed)
        # self.channel_matrix = np.random.randn(self.rx_antenna, self.tx_antenna)
        self.channel_matrix = np.ones([self.rx_antenna, self.tx_antenna])
        d_temp = self.channel_matrix @ d_in
        data = self.time_phase_enable(d_temp)
        d_out = self.fre_phase_enbale(data,self.uesample)
        return d_out

    def time_phase_enable(self, d_in):
        k = self.time_offset // 64
        d_out = d_in[:, :-k].copy()
        d_out = np.concatenate([d_in[:, -k:], d_out], axis=-1)
        return d_out

    def fre_phase_enbale(self, d_in,sample):
        k_idx = np.arange(0, d_in.shape[1])
        delta_t = 1 / sample
        init_phase = 0
        freq_shift = np.exp(1j * (2 * np.pi * self.fre_offset * k_idx * delta_t + init_phase))
        d_out = d_in * np.tile(freq_shift[np.newaxis, :], [self.rx_antenna, 1])
        return d_out
