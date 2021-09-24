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
import copy

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def _green(string):
    """
    将字体转变为绿色
    """
    return r'\033[31m{}\033[0m'.format(string)

class TimeStamp(object):
    def __init__(self, *kwarg, **kwargs):
        super(TimeStamp, self).__init__()
        self.radio_frame = kwargs.get('radio_frame', 0)
        self.sub_frame = kwargs.get('sub_frame', 0)
        self.slot_idx = kwargs.get('slot_idx', 0)
        self.system_slot_id = kwargs.get('system_slot_id', 0)
        self.mu = kwargs.get('mu', 1)

    def __repr__(self):
        return 'time_stamp: {},{},{}'.format(self.radio_frame, self.sub_frame, self.slot_idx)

    # def __str__(self):
    #     return _green('time_stamp: {},{},{}'.format(self.radio_frame, self.sub_frame, self.slot_idx))

    def __next__(self):
        self.system_slot_id += 1
        self.radio_frame = self.system_slot_id // (10 * 2 ** self.mu)
        remain_slot = self.system_slot_id % (10 * 2 ** self.mu)
        self.sub_frame = remain_slot // (2 ** self.mu)
        self.slot_idx = remain_slot % (2 ** self.mu)
        return self


    def system_slot(self):
        slot_id = self.radio_frame * 10 * 2 ** self.mu + self.sub_frame * 2 ** self.mu + self.slot_idx
        self.system_slot_id = slot_id
        return slot_id

    def show_list(self):
        return copy.copy([self.radio_frame, self.sub_frame, self.slot_idx])


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

if __name__ == '__main__':
    time_stamp=TimeStamp()
    for i in range(10):

        print(next(time_stamp))
        time_stamp = next(time_stamp)