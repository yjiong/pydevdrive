#!/usr/bin/python
# coding=utf8
"""
# Author: yjiong
# Created Time : 2019-11-23 11:36:50
# Mail: 4418229@qq.com
# File Name: DLT645_07.py
# Description:

"""
import time
from dlt645di import *  # pass # NOQA


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
        self.write_ctrcode = DI[self.diint][1][1] # pass # NOQA
        self.unit = DI[self.diint][2] # pass # NOQA
        self.chinese_name = DI[self.diint][3] # pass # NOQA


class DLT6452007_base(object):
    def __init__(self, address="999999999999", passwd="", clientcode=""):
        self.address = address
        self.passwd = passwd
        self.cli_code = clientcode
        self._rece_buf = []
        self._seq = 0

    def _plus33(self, buf):
        rb = []
        for i in range(len(buf)):
            rb.append(0)
        for i in range(len(buf)):
            if buf[i] < 0xCD:
                rb[len(buf) - i - 1] = buf[i] + 0x33
            else:
                rb[len(buf) - i - 1] = buf[i] - 0xCD
        return rb

    def _sub33(self, buf):
        rb = []
        for i in range(len(buf)):
            rb.append(0)
        for i in range(len(buf)):
            if buf[i] >= 0x33:
                rb[len(buf) - i - 1] = buf[i] - 0x33
            else:
                rb[len(buf) - i - 1] = buf[i] + 0xCD
        return rb

    def _hexbcd2float(self, buf, decimalp):
        t = str(h2bcd(buf))
        if decimalp != 0:
            t = float("{}.{}".format((t[:len(t)-decimalp]), t[len(t)-decimalp:]))
        return t

    def hex2assci(self, buf, decimalp):
        t = ""
        for i in range(len(buf), 0, -1):
            t += chr(buf[i-1])
        return t

    def _hex2date(self, buf):
        lenght = len(buf)
        t = ""
        if lenght == 5:
            t = "%x年%x月%x日%x时%x分" % (buf[0], buf[1], buf[2], buf[3], buf[4])
        if lenght == 4:
            t = "%x年%x月%x日-星期%x" % (buf[0], buf[1], buf[2], buf[3])
        if lenght == 3:
            t = "%x时%x分%x秒" % (buf[0], buf[1], buf[2])
        if lenght == 2:
            t = "%x日%x时" % (buf[0], buf[1])
        return t

    def _hex2rdate(delf, buf):
        lenght = len(buf)
        if lenght == 4:
            t = "%x年%x月%x日%x分" % (buf[0], buf[1], buf[2], buf[3])
        if lenght == 2:
            t = "%x%x分" % (buf[0], buf[1])
        return t

    def _hex2kwdate(self, buf, decimalp):
        kw = self.hexbcd2float(buf[0-3], decimalp)
        return "{}kW {}".format(kw, self._hex2date(buf[3:]))

    def _hex2stat(self, buf, index):
        bh = buf[1]
        bl = buf[0]
        stat = ""
        if index == 1:
            b7 = ''
            b6 = ''
            b5 = '无功功率方向:反向 ' if bl & 0x20 else '无功功率方向:正向 '
            b4 = '有功功率方向:反向 ' if bl & 0x10 else '有功功率方向:正向 '
            b3 = '停电抄表电池欠压 ' if bl & 0x8 else '停电抄表电池正常 '
            b2 = '时钟电池欠压 ' if bl & 0x4 else '时钟电池正常 '
            b1 = '需量积算方式:区间 ' if bl & 0x2 else '需量积算方式:滑差 '
            b0 = ''
            stat = "{}{}{}{}{}{}{}{}\n".format(b7, b6, b5, b4, b3, b2, b1, b0)
        if index == 2:
            b7 = ''
            b6 = 'C相无功功率方向:反向 ' if bl & 0x40 else 'C相无功功率方向:正向 '
            b5 = 'B相无功功率方向:反向 ' if bl & 0x20 else 'B相无功功率方向:正向 '
            b4 = 'A相无功功率方向:反向 ' if bl & 0x10 else 'A相无功功率方向:正向 '
            b3 = ''
            b2 = 'C相有功功率方向:反向 ' if bl & 0x4 else 'C相有功功率方向:正向 '
            b1 = 'B相有功功率方向:反向 ' if bl & 0x2 else 'B相有功功率方向:正向 '
            b0 = 'A相有功功率方向:反向 ' if bl & 0x1 else 'A相有功功率方向:正向 '
            stat = "{}{}{}{}{}{}{}{}\n".format(b7, b6, b5, b4, b3, b2, b1, b0)
        if index == 3:
            b7 = '预跳闸报警状态:有 ' if bh & 0x80 else '预跳闸报警状态:无 '
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
            b7 = '远程开户:已开 ' if bl & 0x80 else '远程开户:未开 '
            b6 = '本地开户:已开 ' if bl & 0x40 else '本地开户:未开 '
            b5 = '身份认证状态:有效 ' if bl & 0x20 else '身份认证状态:无效 '
            b4 = '保电状态:保电 ' if bl & 0x10 else '保电状态:非保电 '
            b3 = '当前阶梯:第二套 ' if bl & 0x8 else '当前阶梯:第一套 '
            b2 = '当前运行分时费率:第二套 ' if bl & 0x4 else '当前运行分时费率:第一套 '
            b10 = ''
            if bl & 0x2:
                b10 = '电能表类型:电费型预付费 '
            if bl & 0x1:
                b10 = '电能表类型:电量型预付费 '
            if (bl & 0x3) == 0:
                b10 = '电能表类型:非预付费 '
            stat += "{}{}{}{}{}{}{}\n".format(b7, b6, b5, b4, b3, b2, b10)
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
            bl2 = '开端钮盖 ' if bl & 0x4 else ''
            bl1 = '开表盖 ' if bl & 0x2 else ''
            bl0 = '电流严重不平衡 ' if bl & 0x1 else ''
            stat = "{}{}{}{}{}{}{}{}{}{}{}\n".format(b7, b6, b5, b4, b3, b2, b1, b0, bl2, bl1, bl0)
            if stat == '\n':
                stat = '合相无故障\n'
        return stat

    def _get_pdu_head(self):
        amm_addr = '%012d' % int(self.address)
        buf = [0xFE]
        buf.append(0xFE)
        buf.append(0x68)
        for i in range(12, 0, -2):
            buf.append(int(amm_addr[(i-2):i], base=16))
        buf.append(0x68)
        return buf

    def create_cmd_pdu(self, di, value=[]): # pass  # NOQA
        dt = diType(di)
        pdu = self._get_pdu_head()
        length = len(dt.di)
        if len(value) > 0:
            assert dt.write_ctrcode, ("read only for di:%s" % di)
            pdu.append(dt.Write_ctrcode)
            if dt.write_ctrcode == WriteData: # pass  # NOQA
                length = len(dt.di)+len(self.passwd)+len(self.cli_code)+len(value)
        else:
            assert dt.read_ctrcode, ("write only for di:%s" % di)
            if len(self._rece_buf) > 0:  # pass  # NOQA
                pdu.append(ReadFollowData)  # pass  # NOQA
            else:
                pdu.append(dt.read_ctrcode)
        di_seq = self._plus33(dt.di)
        if self._seq != 0:
            length += 1
            di_seq.extend(self._plus33([self._seq]))
        pdu.append(length)
        pdu.extend(di_seq)
        if len(value) > 0:
            pc = "%08d%08d" % (int(self.passwd), int(self.cli_code))
            pcl = self._strd2hlist(pc)
            pdu.extend(self._plus33(pcl))
            pdu.extend(self._plus33(value))
        pdu.append(chsum(pdu[pdu.index(0x68):]))
        pdu.append(0x16)
        return pdu

    def _parse_read_response(self, buf):
        ret = {}
        dtype = diType(self._sub33(buf[0:4]))
        tval = self._sub33(buf[4:])
        self._debug("the value part:%r" % [hex(x) for x in tval])
        if dtype.di[3] != 0xff and dtype.di[2] != 0xff:
            val = self._hexbcd2float(tval, dtype.val_decimal_places)
            if dtype.unit == "meter-stat":
                val = self._hex2stat(tval, dtype.di[3])
            if dtype.unit == "ASCII":
                val = self.hex2assci(tval, dtype.val_decimal_places)
            if dtype.unit == "DATE":
                val = self._hex2date(tval)
            if dtype.unit == "kW-DATE":
                val = self._hex2kwdate(tval, dtype.val_decimal_places)
            if dtype.unit == "Hex":
                val = [hex(x) for x in tval]
            if dtype.unit == "RDATE":
                val = self._hex2rdate(tval)
        else:
            l = dtype.val_len
            r = (len(tval)//l)
            if r != 4 and r != 5 and r != 7:
                raise ValueError("unknow data")
            if r == 4:
                rs = ["C", "B", "A", "total"]
            if r == 5:
                rs = ["费率4", "费率3", "费率2", "费率1", "total"]
            if r == 7:
                rs = ["7", "6", "5", "4", "3", "2", "1"]
            for i in range(0, r, 1):
                key = "%s-%s(%s)" % (dtype.chinese_name, rs[i], dtype.unit)
                if dtype.unit == "kW-DATE":
                    val = self._hex2kwdate(tval[(i*l):(i*l+l)], dtype.val_decimal_places)
                if dtype.unit == "meter-stat":
                    val = self._hex2stat(tval[(i*l):(i*l+l)], int(rs[i]))
                else:
                    val = self._hexbcd2float(tval[(i*l):(i*l+l)], dtype.val_decimal_places) # pass  # NOQA
                ret.update({key: val})
            return ret
            # val = hexbcd2float([0x34,0x12,0x56,0x78], dtype.val_decimal_places)
        key = "%s(%s)" % (dtype.chinese_name, dtype.unit)
        ret = {key: val}
        return ret

    def _parse_write_response(self, buf):
        ret = {}
        return ret

    def _write_buf(self, buf):
        lenght = len(buf)
        if self._seq:
            self._rece_buf.extend(buf[5:(lenght-1)])
        else:
            self._rece_buf.extend(buf)
        self._seq += 1
        self._debug("self._rece_buf:")
        self._debug(len(self._rece_buf))
        self._debug([hex(x) for x in self._rece_buf])
        for i in range(0, len(self._rece_buf)):
            if self._rece_buf[i] == 0xdd:
                self._debug(i,)

    def analysis(self, buf):
        ret = {}
        ctb = 0
        try:
            index = buf.index(0x68)
            if len(buf) < 12 or \
                    buf[len(buf) - 1] != 0x16 or \
                    chsum(buf[index:(len(buf) - 2)]) != \
                    buf[len(buf) - 2]:
                raise ValueError("timeout or check code error")
            ctb = buf[index + 8]
            addr = (buf[index + 1: index + 7])
            addr.reverse()
            assrs = ""
            for x in addr:
                assrs += "{:02x}".format(x)
            if not (assrs == ('%012d' % int(self.address)) or ctb == 0x93):
                raise Exception("response meter address wrong")
            if ctb == 0xC3:
                raise DLT645_07_Expection_serr(self._sub33([buf[index + 11]])[0]) # pass  # NOQA
            if not (ctb & 0xf0 == 0x90 or ctb & 0xf3 == 0x83 or ctb == 0xB1): # pass  # NOQA
                raise DLT645_07_Expection_err(self._sub33([buf[index + 10]])[0])
        except DLT645_07_Expection_serr as e:
            ret.update({"安全认证错误信息": e.message})
            return ret
        except DLT645_07_Expection_err as e:
            ret.update({"错误信息": e.message})
            return ret
        except Exception as e:
            ret.update({"error": str(e)})
            return ret
        val_bs = buf[(index+10): (index+10+buf[index+9])]
        if ctb == (ReadData | 0x80):  # pass  # NOQA
            ret = self._parse_read_response(val_bs)
        if ctb == (ReadFollowData | 0x80):  # pass  # NOQA
            self._write_buf(val_bs)
            ret = self._parse_read_response(self._rece_buf)
        if ctb == (WriteData | 0x80): # pass  # NOQA
            ret = self._parse_write_response(val_bs)
        if ctb == 0xB1:
            self._write_buf(val_bs)
            return ReadFollowData # pass  # NOQA
        if ctb == (ReadAddr | 0x80): # pass  # NOQA
            return {"meter-address": str(h2bcd(self._sub33(val_bs)))}
        if ctb == (ChangeComRate | 0x80): # pass  # NOQA
            return {"ChangeComRate": "ok"}
        if ctb == (ControlOperate | 0x80): # pass  # NOQA
            return {"ControlOperate": "ok"}
        self._debug("self._rece_buf:")
        self._debug([hex(x) for x in self._rece_buf])
        self._rece_buf[:] = []
        self._seq = 0
        return ret

    @property
    def get_meter_address_pdu(self):
        return [0xFE, 0xFE, 0xFE, 0xFE, 0x68, 0xAA, 0xAA, 0xAA,
                0xAA, 0xAA, 0xAA, 0x68, ReadAddr, 0, 0xDF, 0x16] # pass  # NOQA

    @property
    def broadcast_time_pdu(self):
        pdu = [0xFE, 0xFE, 0xFE, 0xFE, 0x68, 0x99, 0x99, 0x99,
               0x99, 0x99, 0x99, 0x68, BroadcastTime, 0x06] # pass  # NOQA
        tstr = time.strftime("%S%M%H%d%m%y", time.localtime())
        for i in range(0, 12, 2):
            pdu.append(int(tstr[i:i+2], base=16))
        pdu.append(chsum(pdu[4:]))
        pdu.append(0x16)
        return pdu

    def set_comrate(self, brate=2400):
        bbyte = brate//600
        bbyte = bbyte << 1
        if bbyte == 0 or bbyte > 0x40:
            raise ValueError("wrong baudrate")
        pdu = self._get_pdu_head()
        pdu.extend([ChangeComRate, # pass  # NOQA
                    0x01,
                    bbyte,
                    chsum(pdu[pdu.index(0x68):]),
                    0x16])
        return pdu

    def _strd2hlist(self, strd):
        ls = []
        for i in range(0, len(strd), 2):
            ls.append(int(strd[i:i+2], base=16))
        return ls

    def _control_operate_pdu(self, ctrbyte):
        pc = "%08d%08d" % (int(self.passwd), int(self.cli_code))
        pcl = self._strd2hlist(pc)
        ts = time.strftime("%y%m%d235959", time.localtime())
        tsl = self._strd2hlist(ts)
        lenght = len(pcl) + len(tsl) + 2
        pdu = self._get_pdu_head()
        pdu.extend([ControlOperate, # pass  # NOQA
                    lenght])
        pdu.extend(self._plus33(pcl))
        pdu.extend(self._plus33([0, ctrbyte]))
        pdu.extend(self._plus33(tsl))
        pdu.extend([chsum(pdu[pdu.index(0x68):]), 0x16])
        return pdu

    # 1AH跳闸,1BH合闸允许,2AH报警,2BH报警解除,3AH保电,3BH保电解除
    @property
    def switch_off_pdu(self):
        return self._control_operate_pdu(0x1A)

    @property
    def switch_on_enable_pdu(self):
        return self._control_operate_pdu(0x1B)

    @property
    def switch_on_pdu(self):
        return self._control_operate_pdu(0x1C)

    @property
    def warning_enable_pdu(self):
        return self._control_operate_pdu(0x2A)

    @property
    def warning_disable_pdu(self):
        return self._control_operate_pdu(0x2B)

    @property
    def keep_power_pdu(self):
        return self._control_operate_pdu(0x3A)

    @property
    def keep_power_release_pdu(self):
        return self._control_operate_pdu(0x3B)


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
