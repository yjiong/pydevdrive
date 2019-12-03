# !/usr/bin/python
#  encoding: UTF-8

import sys
import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp
import logging
import os

try:
    import base
except Exception:
    tp = (os.path.split(os.path.realpath(__file__))[0])
    sys.path.append(os.path.dirname(tp))
    import base


@base.DynApp.registerdev(base.DynApp, 'ModbusTCPExample')
class ModbusTCPExample(base.DevObj):
    def __init__(self, element):
        self.addr = element[base.DevAddr]
        self.getCommif(element)
# -----------------------------user code-----------------------------------
#         定义自己的属性等
#         self.var1 = xxx
#         self.var2 = xxx
#         ......
# -----------------------------user code-----------------------------------


# -----------------------------user code-----------------------------------
    @classmethod
    def dev_help(cls):
        hs = '''
读操作参数格式举例:
    {'StartingAddress': 0,
     'Quantity': 2}
     缺省设置为
    {'StartingAddress': 0,
     'Quantity': 10}
写操作参数格式举例:
    {'StartingAddress': 0,
     'Quantity': 2,
     'value': [8, 9]}
参数类型说明:
    StartingAddress,Quantity为int,value为int列表
'''
        return hs

    def dev_element(self):
        super(ModbusTCPExample, self).dev_element()
        self.element.update({"conn":
                             {base.Commif: self.commif}})
        return self.element

    @classmethod
    def dev_check_key(cls, ele):
        # if ele[base.Commif] not in base.DynApp.syscommif:
        if base.Commif not in ele:
            raise ValueError("必须有commif参数")
        return True

    def rw_device(self, rw="r", var_value=None):
        value = {}
        m = modbus_tcp.TcpMaster(self.commif)
        m.set_timeout(1)
        if rw == "r":
            try:
                # 缺省参数的时候
                if not var_value or\
                        'StartingAddress' not in var_value\
                        or 'Quantity' not in var_value:
                    var_value = {'StartingAddress': 0,
                                 'Quantity': 10}
                md = m.execute(int(self.addr),
                               cst.READ_HOLDING_REGISTERS,
                               var_value['StartingAddress'],
                               var_value['Quantity'])
                value.update({'modbus_value': md})
                self._debug(r'the device value is %r' % value)
            except Exception as e:
                self._debug(e)
                value.update({'error': str(e)})
        else:
            try:
                md = m.execute(int(self.addr),
                               cst.WRITE_MULTIPLE_REGISTERS,
                               var_value['StartingAddress'],
                               var_value['Quantity'],
                               var_value['value'])
                value.update({'write_result': md})
                self._debug(r'write device result is %r' % value)
            except Exception as e:
                self._debug(e)
                value.update({'error': e})
        return value
    # -----------------------------user code-----------------------------------


if __name__ == '__main__':
    ele = {
            base.DevAddr: 1,
            base.Commif: '192.168.1.17'
            }
    mydev = ModbusTCPExample(ele)
    mydev._logger.setLevel(logging.DEBUG)
    # 定义读的参数
    rd = {'StartingAddress': 0,
          'Quantity': 10}
    print(mydev.rw_dev("r", rd))
    # print(mydev.rw_device())
    # 定义要写的参数
    wd = {'StartingAddress': 0,
          'Quantity': 2,
          'value': [8, 9]
          }
    print(mydev.rw_device("w", wd))
