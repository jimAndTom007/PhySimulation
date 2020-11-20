#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-11-4 10:28 
'''
import re
from functools import reduce
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class TimeStamp(object):
    def __init__(self, *kwarg, **kwargs):
        super(TimeStamp, self).__init__()
        self.radio_frame = kwargs.get('radio_frame', 0)
        self.sub_frame = kwargs.get('sub_frame', 0)
        self.slot_idx = kwargs.get('slot_idx', 0)

    def __repr__(self):
        return '{},{},{}'.format(self.radio_frame, self.sub_frame, self.slot_idx)

    def system_slot(self):
        return self.radio_frame * 20 + self.sub_frame * 2 + self.slot_idx



class Moudel(object):

    def __init__(self, **kwargs):
        super(Moudel, self).__init__()
        self.plot_enable = kwargs.get('plot_enable')

    @staticmethod
    def read_file(file_path, shape, fix_len=None):
        partten = re.compile('[0-9.-]+')
        with open(file_path, 'r') as fid:
            lines = fid.readlines()
            str_list = partten.findall(' '.join(lines))

        table_tmp = [int(ss) if '.' not in ss else float(ss) for ss in str_list]
        if fix_len is not None:
            lenght = reduce(lambda x, y: x * y, shape)
        else:
            lenght = len(table_tmp)
        table_output = np.reshape(table_tmp[:lenght], shape)
        return table_output

    def plot(self, data, **kwargs):
        if self.plot_enable is False:
            return 0
        x_data = kwargs.get('x_data')
        title = kwargs.get('title')
        xlable = kwargs.get('xlable')
        ylable = kwargs.get('ylable')
        plt.figure()
        if x_data is not None:
            plt.plot(x_data, data)
        else:
            plt.plot(data)
        plt.title(title)
        plt.xlabel(xlable)
        plt.ylabel(ylable)
        plt.grid()

    def add_property(self, name, value):
        setattr(self, name, value)

    def del_property(self, name):
        delattr(self, name)

    def registered(self):
        pass
