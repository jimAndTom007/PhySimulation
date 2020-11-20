#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@IDE     ：PyCharm 
@Author  ：Zhang.Jing
@Mail    : jing.zhang2020@kingsignal.com
@Date    ：2020-10-31 10:12 
'''

import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack as scf
from scipy.interpolate import interp1d
import scipy.signal as scs


def fuc(x):
    x_rad = x / 180 * np.pi
    return 1 / np.exp(np.sin(x_rad ** 2)) ** 2


def fuc1():
    point = 200
    x = np.linspace(-180, 180, point)
    y = fuc(x)
    y_shift = scf.fft(y, point)
    plt.figure()
    plt.plot(y)

    plt.figure()
    plt.plot(y_shift)
    # plt.show()
    y1 = scs.decimate(y, 4, n=25, ftype='fir')
    y_inter_shift = scf.fft(y1, point)
    plt.figure()
    plt.plot(y1)
    plt.figure()
    plt.plot(y_inter_shift)

    y2 = scs.resample(y, point // 4)
    y_inter_shift2 = scf.fft(y2, point)
    plt.figure()
    plt.plot(y2)
    plt.figure()
    plt.plot(y_inter_shift, 'r-', y_inter_shift2, 'b--')

    plt.show()


def fuc2():
    frequency = np.random.randn(4096) + np.random.randn(4096) * 1j
    time = scf.ifftshift(scf.ifft(frequency)) * np.sqrt(4096)

    ratio = np.mean(abs(frequency)) / np.mean(abs(time))

    print(ratio)


def fuc3():
    import numpy as np
    from scipy import signal
    import matplotlib.pyplot as plt

    x = np.arange(100)
    num = 25
    y = x
    z = signal.resample(y, num, x, axis=0, window=None)
    yy = z[0]
    xx = z[1]
    plt.plot(x, y)
    plt.plot(xx, yy)
    plt.show()


if __name__ == '__main__':
    # fuc3()
    # n = 1
    # len=12
    # fre = np.exp(2 * np.pi / len * np.arange(0,len) * n*1j)*np.exp(1j*np.pi/4*3)
    # time = scf.ifft(fre) * np.sqrt(len)
    # plt.figure()
    # plt.plot(abs(time))
    # plt.show()
    a=np.arange(10)
    for idx,value in enumerate(a):
        print(idx*value)


