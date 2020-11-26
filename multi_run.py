#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-11-23 14:34 
'''

import multiprocessing as mp
from timeit import default_timer as timer
import os
from uplink import *
from basicFuc.wtJson import gen_simu_json

if __name__ == '__main__':
    sinr_set = np.arange(-30, 1, 2)
    folder_path = os.path.join(os.path.dirname(__file__), r'demoJson')
    config_dict = {
        'ttinum': 500,
        'uenum_set': [2],
        'n_set': [120],
        'm_set': [15]
    }
    folder_set = gen_simu_json(folder_path, **config_dict)

    num_cores = mp.cpu_count()
    pool = mp.Pool(num_cores)

    tic = timer()
    for folder in folder_set:
        file_set = os.listdir(folder)
        for filename in file_set:
            file_str, file_suff = os.path.splitext(filename)
            if file_suff == '.json':
                filepath = os.path.join(folder, filename)
                for sinr in sinr_set:
                    pool.apply_async(run, args=(sinr, filepath))
    pool.close()
    pool.join()
    toc = timer()
    print("运行时间为：{}s".format(toc - tic))
