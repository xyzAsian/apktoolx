#!/usr/bin/python3.8
# -*- coding: UTF-8 -*-

import os,sys
from tools.Tool import *

class aabx(object):
    def __init__(self, inAa, bt):
        self.inAa = inAa
        self.workspace = "%s/.workspace"%(os.path.abspath('.'))
        self.bundletool = bt

    def print_aab(self):
        pass

    def build_apks(self):
        out_apks = "%s.apks"%(self.inAa[:-4])
        self.bundletool.build_apks(self.inAa, out_apks)

    def install(self):
        if self.inAa.endswith('.aab'):
            self.install_aab()
        elif self.inAa.endswith('.apks'):
            self.install_apks()
        else:
            print('Not support %s file'%(self.inAa[self.inAa.rfind('.'):]))

    def install_aab(self):
        out_apks = "%s.apks"%(self.inAa[:-4])
        self.bundletool.build_apks(self.inAa, out_apks)
        self.bundletool.install_apks(out_apks)

    def install_apks(self):
        self.bundletool.install_apks(self.inAa)

    def uninstall(self):
        pass