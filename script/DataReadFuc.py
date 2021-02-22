#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2021-2-8 16:25 
'''
import os.path as path
import numpy as np
import matplotlib.pyplot as plt
import copy
import scipy.io as sio
import scipy.fftpack as scf
import os
import re


def pss_sequence(n_id2):
    x = [1, 1, 1, 0, 1, 1, 0]
    x_seq = np.zeros([127])
    for n in range(127):
        x_seq[n] = x[n] if n <= 6 else (x_seq[n - 7 + 4] + x_seq[n - 7]) % 2

    sequence = [1 - 2 * x_seq[(m + 43 * n_id2) % 127] for m in range(127)]
    return sequence


def sss_sequence(n_id1, n_id2):
    pass


def reading(path_folder, file):
    filepath = path.join(path_folder, file)
    with open(filepath, 'r') as fid:
        f_str = fid.readlines()
        d_array = np.array([int(st) for st in f_str])
    return d_array


def main():
    path_folder = r'D:\document\5g_nr_data_122M88\Matlab'
    files = [r'5g_nr_subframe_10.mat']
    filepath = path.join(path_folder, files[0])
    mat_tmp = sio.loadmat(filepath)
    timeData = mat_tmp['waveStruct']['waveform'][0, 0]
    cpStartSet = [352 + (4096 + 288) * i for i in range(14)]
    for symidx in [0]:
        for cpStart in cpStartSet:
            symStart = 61440 * symidx + cpStart
            symData = timeData[symStart:symStart + 4096, 0]
            freData = scf.fftshift(scf.fft(symData))
            plt.figure()
            plt.plot(abs(freData))

    plt.show()


if __name__ == '__main__':
    # path_floder = r'D:\document\5g_nr_data_122M88\仪器厂商'
    # files = [r'5g_nr_rs_fdd_i.dat',
    #          r'5g_nr_rs_fdd_q.dat']
    # pointnum=61440*4
    # d_i = reading(path_floder, files[0])
    # d_q = reading(path_floder, files[1])
    # d = d_i + d_q * 1j
    # d_abs=abs(d)
    # d_bool=np.bool_(d.shape)
    # d_plt= copy.copy(d[:pointnum])
    # # plt.figure()
    # # plt.scatter(np.arange(d.size),abs(d))
    # plt.figure()
    # plt.scatter(np.arange(pointnum),abs(d_plt))
    # plt.show()

    #################mat################################
    pss_sequence(0)
