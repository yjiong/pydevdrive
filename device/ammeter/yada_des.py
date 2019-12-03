#!/usr/bin/python
# coding=utf8
"""
# Author: yjiong
# Created Time : 2019-11-25 13:16:10
# Mail: 4418229@qq.com
# File Name: yada_des.py
# Description:

"""
import sys
import ctypes
import platform
sys.path.append('./')
LL = ctypes.cdll.LoadLibrary


def yada_des(ibs, kbs, ende="en"):
    c_ubyte_array = ctypes.c_ubyte * 8
    ib = c_ubyte_array()
    kb = c_ubyte_array()
    ob = c_ubyte_array()
    for i in range(0, len(ibs)):
        ib[i] = ctypes.c_ubyte(ibs[i])
        kb[i] = ctypes.c_ubyte(kbs[i])
    bib = ctypes.byref(ib)
    bkb = ctypes.byref(kb)
    bob = ctypes.byref(ob)
    try:
        if platform.system() == 'Windows':
            lib = LL(".\des.dll")
        else:
            if platform.uname()[4] == "x86_64":
                lib = LL("./des.so")
            else:
                if platform.uname()[4] == "aarch64":
                    lib = LL("./arm64des.so")
                else:
                    lib = LL("./armdes.so")
        if ende == "en":
            lib.f_des_encrypt(bib, bkb, bob)
        else:
            lib.f_des_decrypt(bib, bkb, bob)
    except Exception as e:
        print(str(e))
    return [x for x in ob]


if __name__ == '__main__':
    inb = [1, 1, 1, 1, 1, 1, 1, 1]
    ink = [1, 1, 1, 1, 1, 1, 1, 1]
    # 加密
    print(yada_des(inb, ink))
    # 结果为:[153, 77, 77, 193, 87, 185, 108, 82]
    inb = [153, 77, 77, 193, 87, 185, 108, 82]
    ink = [1, 1, 1, 1, 1, 1, 1, 1]
    # 解密
    print(yada_des(inb, ink, "de"))
    # 结果为:[1, 1, 1, 1, 1, 1, 1, 1]
