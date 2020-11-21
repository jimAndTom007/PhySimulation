#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-11-19 16:02 
'''
import numpy as np
import os
from channel.channel import Channel
import scipy.io as sio


class MultiChannel(Channel):
    def __init__(self, **kwargs):
        super(MultiChannel, self).__init__(**kwargs)
        self.fading_type = kwargs.get('fading_type', 'a')
        self.delay_type = kwargs.get('delay_type', 1)
        self.ue_speed = kwargs.get('ue_speed', 3)
        self.channel_corr = kwargs.get('channel_corr', 'low')
        self.fc = kwargs.get('fc', 3.5e9)
        self.gnbsample = kwargs.get('gnbsample', 122.88e6)
        self.uesample = kwargs.get('uesample', 30.72e6)

    def tdl(self, tx_signal, config):
        t_start = 0  # FIXME 信道连续性
        signal_len = tx_signal.shape[-1]
        doppler_freqshift = self.ue_speed / 3.6 * self.fc / 3e8
        tx_signal = self.fre_phase_enbale(tx_signal, self.uesample)
        tx_signal = self.time_phase_enable(tx_signal)

        p_norm, p_los, p_delay = self._get_tdl_tap_and_delay_param()
        pathnum = len(p_delay)
        amplitude_norm = np.sqrt(p_norm)
        fadingcoeff_matrix = np.zeros([self.tx_antenna, self.rx_antenna, signal_len], complex)

        delay_sample = np.int_(np.round(p_delay * 1e-9 * self.uesample))
        total_signal = np.zeros([self.rx_antenna, signal_len + np.max(delay_sample)], complex)

        root_matrix = self.root_spa_matrix()
        for n_path in range(pathnum):
            for n_tx in range(self.tx_antenna):
                for n_rx in range(self.rx_antenna):
                    fadingcoeff_matrix[n_tx, n_rx, :] = self.rayleigh_fading(doppler_freqshift, t_start, signal_len)

                    if n_path == 0:
                        fadingcoeff_matrix[n_tx, n_rx, :] += np.sqrt(p_los) / amplitude_norm[n_path] * (
                                (1 + 1j) / np.sqrt(2))

            h = root_matrix @ np.reshape(fadingcoeff_matrix, [self.tx_antenna * self.rx_antenna, -1])
            h_rsp = np.reshape(h, [self.tx_antenna, self.rx_antenna, -1]).swapaxes(0,1) #rx*tx*path
            signal_rx_npath = np.sum(h_rsp * np.tile(tx_signal[None,:,:],[self.rx_antenna,1,1]),axis=1)
            siganl_path_adjust_amp = signal_rx_npath * amplitude_norm[n_path]
            n_dalay = delay_sample[n_path]
            total_signal[:, n_dalay:n_dalay + signal_len] += siganl_path_adjust_amp
        d_out = total_signal[:, :signal_len]
        return d_out

    def _get_tdl_tap_and_delay_param(self):
        folder = os.path.abspath('.')
        filepath = os.path.join(folder, 'channel', 'lib',
                                self.channel_type.lower(),
                                self.fading_type.lower() + '.dat')
        tap_path = self.read_file(filepath, [-1, 2])
        delay_table = [10, 30, 100, 300, 1000]
        delay_spreed = delay_table[self.delay_type - 1]
        n_tap = tap_path.shape[0]
        power_sum = np.sum(10 ** (tap_path[:, 1] / 10))

        if self.fading_type in ['A', 'B', 'C']:
            p_norm = 10 ** (tap_path[:, 1] / 10) / power_sum
            p_los = 0
            p_delay = tap_path[:, 0] * delay_spreed
        else:
            p_norm = 10 ** (tap_path[1:, 1] / 10) / power_sum
            p_los = 10 ** (tap_path[0, 1] / 10) / power_sum
            p_delay = tap_path[1:, 0] * delay_spreed
        return p_norm, p_los, p_delay

    def root_spa_matrix(self):
        table = {'low': [0, 0], 'medium': [0.3, 0.9], 'high': [0.9, 0.9]}
        alfa, beta = table[self.channel_corr]

        if self.rx_antenna == 1:
            r_gnb = 1
        elif self.rx_antenna == 2:
            r_gnb = np.array([[1, alfa], [np.conj(alfa), 1]])
        elif self.rx_antenna == 4:
            r_gnb = np.array([[1, alfa ** (1 / 9), alfa ** (4 / 9), alfa],
                              [np.conj(alfa) ** (1 / 9), 1, alfa ** (1 / 9), alfa ** (4 / 9)],
                              [np.conj(alfa) ** (4 / 9), np.conj(alfa) ** (1 / 9), 1, alfa ** (1 / 9)],
                              [np.conj(alfa), np.conj(alfa) ** (4 / 9), np.conj(alfa) ** (1 / 9), 1]])
        else:
            r_gnb = np.eye(self.rx_antenna)

        if self.tx_antenna == 1:
            t_ue = 1
        elif self.tx_antenna == 2:
            t_ue = np.array([[1, beta], [np.conj(beta), 1]])
        elif self.tx_antenna == 4:
            t_ue = np.array([[1, beta ** (1 / 9), beta ** (4 / 9), beta],
                             [np.conj(beta) ** (1 / 9), 1, beta ** (1 / 9), beta ** (4 / 9)],
                             [np.conj(beta) ** (4 / 9), np.conj(beta) ** (1 / 9), 1, beta ** (1 / 9)],
                             [np.conj(beta), np.conj(beta) ** (4 / 9), np.conj(beta) ** (1 / 9), 1]])
        else:
            t_ue = np.eye(self.tx_antenna)

        r_spat = np.kron(r_gnb, t_ue)
        a_diag = 0
        if self.channel_corr == 'high':
            if self.rx_antenna == 4:
                if self.tx_antenna == 2:
                    a_diag = 0.0001
                elif self.tx_antenna == 4:
                    a_diag = 0.00012

        if self.channel_corr == 'medium':
            if self.rx_antenna == 4 and self.tx_antenna == 4:
                a_diag = 0.00012

        r_spat = (r_spat + a_diag * np.eye(r_spat.shape[0])) / (1 + a_diag)
        root_matrix = np.linalg.cholesky(r_spat)
        return root_matrix

    def rayleigh_fading(self, doppler_freqshift, t_start, signal_len, theta_rand=None):
        """瑞利衰落径"""
        # np.random.seed()  #TODO 随机种子

        n = 8  # ？？？？？？？？？？？？
        if theta_rand is None:
            theta_rand = np.random.randn(n) * 2 * np.pi
        theta = np.tile(theta_rand[:, None], [1, signal_len])
        time_vector = t_start + np.arange(1, signal_len + 1) / self.uesample  # FIXME 按发端采样率计算

        fm = doppler_freqshift
        fk = fm * np.cos(2 * np.pi * np.arange(1, n + 1) / (2 * (2 * n + 1)))
        alpha = np.pi / 4
        beta = np.pi * np.arange(1, n + 1) / n

        cosfk = np.cos(2 * np.pi * fk[:, None] @ time_vector[None, :] + theta)
        cosfm = np.cos(2 * np.pi * fm * time_vector[np.newaxis, :])

        ri = (2 * np.cos(beta[None, :]) @ cosfk + np.sqrt(2) * np.cos(alpha) * cosfm) / np.sqrt(2 * n + 1)
        rq = (2 * np.sin(beta[None, :]) @ cosfk + np.sqrt(2) * np.sin(alpha) * cosfm) / np.sqrt(2 * n + 1)
        fadingcoeff = ri + rq * 1j
        return fadingcoeff
