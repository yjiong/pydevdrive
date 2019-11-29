#!/usr/bin/python
# encoding: UTF-8
"""
# Author: yjiong
# Created Time : 2018-12-24 13:20:42
# Mail: 4418229@qq.com
# File Name: SimpleDTL645_07.py
# Description:

"""

import sys
import json
import logging
import os
import dlt645_07
sys.path.append('../')
try:
    import base
except Exception as e:
    print(e.message)
    os._exit(255)


@base.DynApp.registerdev(base.DynApp, 'SimpleDTL645_07')
class SimpleDTL645_07(base.DevObj, dlt645_07.DLT6452007_base):
    def __init__(self, element):
        super(SimpleDTL645_07, self).__init__(address=element[base.DevAddr])
        self.getCommif(element)
        self.set_serial_config()
        # self.read_di = [(0x0, 0x08, 0xFF, 0x01)]
        # self.read_di = [0x00000000]
        self.read_di = ['40005FF']

    @classmethod
    def set_serial_config(cls):
        cls.baudrate = 2400
        cls.bytesize = 8
        cls.parity = "E"
        cls.stopbits = 1
        cls.timeout = 1

    @property
    def dev_help(self):
        # hs内介绍你的驱动的参数等等,下面是个简单的列子
        hs = '''
读操作参数格式举例:
写操作参数格式举例:
参数类型说明:
'''
        return hs

    def dev_element(self):
        super(SimpleDTL645_07, self).dev_element()
        self.element.update({"conn":
                             {base.Commif: self.commif}
                             })
        return self.element

    @classmethod
    def dev_check_key(cls, ele):
        if base.Commif not in ele:
            raise ValueError("必须有commif参数")
        if ele[base.Commif] not in base.DynApp.syscommif:
            raise ValueError("网关不存在该rs485设备的commif")
        return True

    def rw_device(self, rw="r", var_value=None):
        value = {}
        for di in self.read_di:
            send_data = self.create_cmd_pdu(di)
            self._debug("send date = %r" % [hex(x) for x in send_data])
            self.serial.write(send_data)
            rece_data = []
            while True:
                va = self.serial.read(1)
                if len(va) == 0:
                    break
                intva = ord(va)
                rece_data.append(intva)
            self._debug("rece date = %r" % [hex(x) for x in rece_data])
            value.update(self.analysis(rece_data))
        return value


if __name__ == '__main__':
    ele = {
            base.DevAddr: "171009240037",
            base.Commif: '/dev/ttyUSB0'
            }
    mydev = SimpleDTL645_07(ele)
    mydev._logger.setLevel(logging.DEBUG)
    v = (mydev.rw_dev("r", None))
    print(json.dumps(v, encoding='utf8', ensure_ascii=False))
