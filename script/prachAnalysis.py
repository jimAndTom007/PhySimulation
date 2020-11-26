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
import pandas as pd
from openpyxl import load_workbook
import datetime

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def get_files(path_file, path_out=[], suff='.mat'):
    ls = os.listdir(path_file)
    for i in ls:
        f_path = os.path.join(path_file, i)
        # 判断是否是一个目录,若是,则递归获取
        if os.path.isdir(f_path):
            path_out = get_files(f_path, path_out)
        else:
            if os.path.splitext(f_path)[1] == suff:
                path_out.append(f_path)
    return path_out


def gen_config(file_set, pattern=r'N([0-9]+)_M([0-9]+)TxSinr([0-9-]+)'):
    ls_out = []
    for file in file_set:
        line = os.path.split(file)[1]
        ls_out.append([int(ii) for ii in re.findall(pattern, line)[0]])
    d_out = np.asarray(ls_out)
    d_ls = []
    for col_idx in range(d_out.shape[1]):
        d_ls.append(np.unique(d_out[:, col_idx]).tolist())
    return d_ls


def write_excel(folder_path, M_set, N_set, sinr_set, detect_probability):
    curr_time = datetime.datetime.now()
    time_str = curr_time.strftime('%H_%M_%S')
    excel_path = os.path.join(folder_path, r'ResultStatistics' + time_str + '.xlsx')
    excelwriter = pd.ExcelWriter(excel_path, engine='openpyxl')  # 创建ExcelWriter对象

    for sinr_idx, sinr in enumerate(sinr_set):
        dict_wt = {'': ['m={}'.format(m) for m in M_set]}
        for n_idex, n in enumerate(N_set):
            dict_wt.update({'n={}'.format(n): list(detect_probability[:, n_idex, sinr_idx])})

        sheet_name = 'Txsinr={}'.format(sinr)
        dataframe = pd.DataFrame(dict_wt)
        excelAddSheet(dataframe, excelwriter, sheet_name)


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


def simulation_2(folder_path=None):
    if folder_path is None:
        here = os.path.dirname(__file__)
        folder_path = os.path.join(here, r'demoJson\Ue2')
    # folder_path = r'D:\document\仿真报告\prachSimuDataV02\Ue2'
    # sinr_set = [-30, -25, -15, -10]
    # N_set = [120, 220, 320, 420]
    # M_set = [10, 15]
    data_plt = dict()
    files = get_files(folder_path)
    [N_set, M_set, sinr_set] = gen_config(files, r'N([0-9]+)_M([0-9]+)TxSinr([0-9-]+)')
    for filepath in files:
        temp = os.path.split(filepath)[1]
        filename, _ = os.path.splitext(temp)
        data = sio.loadmat(filepath)['data']
        row, col = data.shape[:]
        resu = np.zeros([row, col])
        resu[data == 0] = 1
        detect_probability = np.sum(resu, axis=-1) / col * 100
        data_plt.update({filename: detect_probability})

    detect_probability = np.zeros([len(M_set), len(N_set), len(sinr_set)])
    for key, value in data_plt.items():
        NM_config = re.findall(r'N([0-9]+)_M([0-9]+)TxSinr([0-9-]+)', key)
        N = int(NM_config[0][0])
        M = int(NM_config[0][1])
        sinr = int(NM_config[0][2])
        N_idx = N_set.index(N)
        M_idx = M_set.index(M)
        sinr_idx = sinr_set.index(sinr)
        detect_probability[M_idx, N_idx, sinr_idx] = value.copy()

    ###存为excel
    if False:
        write_excel(folder_path, M_set, N_set, sinr_set, detect_probability)
    ###画图
    x0 = sinr_set[11]
    y0 = detect_probability[0, 0, 11]
    plt.figure()
    plt.plot(sinr_set, detect_probability[0, 0, :], r'.-')
    plt.annotate(r'%s' % y0, xy=(x0, y0), xytext=(+30, -30), textcoords='offset points', fontsize=16,
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.2'))
    # plt.legend(loc='lower right')
    plt.grid()
    plt.xlabel('Sinr/dB')
    plt.ylabel('Detect Probability/%')
    plt.xticks(sinr_set)
    plt.show()

    # index_label = ['m={}'.format(m) for m in M_set]
    # info_marks.to_excel(os.path.join(folder_path, r'ResultStatistics.xlsx'),
    #                              sheet_name='Txsinr={}'.format(sinr),
    #                              index_label=index_label)

    return detect_probability


def excelAddSheet(dataframe, excelWriter, sheetName):
    if not os.path.exists(excelWriter.path):
        dataframe.to_excel(excelWriter.path, sheet_name=sheetName, index=False)
    else:
        book = load_workbook(excelWriter.path)
        excelWriter.book = book
        dataframe.to_excel(excel_writer=excelWriter, sheet_name=sheetName, index=False)
        excelWriter.close()


if __name__ == '__main__':
    folder_path = r'D:\document\仿真报告\prachSimuDataV03\Ue2_1'
    # sinr_set = [-15, -10, -5, 5]
    # N_set = [30, 50, 70, 90, 120]
    # M_set = [5, 15, 25, 35]
    simulation_2(folder_path)
