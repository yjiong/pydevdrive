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
import datetime
import yada_des

try:
    import base
except Exception:
    tp = (os.path.split(os.path.realpath(__file__))[0])
    sys.path.append(os.path.dirname(tp))
    import base


@base.DynApp.registerdev(base.DynApp, 'SimpleDTL645_07')
class SimpleDTL645_07(base.DevObj,   dlt645_07.DLT6452007_base):
    def __init__(self, element, passwd="", clientcode=""):
        super(SimpleDTL645_07, self).__init__(element[base.DevAddr],
                                              passwd,
                                              clientcode)
        self.getCommif(element)
        self.set_serial_config()
        # self.read_di = [(0x0, 0x08, 0xFF, 0x01)]
        # self.read_di = [0x0001ff00]
        self.read_di = ['04000E01','04000E02','04000F01','04000F02','04000F03','04000F04','00900100','00900101']
        # self.read_di = ['04000407']
        # self.read_di = ['04000102']
        # self.read_di = ['04000703']
        # self.read_di = ['040005ff']
        # self.read_di = ['0500ff01']
        # self.read_di = ['500ff01']

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
        self.element.update({"conn":
                             {base.Commif: self.commif}
                             })
        return self.element

    @classmethod
    def dev_check_key(cseconds2hexls, ele):
        if base.Commif not in ele:
            raise ValueError("必须有commif参数")
        if ele[base.Commif] not in base.DynApp.syscommif:
            raise ValueError("网关不存在该rs485设备的commif")
        return True

    def seconds2hex(self):
        startTime = '2000-01-01 00:00:00'
        endTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        startTime = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
        endTime =  datetime.datetime.strptime(endTime,'%Y-%m-%d %H:%M:%S')
        total_seconds = (endTime - startTime).total_seconds()
        hexSeconds = "%08x"%(int(total_seconds))
        return hexSeconds
        
    #充值/退费电量
    def  dev_tranbattery_pdu(self, ttype, value):
        #dt = diType(di)
        #用户
        if ttype == 'cz':
            di = '070102FF'
        else:
            di = '070103FF'
        dt = dlt645_07.diType(di)
        pdu = self._get_pdu_head()
        #添加控制码
        pdu.append(dt.write_ctrcode)
        #添加客户号
        cl = "%08x"%(int(self.cli_code))
        cll = self._strd2hlist(cl) 
        #MAC1
        ink = [11, 12, 13, 14, 14, 13, 12, 11]
        #交易金额数据
        td = "%08x"%(int(value*100))
        tdl =  self._strd2hlist(td)
        tdl = list(reversed(tdl))
        #交易日期数据
        ts  = self.seconds2hex()
        tsl = self._strd2hlist(ts)
        tsl = list(reversed(tsl))
        #加密数据
        mc1 = yada_des.yada_des(tdl + tsl, ink) 
        #添加数据长度L=04H（数据标识）+04H（操作者代码）+m(交易+日期+秘钥)
        length = len(dt.di) +  len(cll) + len(mc1)  + len(ink) 
        pdu.append(length)
        #添加数据域 添加
        pdu.extend(self._plus33(list(dt.di)))
        pdu.extend(self._plus33(cll))
        pdu.extend(list(reversed(self._plus33(mc1))))
        pdu.extend(list(reversed(self._plus33(ink))))
        #添加校验码
        pdu.append(dlt645_07.chsum(pdu[pdu.index(0x68):]))
        #添加结束符
        pdu.append(0x16)
        return pdu
    
    #读写数据
    def rw_device(self, rw="r", var_value=None):
        value = {}
        if rw == "r":
            for di in self.read_di:
                while True:
                    send_data = self.create_cmd_pdu(di)
                    print([hex(x) for x in send_data])
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
                    print( [hex(x) for x in rece_data])
                    resp = self.analysis(rece_data)
                    if resp != dlt645_07.ReadFollowData:
                        break
                value.update(resp)
        else:
            #json参数处理
            j_data = json.loads(var_value)
            #强制断闸
            if 'switch_off' in j_data:
                send_data = self.switch_off_pdu
            #强制合闸
            elif 'switch_on' in j_data:
                send_data = self.switch_on_pdu
            #强制保电
            elif 'power_on' in j_data:
                send_data = self.keep_power_pdu
            #取消保电
            elif 'power_off' in j_data:
                send_data = self.keep_power_release_pdu
            #设置报警1限值
            elif 'set_warn_1' in j_data:
                di = '04000F01'
                tvalue = j_data['set_warn_1']
                vle = "%08d"%(int(tvalue * 100))
                vlel = self._strd2hlist(vle)  
                send_data = self.create_cmd_pdu_v2(di, vlel)
            #设置报警2限值
            elif 'set_warn_2' in j_data:
                di = '04000F02'
                tvalue = j_data['set_warn_2']
                vle = "%08d"%(int(tvalue * 100))
                vlel = self._strd2hlist(vle)  
                send_data = self.create_cmd_pdu_v2(di, vlel)
            #设置允许囤积限值
            elif 'set_hoard' in j_data:
                di = '04000F03'
                tvalue = j_data['set_hoard']
                vle = "%08d"%(int(tvalue * 100))
                vlel = self._strd2hlist(vle)  
                send_data = self.create_cmd_pdu_v2(di, vlel)
            #设置允许透支
            elif 'set_overdraft' in j_data:
                di = '04000F04'
                tvalue = j_data['set_overdraft']
                vle = "%08d"%(int(tvalue * 100))
                vlel = self._strd2hlist(vle)  
                send_data = self.create_cmd_pdu_v2(di, vlel)
            #设置正向功率限值
            elif 'set_powerup_limit' in j_data:
                di = '04000E01'
                tvalue = j_data['set_powerup_limit']
                vle = "%06d"%(int(tvalue * 10000))
                vlel = self._strd2hlist(vle)  
                send_data = self.create_cmd_pdu_v2(di, vlel)
            #设置反向功率限值
            elif 'set_powerdown_limit' in j_data:
                di = '04000E02'
                tvalue = j_data['set_powerdown_limit']
                vle = "%06d"%(int(tvalue * 10000))
                vlel = self._strd2hlist(vle)  
                send_data = self.create_cmd_pdu_v2(di, vlel)
            #充值
            elif 'charge' in j_data:
                tvalue = j_data['charge']
                send_data = mydev.dev_tranbattery_pdu('cz', tvalue)
            #充值退费
            elif 'refund' in j_data:
                tvalue = j_data['refund']
                send_data = mydev.dev_tranbattery_pdu('tf', tvalue)
            # 读地址
            # send_data = self.get_meter_address_pdu
            # 广播校时, 本指令无应答, timeout
            # send_data = self.broadcast_time_pdu
            # 设置波特率
            # send_data = self.set_comrate(2400)
            # 跳闸
            #send_data = self.switch_off_pdu
            # 合闸允许
            #send_data = self.switch_on_pdu
            # 报警
            # send_data = self.warning_enable_pdu
            # 报警解除
            # send_data = self.warning_disable_pdu
            # 保电
            #send_data = self.keep_power_pdu
            # 保电解除
            #send_data = self.keep_power_release_pdu

            print("send date = %r" % [hex(x) for x in send_data])
            self.serial.write(send_data)
            time.sleep(0.5)
            rece_data = []
            while True:
                va = self.serial.read(1)
                if len(va) == 0:
                    break
                intva = ord(va)
                rece_data.append(intva)
            if len(rece_data) == 0:
                raise Exception("timeout")
            print("rece date = %r" % [hex(x) for x in rece_data])
            resp = self.analysis(rece_data)
            value.update(resp)
        return value

if __name__ == '__main__':
    ele = {
            # base.DevAddr: "171009240037",
            base.DevAddr: "180510200012",
            base.Commif: '/dev/ttyUSB0',
            }
    mydev = SimpleDTL645_07(ele, passwd="00000002", clientcode="00000002")


    # var_value = '{"power_off":""}'
    # v = (mydev.rw_dev("w", var_value))
    # print(json.dumps(v, ensure_ascii=False))
    
    # var_value = '{"set_powerup_limit":90}'
    # v = (mydev.rw_dev("w", var_value))
    # print(json.dumps(v, ensure_ascii=False))

    # var_value = '{"set_powerdown_limit":80}'
    # v = (mydev.rw_dev("w", var_value))
    # print(json.dumps(v, ensure_ascii=False))
    # mydev.read_di = ['04000E01','04000E02','04000F01','04000F02','04000F03','04000F04','00900100','00900101']
    # v =  mydev.rw_dev("r", None)
    # print(json.dumps(v, ensure_ascii=False))

    # mydev.read_di = ['04000E02']
    # v =  mydev.rw_dev("r", None)
    # print(json.dumps(v, ensure_ascii=False))
    
    # mydev.read_di = ['04000E02']
    # v =  mydev.rw_dev("r", None)
    # print(json.dumps(v, ensure_ascii=False))

    
    #充值
    var_value = '{"charge":10}'
    v = (mydev.rw_dev("w", var_value))
    print(json.dumps(v, ensure_ascii=False))
   #保电解除

    