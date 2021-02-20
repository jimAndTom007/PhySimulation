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
import os
import re


def reading(path_folder, file):
    filepath = path.join(path_folder, file)
    with open(filepath, 'r') as fid:
        f_str = fid.readlines()
        d_array = np.array([int(st) for st in f_str])
    return d_array


def readmat(path_folder, file):
    filepath = path.join(path_folder, file)
    mat_tmp = sio.loadmat(filepath)


if __name__ == '__main__':
    path_floder = r'D:\document\5g_nr_data_122M88\仪器厂商'
    files = [r'5g_nr_rs_fdd_i.dat',
             r'5g_nr_rs_fdd_q.dat']

    d_i = reading(path_floder, files[0])
    d_q = reading(path_floder, files[1])
    d = d_i + d_q * 1j
    d_abs=abs(d)
    d_bool=np.bool_(d.shape)
    d_plt= copy.copy(d[:500000])
    plt.figure()
    plt.scatter(np.arange(d.size),abs(d))
    # plt.figure()
    # plt.scatter(np.arange(500000),abs(d_plt))
    plt.show()

    #################mat################################
    # path_folder = r'D:\document\5g_nr_data_122M88\Matlab'
    # files = [r'5g_nr_subframe_10.mat']
    # readmat(path_folder, files[0])
