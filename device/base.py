#!/usr/bin/python
# encoding: UTF-8
"""
# Author: yjiong
# Created Time : 2019-10-18 14:18:41

# File Name: base.py
# Description:

"""

import time
import re
import os
import sys
import traceback
import configparser
import codecs
import platform
# from serial.tools import list_ports as spl

_VERSION = 'v1.0.0'
DevID = "_devid"
DevConn = "_conn"
DevType = "_type"
DevAddr = "devaddr"
DevName = "dname"
Commif = "commif"
UpdateDevItem = "manager/dev/update.do"
SetDevVar = "do/setvar"
GetDevVar = "do/getvar"
_PYVER = platform.python_version()[0]


def objLoger(obj):
    """Function for attaching a debugging logger to a class or function."""
    # create a logger for this object
    import logging.handlers
    logger = logging.getLogger(obj.__module__ + '.' + obj.__name__)

    '''
    fh = logging.handlers.RotatingFileHandler(
            os.path.join(sys.path[0], obj.__name__+'.log'),
            maxBytes=1024*1024*50,
            backupCount=3,
            encoding='utf-8')
            '''
    # fh.setFormatter(formats)
    # logger.addHandler(fh)
    # filter=logging.Filter(”abc.xxx”)
    ch = logging.StreamHandler()
    fm = logging.Formatter(
        '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    ch.setFormatter(fm)
    # logger.setLevel(20)
    logger.addHandler(ch)
    obj._logger = logger
    obj._debug = logger.debug
    obj._info = logger.info
    obj._warning = logger.warning
    obj._error = logger.error
    obj._exception = logger.exception
    obj._fatal = logger.fatal
    return obj


@objLoger
class DynApp(object):
    config = '/etc/default/iotdconf'
    devtypes = {}
    syscommif = {}
    serstat = {}
    if os.path.exists(config):
        with codecs.open(config, encoding='utf-8') as f:
            conf = configparser.ConfigParser()
            conf.readfp(f)
            syscommif = dict(conf.items('commif'))
    else:
        syscommif.update({'rs485-1': '/dev/ttyS1',
                          'rs485-2': '/dev/ttyS2'})
    # for pt in spl.comports():
    for pt in syscommif:
        serstat[syscommif[pt]] = 0

    def __init__(self):
        self.devlist_file = '/opt/iot/devlist'
        self.devlist = {}
        self.load_drive()
        self._dev_update()

    def _dev_update(self):
        if os.path.exists(self.devlist_file):
            with codecs.open(self.devlist_file, encoding='utf-8') as f:
                conf = configparser.ConfigParser()
                conf.readfp(f)
                for devid in conf.sections():
                    try:
                        dt = conf.get(devid, DevType)
                        ob = self.devtypes[dt](dict(conf.items(devid)))
                        ob._logger.level = self._logger.level
                        self.devlist.update({devid: ob})
                    except Exception:
                        print(traceback.format_exc())

    @staticmethod
    def registerdev(app, devname):
        def call(cls):
            # thiscls = cls()
            # app.devtypes[devname] = thiscls
            app.devtypes[devname] = cls
            return cls
        return call

    def load_drive(self, path=os.path.dirname(os.path.abspath(__file__))):
        # self._debug("current path :%s" % path)
        for pyfl in os.listdir(path):
            try:
                if os.path.isdir(path + "/" + pyfl):
                    sys.path.append(path + "/" + pyfl)
                    # self._debug(sys.path)
                    self.load_drive(path + "/" + pyfl)
                tstr = pyfl.split('.')
                if len(tstr) > 1 and tstr[1] == r'py':
                    if re.search(r'(\w+).py$', pyfl)\
                            and pyfl != os.path.basename(__file__)\
                            and pyfl != "__init__.py":
                        self._debug("import modle :" + tstr[0])
                        __import__(tstr[0])

            except Exception:
                self._error(traceback.format_exc())


@objLoger
class DevObj(object):
    def _getser(self, serialPort):
        import serial
        ser = serial.Serial()
        ser.port = serialPort
        ser.baudrate = self.baudrate
        ser.bytesize = self.bytesize
        ser.parity = self.parity
        ser.stopbits = self.stopbits
        ser.timeout = self.timeout

        try:
            ser.open()
            DynApp.serstat[serialPort] = 1
        except Exception as e:
            DynApp.serstat[serialPort] = 0
            # print("%s open failed %s" % (serialPort, e))
            return 0
        return ser

    def rw_dev(self, rw='r', var_value=None):
        ser = 0
        try:
            if re.search(r'(/dev.+)|(COM\d+)|(com\d+)', self.commif):
                if self.commif not in DynApp.serstat:
                    DynApp.serstat[self.commif] = 0
                count = 0
                while DynApp.serstat[self.commif] != 0:
                    time.sleep(0.2)
                    count += 1
                    if count > 25:
                        raise RuntimeError("timeout")
                ser = self._getser(self.commif)
                if ser == 0:
                    raise IOError("open serialPort failed")
                else:
                    DynApp.serstat[self.commif] = 1
                    self.serial = ser
            value = self.rw_device(rw=rw, var_value=var_value)
            if len(value) == 0:
                raise ValueError("value len is zero")
        except Exception as e:
            value = {'error': e}
            time.sleep(0.2)
            self._error(e)
        if ser != 0:
            if ser.isOpen():
                ser.close()
            DynApp.serstat[self.commif] = 0
        return value

    @property
    def dev_help(self):
        return {"error": u"设备驱动程序未定义dev_help方法"}

    @property
    def dev_commif(self):
        return self.syscommif

    def dev_element(self):
        self.element = {DevAddr: self.addr,
                        DevType: self.__class__.__name__}

    def dev_check_key(self, ele):
        return {"error": u"设备驱动程序未定义dev_check_key方法"}

    def rw_device(self, rw=None, var_value=None):
        return {"error": u"设备驱动程序未定义rw_device方法"}

    def getCommif(self, ele):
        self.commif = ele[Commif]
        self.syscommif = ele[Commif]
        if self.commif in DynApp.syscommif:
            self.commif = DynApp.syscommif[self.commif]
