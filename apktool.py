#!/usr/local/bin/python3.8

import os,sys
from adbx.adbx import *
from adbx.apkx import *

import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Yazhou.Xie's command tool")
    # No apk param
    parser.add_argument("-ua", "--uninstall-all", dest="uninstall_all", action="store_true", help="uninstall all installed apk")

    # Must apk param
    parser.add_argument("-d", "--detail", dest="detail", action="store_true", help="Display apk manifest detail")
    parser.add_argument("-de", "--debugable", dest="debugable", action="store_true", help="debugable apk")
    parser.add_argument("-dmc", "--dex-method-count", dest="dex_method_count", action="store_true", help="Apk or dex method count")
    parser.add_argument("-dfc", "--dex-field-count", dest="dex_field_count", action="store_true", help="Apk or dex field count")
    parser.add_argument("-dtc", "--dex-type-count", dest="dex_type_count", action="store_true", help="Apk or dex type count")

    parser.add_argument("-fsc", "--find-same-class", dest="find_same_class", action="store_true", help="find if apk have same class in diff dex")
    
    parser.add_argument("-i","--install", dest="install", action="store_true", help="Install apk")

    parser.add_argument("-ks", "--kill-sign", dest="kill_sign", action="store_true", help="kill sign check for apk")

    parser.add_argument("-p", "--pm-clear", dest="pm_clear", action="store_true", help="pm clear apk")
    parser.add_argument("-ps", "--pmclear-start", dest="pm_clear_start", action="store_true", help="pm clear apk and start LaunchableActivity")
    parser.add_argument("-psw", "--pmclear-start-W", dest="pm_clear_start_W", action="store_true", help="pm clear apk and start -W LaunchableActivity")
    parser.add_argument("-pa", "--path", dest="path", action="store_true", help="pm path apk")

    parser.add_argument("-s", "--start", dest="start", action="store_true", help="start LaunchableActivity")
    parser.add_argument("-sd","--start-D", dest="start_D", action="store_true", help="start -D LaunchableActivity")
    parser.add_argument("-si", "--sign", dest="sign", action="store_true", help="sign apk to \{dirname\}/ori.signed.apk")
    parser.add_argument("-sw","--start-w", dest="start_W", action="store_true", help="start -W LaunchableActivity")

    parser.add_argument("-ts", "--to-smali", dest="to_smali", action="store_true", help="Apk or dex baksmali to smali")
    
    parser.add_argument("-u", "--uninstall", dest="uninstall", action="store_true", help="uninstall apk")
    parser.add_argument("-ui", "--un-install", dest="uninstall_install", action="store_true", help="uninstall and install apk")
    parser.add_argument("-uis", "--un-ins-start", dest="uninstall_install_start", action="store_true", help="uninstall and install apk and start LaunchableActivity")
    parser.add_argument("-uisw", "--un-ins-startW", dest="uninstall_install_start_W", action="store_true", help="uninstall and install apk and start -W LaunchableActivity")
    
    isNeedApk = True
    for arg in sys.argv:
        if arg.find("-ua") > -1 or arg.find("--uninstall-all") > -1:
            isNeedApk = False
    if isNeedApk:
        parser.add_argument("apk", action="store", help="The apk file path")

    args = parser.parse_args()
    adbx = adbx()
    if args.uninstall_all:
        adbx.uninstall_all()
        exit(0)
    apkpath = os.path.abspath(args.apk)
    manifest = AndroidManifest(apkpath) 
    apkx = apkx(apkpath, manifest=manifest, adbx = adbx)
    if args.detail:
        apkx.print_apk()
    if args.uninstall:
        apkx.uninstall(allow_fail=False)
    if args.install:
        apkx.install()
    if args.uninstall_install:
        apkx.uninstall()
        apkx.install()
    if args.start:
        apkx.start(time=False, num=1)
    if args.start_W:
        apkx.start(time=True, num=1)
    if args.start_D:
        apkx.start(time=False, debug=True, num=1)
    if args.uninstall_install_start:
        apkx.uninstall()
        apkx.install()
        apkx.start(time=False, num=1)
    if args.uninstall_install_start_W:
        apkx.uninstall()
        apkx.install()
        apkx.start(time=True, num=1)
    if args.pm_clear:
        apkx.pmclear()
    if args.pm_clear_start:
        apkx.pmclear()
        apkx.start(time=False)
    if args.pm_clear_start_W:
        apkx.pmclear()
        apkx.start(time=True)
    if args.path:
        apkx.apk_path_on_device()
    if args.sign:
        apkx.apksign()
    if args.kill_sign:
        apkx.kill_signcheck()
    if args.find_same_class:
        apkx.find_same_class()
    if args.debugable:
        apkx.debugable()
    if args.to_smali:
        apkx.apk_2_smali()
    if args.dex_method_count:
        apkx.dex_method_id_count()
    if args.dex_field_count:
        apkx.dex_field_id_count()
    if args.dex_type_count:
        apkx.dex_type_id_count()