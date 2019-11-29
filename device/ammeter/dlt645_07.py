#!/usr/bin/python
# coding=utf8
"""
# Author: yjiong
# Created Time : 2019-11-23 11:36:50
# Mail: 4418229@qq.com
# File Name: DLT645_07.py
# Description:

"""
import sys
import ctypes
import platform
from dlt645di import *  # pass # NOQA
sys.path.append('./')
LL = ctypes.cdll.LoadLibrary
if platform.uname()[4] == "x86_64":
    lib = LL("./des.so")
else:
    lib = LL("./armdes.so")


def h2bcd(hexv):
    if isinstance(hexv, list):
        retval = 0
        for h in hexv:
            if isinstance(h, int):
                retval *= 100
                retval += (h >> 4) * 10 + (h & 0xf)
            else:
                return 0
        return retval
    if isinstance(hexv, int):
        return (hexv >> 4) * 10 + (hexv & 0xf)
    return 0


def chsum(cl):
    chsum = 0
    for chsumi in cl:
        chsum = (chsum + chsumi) % 256
    return chsum


def hexbcd2float(buf, decimalp):
    t = str(h2bcd(buf))
    if decimalp != 0:
        t = float("{}.{}".format((t[:len(t)-decimalp]), t[len(t)-decimalp:]))
    return t


def hex2assci(buf, decimalp):
    t = ""
    for i in range(len(buf), 0, -1):
        t += chr(buf[i-1])
    return t


def hex2date(buf):
    l = len(buf)
    t = ""
    if l == 5:
        t = "%x年%x月%x日%x时%x分" % (buf[0], buf[1], buf[2], buf[3], buf[4])
    if l == 4:
        t = "%x年%x月%x日-星期%x" % (buf[0], buf[1], buf[2], buf[3])
    if l == 3:
        t = "%x时%x分%x秒" % (buf[0], buf[1], buf[2])
    return t


def hex2kwdate(buf, decimalp):
    kw = hexbcd2float(buf[0-3], decimalp)
    return "{}kW {}".format(kw, hex2date(buf[3:]))


def hex2stat(buf, index):
    bh = buf[1]
    bl = buf[0]
    stat = ""
    if index == 1:
        b7 = ''
        b6 = 'C相无功功率方向:反向 ' if bl & 0x40 else 'C相无功功率方向:正向 '
        b5 = 'B相无功功率方向:反向 ' if bl & 0x20 else 'B相无功功率方向:正向 '
        b4 = 'A相无功功率方向:反向 ' if bl & 0x10 else 'A相无功功率方向:正向 '
        b3 = ''
        b2 = 'C相有功功率方向:反向 ' if bl & 0x4 else 'C相有功功率方向:正向 '
        b1 = 'B相有功功率方向:反向 ' if bl & 0x2 else 'B相有功功率方向:正向 '
        b0 = 'A相有功功率方向:反向 ' if bl & 0x1 else 'A相有功功率方向:正向 '
        stat = "{}{}{}{}{}{}{}{}\n".format(b7, b6, b5, b4, b3, b2, b1, b0)
    if index == 2:
        b7 = ''
        b6 = ''
        b5 = '无功功率方向:反向 ' if bl & 0x20 else '无功功率方向:正向 '
        b4 = '有功功率方向:反向 ' if bl & 0x10 else '有功功率方向:正向 '
        b3 = '停电抄表电池欠压 ' if bl & 0x8 else '停电抄表电池正常 '
        b2 = '时钟电池欠压 ' if bl & 0x4 else '时钟电池正常 '
        b1 = '需量积算方式:区间 ' if bl & 0x2 else '需量积算方式:滑差 '
        b0 = ''
        stat = "{}{}{}{}{}{}{}{}\n".format(b7, b6, b5, b4, b3, b2, b1, b0)
    if index == 3:
        b7 = '预跳闸报警状态:有 ' if bh & 0x80 else '预跳闸报警状态:无'
        b6 = '继电器命令状态:断 ' if bh & 0x40 else '继电器命令状态:通 '
        b5 = '当前运行时区:第二套 ' if bh & 0x20 else '当前运行时区:第一套 '
        b4 = '继电器状态:断 ' if bh & 0x10 else '继电器状态:通 '
        b3 = '编程允许许可 ' if bh & 0x8 else '编程允许禁止 '
        b21 = ''
        if bh & 0x2:
            b21 = '供电方式:辅助电源 '
        if bh & 0x4:
            b21 = '供电方式:电池供电 '
        if (bh & 0x6) == 0:
            b21 = '供电方式:主电源 '
        b0 = '当前运行时段:第二套 ' if bh & 0x1 else '当前运行时段:第一套 '
        stat = "{}{}{}{}{}{}{}\n".format(b7, b6, b5, b4, b3, b21, b0)
        b3 = '当前阶梯:第二套 ' if bl & 0x8 else '当前阶梯:第一套 '
        b2 = '当前运行分时费率:第二套 ' if bl & 0x4 else '当前运行分时费率:第一套 '
        b10 = ''
        if bl & 0x2:
            b10 = '电能表类型:电费型预付费 '
        if bl & 0x1:
            b10 = '电能表类型:电量型预付费 '
        if (bl & 0x3) == 0:
            b10 = '电能表类型:非预付费 '
        stat = "{}{}{}\n".format(b3, b2, b10)
    if index == 4:
        b7 = 'A相断相 ' if bh & 0x80 else ''
        b6 = 'A相潮流反向 ' if bh & 0x40 else ''
        b5 = 'A相过载 ' if bh & 0x20 else ''
        b4 = 'A相过流 ' if bh & 0x10 else ''
        b3 = 'A相失流 ' if bh & 0x10 else ''
        b2 = 'A相过压 ' if bh & 0x4 else ''
        b1 = 'A相欠压 ' if bh & 0x2 else ''
        b0 = 'A相失压 ' if bh & 0x1 else ''
        bl0 = 'A相断流 ' if bl & 0x1 else ''
        stat = "{}{}{}{}{}{}{}{}{}\n".format(b7, b6, b5, b4, b3, b2, b1, b0, bl0)
        if stat == '\n':
            stat = 'A相无故障\n'
    if index == 5:
        b7 = 'B相断相 ' if bh & 0x80 else ''
        b6 = 'B相潮流反向 ' if bh & 0x40 else ''
        b5 = 'B相过载 ' if bh & 0x20 else ''
        b4 = 'B相过流 ' if bh & 0x10 else ''
        b3 = 'B相失流 ' if bh & 0x10 else ''
        b2 = 'B相过压 ' if bh & 0x4 else ''
        b1 = 'B相欠压 ' if bh & 0x2 else ''
        b0 = 'B相失压 ' if bh & 0x1 else ''
        bl0 = 'B相断流 ' if bl & 0x1 else ''
        stat = "{}{}{}{}{}{}{}{}{}\n".format(b7, b6, b5, b4, b3, b2, b1, b0, bl0)
        if stat == '\n':
            stat = 'B相无故障\n'
    if index == 6:
        b7 = 'C相断相 ' if bh & 0x80 else ''
        b6 = 'C相潮流反向 ' if bh & 0x40 else ''
        b5 = 'C相过载 ' if bh & 0x20 else ''
        b4 = 'C相过流 ' if bh & 0x10 else ''
        b3 = 'C相失流 ' if bh & 0x10 else ''
        b2 = 'C相过压 ' if bh & 0x4 else ''
        b1 = 'C相欠压 ' if bh & 0x2 else ''
        b0 = 'C相失压 ' if bh & 0x1 else ''
        bl0 = 'C相断流 ' if bl & 0x1 else ''
        stat = "{}{}{}{}{}{}{}{}{}\n".format(b7, b6, b5, b4, b3, b2, b1, b0, bl0)
        if stat == '\n':
            stat = 'C相无故障\n'
    if index == 7:
        b7 = '总功率因素超下限 ' if bh & 0x80 else ''
        b6 = '需量超限 ' if bh & 0x40 else ''
        b5 = '掉电 ' if bh & 0x20 else ''
        b4 = '辅助电源失电 ' if bh & 0x10 else ''
        b3 = '电流不平衡 ' if bh & 0x10 else ''
        b2 = '电压不平衡 ' if bh & 0x4 else ''
        b1 = '电流逆相序 ' if bh & 0x2 else ''
        b0 = '电压逆相序 ' if bh & 0x1 else ''
        bl0 = '电流严重不平衡 ' if bl & 0x1 else ''
        stat = "{}{}{}{}{}{}{}{}{}\n".format(b7, b6, b5, b4, b3, b2, b1, b0, bl0)
        if stat == '\n':
            stat = '合相无故障\n'
    return stat


class diType(object):
    def __init__(self, argdi):
        if isinstance(argdi, str):
            self.diint = int(argdi, base=16)
            self.di = (self.diint >> 24,
                       (self.diint & 0xFFFFFF) >> 16,
                       (self.diint & 0xFFFF) >> 8,
                       self.diint & 0xFF)
        if isinstance(argdi, int):
            self.diint = argdi
            self.di = (argdi >> 24,
                       (argdi & 0xFFFFFF) >> 16,
                       (argdi & 0xFFFF) >> 8,
                       argdi & 0xFF)
        if isinstance(argdi, tuple) or isinstance(argdi, list):
            self.di = tuple(argdi)
            self.diint = (argdi[0] * 0x1000000 + argdi[1] * 0x10000 +
                          argdi[2] * 0x100 + argdi[3])
        if self.diint not in DI: # pass # NOQA
            raise Exception("DI %x not exist" % self.diint)

        self.val_len = DI[self.diint][0][0] # pass # NOQA
        self.val_decimal_places = DI[self.diint][0][1] # pass # NOQA
        self.read_ctrcode = DI[self.diint][1][0] # pass # NOQA
        self.write_ctrcode = DI[self.diint][1][0] # pass # NOQA
        self.unit = DI[self.diint][2] # pass # NOQA
        self.chinese_name = DI[self.diint][3] # pass # NOQA


class DLT6452007_base(object):
    def __init__(self, address="999999999999", passwd="", clientcode=""):
        self.address = address
        self.passwd = passwd
        self.cli_code = clientcode

    def plus33(self, buf):
        rb = []
        for i in range(len(buf)):
            rb.append(0)
        for i in range(len(buf)):
            if buf[i] < 0xCD:
                rb[len(buf) - i - 1] = buf[i] + 0x33
            else:
                rb[len(buf) - i - 1] = buf[i] - 0xCD
        return rb

    def sub33(self, buf):
        rb = []
        for i in range(len(buf)):
            rb.append(0)
        for i in range(len(buf)):
            if buf[i] >= 0x33:
                rb[len(buf) - i - 1] = buf[i] - 0x33
            else:
                rb[len(buf) - i - 1] = buf[i] + 0xCD
        return rb

    def create_cmd_pdu(self, di, value=[]):
        dt = diType(di)
        amm_addr = '%012d' % int(self.address)
        buf = [0xFE]
        buf.append(0xFE)
        buf.append(0x68)
        buf.append(int(amm_addr[10:12]) // 10 * 16 + int(amm_addr[10:12]) % 10)
        buf.append(int(amm_addr[8:10]) // 10 * 16 + int(amm_addr[8:10]) % 10)
        buf.append(int(amm_addr[6:8]) // 10 * 16 + int(amm_addr[6:8]) % 10)
        buf.append(int(amm_addr[4:6]) // 10 * 16 + int(amm_addr[4:6]) % 10)
        buf.append(int(amm_addr[2:4]) // 10 * 16 + int(amm_addr[2:4]) % 10)
        buf.append(int(amm_addr[0:2]) // 10 * 16 + int(amm_addr[0:2]) % 10)
        buf.append(0x68)
        if len(value) > 0:
            buf.append(dt.Write_ctrcode)
        else:
            buf.append(dt.read_ctrcode)
        buf.append(len(dt.di)+len(self.passwd)+len(self.cli_code)+len(value))
        buf = buf + self.plus33(dt.di)
        if len(value) > 0:
            buf.append(value)
        chsum = 0
        for chsumi in buf[2:]:
            chsum = (chsum + chsumi) % 256
        buf.append(chsum)
        buf.append(0x16)
        return buf

    def analysis(self, buf):
        ret = {}
        try:
            index = buf.index(0x68)
            if len(buf) < 12 or \
                    buf[len(buf) - 1] != 0x16 or \
                    chsum(buf[index:(len(buf) - 2)]) != \
                    buf[len(buf) - 2]:
                    # (buf[index + 8] & 0xf0 != 0x90 and buf[index + 8] & 0xf0 != 0xD0): # pass  # NOQA
                raise ValueError("timeout or check code error")
            if buf[index + 8] == 0xC3:
                raise DLT645_07_Expection_serr(self.sub33([buf[index + 11]])[0]) # pass  # NOQA
            if not (buf[index + 8] & 0xf0 == 0x90 or buf[index + 8] & 0xf3 == 0x83): # pass  # NOQA
                raise DLT645_07_Expection_err(self.sub33([buf[index + 10]])[0])
        except DLT645_07_Expection_serr as e:
            ret.update({"安全认证错误信息": e.message})
            return ret
        except DLT645_07_Expection_err as e:
            ret.update({"错误信息": e.message})
            return ret
        except Exception as e:
            ret.update({"error": str(e)})
            return ret
        val_bs = buf[(index+10): len(buf)-2]
        dtype = diType(self.sub33(val_bs[0:4]))
        tval = self.sub33(val_bs[4:])
        self._debug("the value part:%r" % [hex(x) for x in tval])
        if dtype.di[3] != 0xff and dtype.di[2] != 0xff:
            val = hexbcd2float(tval, dtype.val_decimal_places)
            if dtype.unit == "meter-stat":
                val = hex2stat(tval, dtype.di[3])
            if dtype.unit == "ASCII":
                val = hex2assci(tval, dtype.val_decimal_places)
            if dtype.unit == "DATE":
                val = hex2date(tval)
            if dtype.unit == "kW-DATE":
                val = hex2kwdate(tval, dtype.val_decimal_places)
        else:
            l = dtype.val_len
            r = (len(tval)/l)
            rs = ["C", "B", "A", "total"]
            if r == 5:
                rs = ["费率4", "费率3", "费率2", "费率1", "total"]
            if r == 7:
                rs = ["7", "6", "5", "4", "3", "2", "1"]
            for i in range(0, r, 1):
                key = "%s-%s(%s)" % (dtype.chinese_name, rs[i], dtype.unit)
                if dtype.unit == "kW-DATE":
                    val = hex2kwdate(tval[(i*l):(i*l+l)], dtype.val_decimal_places)
                if dtype.unit == "meter-stat":
                    val = hex2stat(tval[(i*l):(i*l+l)], int(rs[i]))
                else:
                    val = hexbcd2float(tval[(i*l):(i*l+l)], dtype.val_decimal_places) # pass  # NOQA
                ret.update({key: val})
            return ret
            # val = hexbcd2float([0x34,0x12,0x56,0x78], dtype.val_decimal_places)
        key = "%s(%s)" % (dtype.chinese_name, dtype.unit)
        ret = {key: val}
        return ret


class DLT645_07_Expection_err(Exception):
    def __init__(self, serr):
        err = "Error byte:{:x}".format(serr)
        self.serr = serr
        super(DLT645_07_Expection_err, self).__init__(err)
        self.message = self.getError()

    def getError(self):
        b6 = '费率数超 ' if self.serr & 0x40 else ""
        b5 = '日时段数超 ' if self.serr & 0x20 else ""
        b4 = '年时区数超 ' if self.serr & 0x10 else ""
        b3 = '通信速率不能更改 ' if self.serr & 0x8 else ""
        b2 = '密码错/未授权 ' if self.serr & 0x4 else ""
        b1 = '无请求数据 ' if self.serr & 0x2 else ""
        b0 = '其他错误 ' if self.serr & 0x1 else ""
        return "ERROR: {}{}{}{}{}{}{}".format(b6, b5, b4, b3, b2, b1, b0)


class DLT645_07_Expection_serr(Exception):
    def __init__(self, serr):
        err = "Error byte:{:x}".format(serr)
        self.serr = serr
        super(DLT645_07_Expection_serr, self).__init__(err)
        self.message = self.getError()

    def getError(self):
        b6 = '购电超囤积 ' if self.serr & 0x40 else ""
        b5 = '充值次数错误 ' if self.serr & 0x20 else ""
        b4 = '客户编号不匹配 ' if self.serr & 0x10 else ""
        b3 = '身份认证失败 ' if self.serr & 0x8 else ""
        b2 = 'ESM验证失败 ' if self.serr & 0x4 else ""
        b1 = '重复充值 ' if self.serr & 0x2 else ""
        b0 = '其他错误 ' if self.serr & 0x1 else ""
        return "ERROR: {}{}{}{}{}{}{}".format(b6, b5, b4, b3, b2, b1, b0)


if __name__ == '__main__':
    pass
