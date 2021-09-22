#!/usr/local/bin/python3.8

import os,sys
from aab.bundletool import *
from aab.aabx import *

import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Yazhou.Xie's aab command tool")

    #aab
    parser.add_argument("-d", "--detail", dest="detail", action="store_true", help="Display aab manifest detail")
    parser.add_argument("-u", "--uninstall", dest="uninstall", action="store_true", help="uninstall aab")
    parser.add_argument("-b","--build", dest="build", action="store_true", help="Build apks")
    parser.add_argument("-i","--install", dest="install", action="store_true", help="Install aab")

    # apks
    parser.add_argument("-ia","--install-apks", dest="install_apks", action="store_true", help="Install aab")

    # no args
    parser.add_argument("-ds", "--get-device-spec", dest="get_device_spec", action="store_true", help="Apk or dex method count")

    
    isNeedAab = True
    for arg in sys.argv:
        if arg.find("-ds") > -1 or arg.find("--get-device-spec") > -1:
            isNeedAab = False

    if isNeedAab:
        parser.add_argument("aab", action="store", help="The aab file path")

    args = parser.parse_args()
    bt = bundletool()
    aabpath = os.path.abspath(args.aab)
    aabx = aabx(aabpath, bt)
    if args.detail:
        aabx.print_aab()
    if args.uninstall:
        aabx.uninstall()
    if args.install:
        aabx.install()
    if args.build:
        aabx.build_apks()