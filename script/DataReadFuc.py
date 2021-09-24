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
    x = [0, 1, 1, 0, 1, 1, 1]
    x_seq = np.zeros([127])
    for n in range(127):
        x_seq[n] = x[n] if n <= 6 else (x_seq[n - 7 + 4] + x_seq[n - 7]) % 2

    sequence = [1 - 2 * x_seq[(m + 43 * n_id2) % 127] for m in range(127)]
    return sequence


def sss_sequence(n_id1, n_id2):
    """
    :param n_id1: {0,1,...,335}
    :param n_id2: {0,1,2}
    :return:
    """
    x0 = [1, 0, 0, 0, 0, 0, 0]
    x1 = [1, 0, 0, 0, 0, 0, 0]

    x0_seq = np.zeros([127])
    x1_seq = np.zeros([127])
    for n in range(127):
        x0_seq[n] = x0[n] if n <= 6 else (x0_seq[n - 7 + 4] + x0_seq[n - 7]) % 2
        x1_seq[n] = x1[n] if n <= 6 else (x1_seq[n - 7 + 1] + x1_seq[n - 7]) % 2

    m0 = 15 * (n_id1 // 112) + 5 * n_id2
    m1 = n_id1 % 112
    sequence = [(1 - 2 * x0_seq[(n + m0) % 127]) * (1 - 2 * x1_seq[(n + m1) % 127]) for n in range(127)]
    return sequence


def pseudo_random_sequence(c_init):
    nc = 1600
    x1 = np.concatenate([[1], np.zeros([30])])
    tmp_bin = bin(c_init)[2:]
    out_bin = tmp_bin.rjust(31, '0')[::-1]
    x2 = [eval(n) for n in out_bin]

    x1_seq = np.zeros([3200])
    x2_seq = np.zeros([3200])
    for n in range(3200):
        x1_seq[n] = x1[n] if n <= 30 else (x1_seq[n - 31 + 3] + x1_seq[n - 31]) % 2
        x2_seq[n] = x2[n] if n <= 30 else (
                                                  x2_seq[n - 31 + 3] + x2_seq[n - 31 + 2] + x2_seq[n - 31 + 1] + x2_seq[
                                              n - 31]) % 2

    c_sequence = [(x1_seq[n + nc] + x2_seq[n + nc]) % 2 for n in range(1600)]
    return c_sequence


def reading(path_folder, file):
    filepath = path.join(path_folder, file)
    with open(filepath, 'r') as fid:
        f_str = fid.readlines()
        d_array = np.array([int(st) for st in f_str])
    return d_array


def main():

    path_floder = r'C:\Users\zhangjing\Desktop\IQData'
    files = [r'ddrdata_I.txt',
             r'ddrdata_Q.txt']
    d_i = reading(path_floder, files[0])
    d_q = reading(path_floder, files[1])
    d = d_i + d_q * 1j

    d_plt = d[298430:298430+61440*1]


    ###################################################################

    # path_folder = r'D:\document\5g_nr_data_122M88\Matlab'
    # files = [r'5g_nr_subframe_10.mat']
    # filepath = path.join(path_folder, files[0])
    # mat_tmp = sio.loadmat(filepath)
    # timeData = mat_tmp['waveStruct']['waveform'][0, 0]
    slotnum = 1
    timeData = np.reshape(d,[-1,1])
    cpStartSet = [352 + (4096 + 288) * i for i in range(14)]
    freData_slot = np.zeros([slotnum, 14, 4096], complex)
    for slotidx in range(slotnum):
        symStart=slotidx*61440
        plt.figure(slotidx+1)
        for symidx, cpStart in enumerate(cpStartSet):
            symData = timeData[cpStart:cpStart + 4096, 0]
            freData = scf.fftshift(scf.fft(symData)/np.sqrt(4096))
            # freData_slot[slotidx, symidx, :] = freData[(4096 - 3276) // 2:(4096 + 3276) // 2]
            freData_slot[slotidx, symidx, :] = freData.copy()

            """保存图片"""
            plt.subplot(4,4,symidx+1)
            plt.plot(abs(freData_slot[slotidx, symidx, :]))
            plt.title('symb_{}'.format(symidx))
        plt.savefig(path.join(r'C:\Users\zhangjing\Desktop\IQData', '{}_slotIndex.jpg'.format(slotidx)))
    # plt.show()
    sio.savemat(r'C:\Users\zhangjing\Desktop\IQData\freq_data.mat',{'signal':freData_slot})
    raise ValueError
    #########################################################################################################
    ####################################################SSB解调###############################################
    # ssbData = freData_slot[0, 4:8, 1518:1758]
    # pssData = ssbData[0, 56:183]
    # sssData = ssbData[2, 56:183]
    #
    # cell_id = 1
    # n_id1 = cell_id // 3
    # n_id2 = cell_id % 3
    # pss_seq = pss_sequence(n_id2)
    # sss_seq = sss_sequence(n_id1, n_id2)
    #
    # pss_corr = pssData * np.conj(pss_seq)
    # sss_corr = sssData * np.conj(sss_seq)
    # plt.figure()
    # plt.plot(abs(scf.ifft(pss_corr)))
    # plt.title("PSS")
    # plt.figure()
    # plt.plot(abs(scf.ifft(sss_corr)))
    # plt.title("SSS")
    # plt.show()

    # pbchData = np.concatenate([ssbData[1, :], ssbData[2, :48], ssbData[2, 192:], ssbData[3, :]])
    #
    # l_max = 4
    # n_hf = 0
    # idx_ssb = 0
    # lidx_ssb = idx_ssb + 4 * n_hf
    # c_init = 2 ** 11 * (lidx_ssb + 1) * (cell_id // 4 + 1) + 2 ** 6 * (lidx_ssb + 1) + cell_id % 4
    # c_seq = pseudo_random_sequence(c_init)
    # pbch_seq = [1 / np.sqrt(2) * (1 - 2 * c_seq[2 * m]) + 1j / np.sqrt(2) * (1 - 2 * c_seq[2 * m + 1]) for m in
    #             range(144)]
    # pbch_dmrs = pbchData[cell_id % 4::4]
    # pbch_h = pbch_dmrs * np.conj(pbch_seq)
    # pbch_h1 = np.tile(pbch_h[:, None], [1, 3]).flatten()
    # temp = np.reshape(pbchData, [-1, 4])
    # pbch_data = np.delete(temp, cell_id % 4, axis=-1).flatten()
    # eq_data = pbch_data * np.conj(pbch_h1) / (abs(pbch_h1) ** 2)

    ###计算频偏
    # h1 = ssbData[1, cell_id % 4::4] * np.conj(pbch_seq[:60])
    # h3 = ssbData[3, cell_id % 4::4] * np.conj(pbch_seq[-60:])
    # angle_sym2=np.mean(np.angle(h1*np.conj(h3)))
    # fre_offset=angle_sym2*30e3/(4*np.pi)  #Hz


    # plt.figure()
    # plt.plot(eq_data.real, eq_data.imag, 'o')
    # plt.title('constellation point')
    #
    # plt.figure()
    # plt.plot(abs(scf.ifft(pbch_h, 256, -1)))
    # plt.title('PBCH')
    # plt.show()

    ###############################################################################################################
    ##########################################PDSCH解调############################################################
def pf(d):
    return d*d

if __name__ == '__main__':
    # path_floder = r'C:\Users\zhangjing\Desktop\满振国'
    # files = [r'5g_nr_3p3a_fdd_i.dat',
    #          r'5g_nr_3p3a_fdd_q.dat']
    # # pointnum=61440*4
    # d_i = reading(path_floder, files[0])
    # d_q = reading(path_floder, files[1])
    # # d = d_i + d_q * 1j
    # dtime=d_i[:61440] + d_q[:61440] * 1j
    # sio.savemat(r'C:\Users\zhangjing\Desktop\满振国\data1.mat',{"signal":dtime})
    # d_freq=scf.fft()
    # plt.figure()
    # plt.plot(abs(d[:61440]))
    # plt.show()

    #################mat################################
    # main()
    from icecream import ic
    ic(pf(10))
    ic()


    # cell_id = 1
    # n_id1 = cell_id // 3
    # n_id2 = cell_id % 3
    # pss_seq = pss_sequence(n_id2)
    # sss_seq = sss_sequence(n_id1, n_id2)
    # l_max = 4
    # n_hf = 0
    # idx_ssb = 0
    # lidx_ssb = idx_ssb + 4 * n_hf
    # c_init = 2 ** 11 * (lidx_ssb + 1) * (cell_id // 4 + 1) + 2 ** 6 * (lidx_ssb + 1) + cell_id % 4
    # c_seq = pseudo_random_sequence(c_init)
    # pbch_seq = [1 / np.sqrt(2) * (1 - 2 * c_seq[2 * m]) + 1j / np.sqrt(2) * (1 - 2 * c_seq[2 * m + 1]) for m in
    #             range(144)]
    #
    # a=1


