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
from uplink import main
from basicFuc.wtJson import gen_simu_json

if __name__ == '__main__':
    folder_path = os.path.join(os.path.dirname(__file__), r'demoJson')
    config_dict = {
        'ttinum': 1,
        'uenum_set': [1, 2],
        'n_set': [30, 50, 70, 90, 120],
        'm_set': [5, 15, 25, 35]
    }
    folder_set = gen_simu_json(folder_path, **config_dict)

    num_cores = mp.cpu_count()
    pool = mp.Pool(num_cores)

    folder = os.path.join(os.path.dirname(__file__), r'demoJson', 'Ue1')
    file_set = os.listdir(folder)
    sinr_set = [-15, -10, -5, 5]
    tic = timer()
    for folder in folder_set:
        for filename in file_set:
            file_str, file_suff = os.path.splitext(filename)
            if file_suff == '.json':
                filepath = os.path.join(folder, filename)
                pool.apply_async(main, args=(sinr_set, filepath))
    pool.close()
    pool.join()
    toc = timer()
    print("运行时间为：{}s".format(toc - tic))
