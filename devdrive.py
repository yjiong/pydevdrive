#!/usr/bin/python
# coding=utf8
"""
# Author: yjiong
# Created Time : 2019-10-18 14:18:41
# Mail: 4418229@qq.com
# File Name: devdrive.py
# Description:

"""

import time
import grpc
import drivesvr_pb2_grpc
import drivesvr_pb2
import sys
import os
import json
import traceback
import argparse
from concurrent import futures

sys.path.append(sys.path[0] + "/device")
try:
    import base
except Exception:
    tp = (os.path.split(os.path.realpath(__file__))[0])
    sys.path.append(os.path.dirname(tp))
    import base


class DevDriveService(drivesvr_pb2_grpc.DriveServicer,
                      base.DynApp,
                      argparse.ArgumentParser):
    def __init__(self):
        argparse.ArgumentParser.__init__(self,
                                         description='IOT device drive')
        self.add_argument('--version', action='version', version=base._VERSION)
        self.add_argument("-L", "--loglevel",
                          default=2, type=int,
                          choices=[1, 2, 3, 4, 5, 6],
                          help='''set loglevel,
                                  1=debug,
                                  2=info,
                                  3=warning,
                                  4=error,
                                  5=exception,
                                  6=fatal,
                                  defalut=2''')
        self.add_argument("-H", "--host", default="localhost",
                          type=str, help="server interface, defalut=localhost")
        self.add_argument("-P", "--port", default="9974",
                          type=str, help="server port, defualut=9974")
        self._logger.setLevel(self.parse_args().loglevel*10)
        base.DynApp.__init__(self)
        self.response = drivesvr_pb2.DriveSvrResponse()
        self.handlers = [
                self._dev_help,
                self._dev_check_key,
                self._support_list,
                self._dev_list,
                self._dev_update,
                self._dev_commif,
                self._dev_element,
                self._dev_getset,
                self._get_version]

    def DriveSvr(self, request, context):
        self._debug("request.Devid: %s" % request.Devid)
        self._debug("request.Cmd: %s" % self.handlers[request.Cmd].__name__)
        self._debug("request.CmdStr: %s" % request.CmdStr)
        self._debug("request.Data: %s" % request.Data)
        try:
            reqs = request.Data if base._PYVER == "2" else\
                bytes.decode(request.Data)
            try:
                rdata = json.loads(reqs)
            except Exception:
                rdata = None
            self.handlers[request.Cmd](devid=request.Devid,
                                       rw=request.CmdStr,
                                       vv=rdata)
            self.response.Data = self.respstr if base._PYVER == "2" else\
                str.encode(self.respstr)
        except Exception as e:
            self._debug(traceback.format_exc())
            context.set_code(grpc.StatusCode.ABORTED)
            context.set_details(str(e))
        return self.response

    def server(self):
        # 定义服务器并设置最大连接数,corcurrent.futures是一个并发库，类似于线程池的概念
        grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
        # add drivesvr too grpcServer
        drivesvr_pb2_grpc.add_DriveServicer_to_server(self, grpcServer)
        grpcServer.add_insecure_port(
                self.parse_args().host + ':' + self.parse_args().port)
        grpcServer.start()
        try:
            while True:
                time.sleep(100)
        except KeyboardInterrupt:
            grpcServer.stop(0)

    def _dev_help(self, **kw):
        if kw['devid'] not in self.devtypes:
            raise KeyError("device type %s not exist" % kw['devid'])
        ustr = self.devtypes[kw['devid']].dev_help()
        self.response.Data = json.dumps(ustr)

    def _dev_check_key(self, **kw):
        if kw['devid'] not in self.devtypes:
            raise KeyError("device type %s not exist" % kw['devid'])
        self.respstr = json.dumps(
                self.devtypes[kw['devid']].dev_check_key(kw['vv']))

    def _support_list(self, **kw):
        self._dev_update()
        retlist = [key for key in self.devtypes]
        retlist.sort()
        self.respstr = json.dumps(retlist)

    def _dev_list(self, **kw):
        self._dev_update()
        retlist = [key for key in self.devlist]
        retlist.sort()
        self.respstr = json.dumps(retlist)

    def _dev_commif(self, **kw):
        if kw['devid'] not in self.devlist:
            raise KeyError("device %s not exist" % kw['devid'])
        ustr = self.devlist[kw['devid']].dev_commif
        self.respstr = json.dumps(ustr)

    def _dev_element(self, **kw):
        print("in dev element")
        if kw['devid'] not in self.devlist:
            raise KeyError("device %s not exist" % kw['devid'])
        ele = self.devlist[kw['devid']].dev_element()
        ele[base.DevID] = kw['devid']
        self.respstr = json.dumps(ele)

    def _dev_getset(self, **kw):
        if kw['devid'] not in self.devlist:
            raise KeyError("device %s not exist" % kw['devid'])
        rw = "r"
        vv = None
        if kw['rw'] != "":
            rw = kw['rw']
        if kw['vv'] != "":
            vv = kw['vv']
        self.respstr = json.dumps(
                self.devlist[kw['devid']].rw_dev(rw, vv))

    def _get_version(self, **kw):
        self.respstr = json.dumps(base._VERSION)


if __name__ == '__main__':
    DevDriveService().server()
