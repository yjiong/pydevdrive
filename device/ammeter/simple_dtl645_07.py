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
import time

try:
    import base
except Exception:
    tp = (os.path.split(os.path.realpath(__file__))[0])
    sys.path.append(os.path.dirname(tp))
    import base


@base.DynApp.registerdev(base.DynApp, 'SimpleDTL645_07')
class SimpleDTL645_07(base.DevObj, dlt645_07.DLT6452007_base):
    def __init__(self, element, passwd="", clientcode=""):
        super(SimpleDTL645_07, self).__init__(element[base.DevAddr],
                                              passwd,
                                              clientcode)
        self.addr = element[base.DevAddr]
        self.getCommif(element)
        self.set_serial_config()
        # self.read_di = [(0x0, 0x08, 0xFF, 0x01)]
        # self.read_di = [0x0001ff00]
        # 状态字3
        self.read_di = ['04000503']
        # self.read_di = ['04000407']
        # self.read_di = ['04000102']
        # self.read_di = ['04000703']
        # self.read_di = ['040005ff']
        # ReadFollowData
        # self.read_di = ['500ff01']
        # 剩余电量
        self.read_di = ['900100']
        # self.read_di = ['03320101']
        # 上1次购电后总购电次数
        # self.read_di = ['03320201']
        # safe剩余电量
        # self.read_di = ['78102ff']

    @classmethod
    def set_serial_config(cls):
        cls.baudrate = 2400
        cls.bytesize = 8
        cls.parity = "E"
        cls.stopbits = 1
        cls.timeout = 1

    @property
    def dev_help(self):
        # hs内介绍你的驱动的参数等等
        hs = '''
            读操作参数格式举例:
            写操作参数格式举例:
            参数类型说明:
            '''
        return hs

    def dev_element(self):
        super(SimpleDTL645_07, self).dev_element()
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
        if rw == "r":
            for di in self.read_di:
                while True:
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
                    if len(rece_data) == 0:
                        raise Exception("timeout")
                    self._debug("rece date = %r" % [hex(x) for x in rece_data])
                    resp = self.analysis(rece_data)
                    if resp != dlt645_07.ReadFollowData:
                        break
                value.update(resp)
        else:
            # 读地址
            # send_data = self.get_meter_address_pdu
            # 广播校时, 本指令无应答, timeout
            # send_data = self.broadcast_time_pdu
            # send_data = self.broadcast_time_pdu
            # 设置波特率
            # send_data = self.set_comrate(2400)
            # 跳闸
            # send_data = self.switch_off_pdu
            # 合闸
            send_data = self.switch_on_pdu
            # 合闸允许
            # send_data = self.switch_on_enable_pdu
            # 报警
            # send_data = self.warning_enable_pdu
            # 报警解除
            # send_data = self.warning_disable_pdu
            # 保电
            # send_data = self.keep_power_pdu
            # 保电解除
            # send_data = self.keep_power_release_pdu
            self._debug("send date = %r" % [hex(x) for x in send_data])
            self.serial.write(send_data)
            time.sleep(0.2)
            rece_data = []
            while True:
                va = self.serial.read(1)
                if len(va) == 0:
                    break
                intva = ord(va)
                rece_data.append(intva)
            if len(rece_data) == 0:
                raise Exception("timeout")
            self._debug("rece date = %r" % [hex(x) for x in rece_data])
            resp = self.analysis(rece_data)
            value.update(resp)
        return value


if __name__ == '__main__':
    ele = {
            # base.DevAddr: "171009240037",
            base.DevAddr: "180510200012",
            # base.DevAddr: "9",
            base.Commif: '/dev/ttyUSB0',
            }
    mydev = SimpleDTL645_07(ele, passwd="00000000", clientcode="00000000")
    mydev._logger.setLevel(logging.DEBUG)
    # v = (mydev.rw_dev("w", None))
    # print(json.dumps(v, ensure_ascii=False))
    v = (mydev.rw_dev("r", None))
    print(json.dumps(v, ensure_ascii=False))
