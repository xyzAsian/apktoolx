#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import os,sys
from tools.Tool import *

UNINSTALL_FILTER = ["com.github.shadowsocks", "com.github.shadowsocks.plugin.obfs_local", "com.topjohnwu.magisk","qegx.xpg"]

class adbx(object):
    def __init__(self, sdevice=""):
        self.device = sdevice
        self.adb = ADB
        if self.device:
            self.adb = "%s -s %s"%(ADB, self.device)

    @output
    def install(self, apk):
        return exec_command("%s install %s"%(self.adb, apk))

    @output
    def uninstall_item(self, pkgname, allow_fail = True):
        b = exec_command("%s uninstall %s"%(self.adb, pkgname), allow_fail=allow_fail, status=False)
        if "Unknown package" in b :
            return "Unknow package : %s"%(pkgname)
        return b

    def uninstall_all(self, allow_fail = True):
        pkgstr = exec_command("%s shell pm list packages -3"%(self.adb), allow_fail=allow_fail, status=False)
        pkgs = pkgstr.split("\n")
        for item in pkgs:
            if not item:
                continue
            pkg = item.split(":")[1].strip()
            if pkg not in UNINSTALL_FILTER:
                self.uninstall_item(pkg)
            else:
                print("Skip Package %s"%(pkg))

    @output
    def pmclear(self, pkgname):
        return exec_command("%s shell pm clear '%s'"%(self.adb, pkgname))

    @output
    def start(self,pkgname, launchableActivity, time = False, debug=False, num = 1):
        W = ""
        if time:
            W = "-W"
        D = ""
        if debug:
            D = "-D -n "
        return exec_command("%s shell am start %s %s %s/%s"%(self.adb, W, D, pkgname, launchableActivity))

    @output
    def path(self, pkgname):
        return exec_command("adb shell pm path %s"%(pkgname), pexception=True)

if __name__ == "__main__":
    pass