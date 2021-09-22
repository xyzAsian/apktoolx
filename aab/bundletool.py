#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import os,sys
from tools.Tool import *

class bundletool(object):
    def __init__(self, sdevice=""):
        self.device = sdevice
        self.bundletool = BUNDLE_TOOL
        if self.device:
            self.bundletool = "%s -s %s"%(BUNDLE_TOOL, self.device)

    @output
    def build_apks(self, aab, out_apks, is_overwrite=True, is_local_testing=True, is_connected_device=True, device_id='', device_spec=''):
        overwrite = '--overwrite' if is_overwrite else ''
        local_testing = '--local-testing' if is_local_testing else ''
        connected_device = '--connected-device' if is_connected_device else ''
        device_id_ = '--device-id=%s'%(device_id) if device_id else ''
        device_spec_ = '--device-spec=%s'%(device_spec) if device_spec else ''
        others = "%s %s %s %s %s"%(overwrite, local_testing, connected_device, device_id_, device_spec_)
        return exec_command("%s build-apks %s --bundle=%s --output=%s"%(self.bundletool, others, aab, out_apks))

    @output
    def install_apks(self, apks):
        return exec_command("%s install-apks --apks=%s"%(self.bundletool, apks))

    @output
    def get_device_spec(self):
        output_device_spec = "connected_device.spec.json"
        return exec_command("%s get-device-spec --output=%s"%(self.bundletool, output_device_spec))


    def extract_apks(self, apks, device_spec):
        output_dir = os.path.join(os.path.abspath('.'), 'extract_apks')
        return exec_command("%s extract-apks --apks=%s --output-dir=%s --device-spec=%s"%(self.bundletool, apks, output_dir, device_spec))