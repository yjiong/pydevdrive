#!/usr/bin/python
# encoding:utf_8
import os
import re
import platform


def mknewdev():
    print(u'请输入你的设备类定义名')
    dname = raw_input() if platform.python_version()[0] == '2' else input() 
    # dname = input()
    text = r'''#!/usr/bin/python
# encoding:utf-8

import sys
import logging
import os
sys.path.append('../')
try:
    import base
except Exception as e:
    print(e.message)
    os._exit(255)


@base.DynApp.registerdev(base.DynApp, 'DeviceName')
class DeviceName(base.DevObj):
    def __init__(self, element):
        self.addr = element[base.DevAddr]
        self.getCommif(element)

# -----------------------------user code-----------------------------------
        # 如果是串口类接口,初始化串口
        self.set_serial_config()
#         定义自己的属性等
#         self.var1 = xxx
#         self.var2 = xxx
#         ......

    @classmethod
    def set_serial_config(cls):
        cls.baudrate = 9600
        cls.bytesize = 8
        cls.parity = 'N'
        cls.stopbits = 1
        cls.timeout = 1

    @property
    def dev_help(self):
        # hs内介绍你的驱动的参数等等,下面是个简单的列子
        hs = fuck
读操作参数格式举例:
    {'xxx': 0,
     'yyy': 'abc'}
     缺省设置为
    {'xxx': 0,
     'yyy': 10}
写操作参数格式举例:
    {'xxx': 0,
     'yyy': 'def',
     'zzz': [8, 9, 10]}
参数类型说明:
    xxx为int,
    yyy为str,
    zzz为int list,
fuck
        return hs

    def dev_element(self):
        super(DeviceName, self).dev_element()
        return self.element

    @classmethod
    def dev_check_key(cls, ele):
        if base.Commif not in ele:
            raise ValueError("必须有commif参数")
        # if ele[base.Commif] not in base.DynApp.syscommif:
            # raise ValueError("网关不存在该rs485设备的commif")
        return True

    def rw_device(self, rw="r", var_value=None):
        value = {}
        if rw == "r":
            try:
                # 缺省参数的时候
                if 'xxx' not in var_value\
                        or 'yyy' not in var_value:
                    var_value = {'xxx': 0,
                                 'yyy': 10}
                md = "这里是你的驱动读处理"
                value.update({'xxx_value': md})
                self._debug(r'the device value is %r' % value)
            except Exception as e:
                self._debug(e)
                value.update({'error': e})
        else:
            try:
                md = "这里是你的驱动写处理"
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
            base.Commif: '/dev/ttyUSB0'
            }
    mydev = DeviceName(ele)
    mydev._logger.setLevel(logging.DEBUG)
    # 定义读的参数
    rd = {'xxx': 0,
          'yyy': 'abc'}
    print(mydev.rw_dev("r", rd))
    # 定义要写的参数
    wd = {'xxx': 0,
          'yyy': 'def',
          'zzz': [2, 3, 4]
          }
    print(mydev.rw_device("w", wd))
'''
    cc = re.sub(r'DeviceName', dname, text)
    cc = re.sub(r'fuck', r"'''", cc)
    dirstr = os.path.join(os.path.dirname(os.path.abspath(__file__)), dname)
    with open(dirstr + r'.py', 'w') as f:
        f.write(cc)
    print(u"已生成驱动模板:%s" % dirstr)


if __name__ == "__main__":
    mknewdev()
