#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-11-23 9:48 
'''

import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import os
import re

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def get_files(path_file, path_out=[]):
    ls = os.listdir(path_file)
    for i in ls:
        f_path = os.path.join(path_file, i)
        # 判断是否是一个目录,若是,则递归删除
        if os.path.isdir(f_path):
            path_out = get_files(f_path, path_out)
        else:
            path_out.append(f_path)
    return path_out


def simulation_1():
    folder_path = r'D:\document\仿真报告\prachSimuData\B4_MODE'
    sinr_set = np.arange(-20, 11, 3)
    data_plt = dict()
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if not os.path.isdir(filepath):
            data = sio.loadmat(filepath)['simuResult']
            row, col = data.shape[:]
            resu = np.zeros([row, col])
            resu[data == 0] = 1
            detect_probability = np.sum(resu, axis=-1) / col * 100
            data_plt.update({filename: detect_probability})

    table_bar = {'prach_B4_3km.mat': '3Km_Model1', 'prach_B4_3km_pre.mat': '3Km_Model2',
                 'prach_B4_30km.mat': '30Km_Model1', 'prach_B4_30km_pre.mat': '30Km_Model2'}
    plt.figure()
    for key, vaule in data_plt.items():
        plt.plot(sinr_set, vaule, '-o', label=table_bar[key])

    plt.legend(loc='lower right')
    plt.grid()
    plt.xlabel('Sinr/dB')
    plt.ylabel('Detect Probability/%')
    plt.xticks(sinr_set)
    plt.show()


def simulation_2():
    folder_path = r'D:\document\仿真报告\prachSimuData\ue2'
    # folder_path = r'D:\document\仿真报告\prachSimuData\ue1\Ue1'
    sinr_set = [-20, -15, -10, -5, 0, 5, 10]
    N_set = [10, 20, 30, 40]
    M_set = [5, 10, 15, 20]
    data_plt = dict()
    files = get_files(folder_path)
    for filepath in files:
        temp = os.path.split(filepath)[1]
        filename, filesuff = os.path.splitext(temp)
        if filesuff == '.mat':
            data = sio.loadmat(filepath)['data']
            row, col = data.shape[:]
            resu = np.zeros([row, col])
            resu[data == 0] = 1
            detect_probability = np.sum(resu, axis=-1) / col * 100
            data_plt.update({filename: detect_probability})

    detect_probability = np.zeros([len(M_set), len(N_set), len(sinr_set)])
    for key, value in data_plt.items():
        NM_config = re.findall(r'N([0-9]+)_M([0-9]+)', key)
        N = int(NM_config[0][0])
        M = int(NM_config[0][1])
        N_idx = N_set.index(N)
        M_idx = M_set.index(M)
        detect_probability[M_idx, N_idx, :] = value.copy()

    return detect_probability


if __name__ == '__main__':
    simulation_2()
