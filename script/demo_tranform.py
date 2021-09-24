#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2021-5-24 16:37 
'''
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack as scf


def generation_sequence_copy(u, cv):
    idx = np.arange(0, 3276)
    n = np.pi * u * idx * (idx + 1) / 3276 * (-1j)
    s = np.exp(np.roll(n, cv))
    m = 2 * np.pi * idx / 3276 * (-1j)
    mn = np.tile(m[:, None], [1, 3276]) * np.tile(idx[None, :], [3276, 1])
    x = np.sum(np.tile(s[:, None], [1, 3276]) * np.exp(mn), axis=0) / np.sqrt(3276)
    return x

if __name__ == '__main__':

    seq=generation_sequence_copy(1,100)
    d_fre=np.zeros(4096,complex)
    d_fre[410:(410+3276)]=seq
    d_time = scf.ifft(d_fre)
    d_fre_trans = scf.fft(d_time)
    seq_trans = d_fre_trans[410:(410+3276)]


    diff = seq-seq_trans