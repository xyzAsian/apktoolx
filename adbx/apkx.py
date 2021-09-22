#!/usr/bin/python3.8
# -*- coding: UTF-8 -*-

import os,sys
from apk.manifest import *
from tools.Tool import *
import base64

class apkx(object):
    def __init__(self, inApk, manifest, adbx):
        self.inApk = inApk
        self.workspace = "%s/.workspace"%(os.path.abspath('.'))
        self.adbx = adbx
        self.manifest=manifest
        self.mac_mach = "''" if PLATFORM=="macos" else ""

    ## adb 

    def print_apk(self):
        print(self.manifest.toString())
    
    def install(self):
        self.adbx.install(self.inApk)

    def uninstall(self, allow_fail = True):
        return self.adbx.uninstall_item(self.manifest.pkgname)

    def start(self, time = False, debug=False, num = 1):
        self.adbx.start(self.manifest.pkgname, self.manifest.launchableActivity, time, debug, num)
    
    def pmclear(self):
        self.adbx.pmclear(self.manifest.pkgname)

    @output
    def apksign(self, jks=JKS):
        return exec_command("%s sign --ks %s --ks-key-alias debugkey --ks-pass pass:qwe123 --key-pass pass:qwe123 --out %s.signed.apk %s"%(APK_SIGNER, jks, self.inApk[0:-4], self.inApk))


    ## apk

    def create_workspace(self):
        if os.path.exists(self.workspace):
            exec_command("rm -rf %s"%(self.workspace), doing=False)
        os.makedirs(self.workspace)

    def clear_workspace(self):
        exec_command("rm -rf %s"%(self.workspace), doing=False)

    def get_superclass(self, smali_path):
        with open(smali_path) as smail_file:
            for line in smail_file.readlines():
                if line.startswith(".super"):
                    return line.lstrip(".super").strip()
        
        return None

    # clazz = "Lcom/example/demo;"
    def find_class_path(self, clazz, dexdir):
        dexes = [os.path.join(dexdir, name) for name in os.listdir(dexdir) if name.endswith('.dex')]
        for dexitem in dexes:
            b = exec_command("%s list classes %s"%(BAKSMALI, dexitem))
            print(clazz)
            if b.find(clazz) >=0 :
                exec_command("%s d %s -o %s"%(BAKSMALI, dexitem, dexitem[0:-4]), allow_fail=False)
                smali_path = "%s/%s"%(dexitem[0:-4], clazz[1:-1])
                super_class = self.get_superclass("%s.smali"%smali_path)
                if super_class == 'Landroid/app/Application;':
                    return smali_path,dexitem
                else:
                    exec_command("rm -rf %s"%(dexitem[0:-4]))
                    return self.find_class_path(super_class, dexdir)
                
        return None,None

    def splitKey(self, s,start,head,tail):
        i = s.find(head,start)
        if i != -1 :
            i = i + len(head)
            j = s.find(tail,i)
            return (j,s[i:j])
        else:
            return (start,'')

    def parse_cert(self, rsa_file):
        content = exec_command("openssl pkcs7 -inform DER -in '%s' -print_certs -text" % rsa_file, allow_fail=False)
        i,cert_base64 = self.splitKey(content,0,'-----BEGIN CERTIFICATE-----','-----END CERTIFICATE-----')
        cert = cert_base64.replace('\n','')
        return cert

    @output
    def kill_signcheck(self):
        try:
            self.create_workspace()
            outapk = "%s.killsign.apk"%(self.inApk[0:-4])
            exec_command("cp -f %s %s"%(self.inApk, outapk), log = True, status=True)
            '''
            # Plan 1
            exec_command("unzip %s classes.dex -d %s"%(self.inApk, self.workspace), log = True, status=True)
            exec_command("%s d %s/classes.dex -o %s/classes"%(BAKSMALI, self.workspace, self.workspace), log = True, status=True)
            exec_command("cp -rf %s/xyz %s/classes"%(MY_SMALI_DIR, self.workspace), log = True, status=True)
            exec_command("%s a %s/classes -o %s/classes.dex"%(SMALI, self.workspace, self.workspace), log = True, status=True)
            exec_command("cd %s && zip -rD %s classes.dex && cd -"%(self.workspace, outapk), log = True, status=True)
            '''
            # Plan 2
            dexdir = "%s/dex"%self.workspace
            exec_command("unzip %s classes*.dex -d %s"%(self.inApk, dexdir),allow_fail=False)
            # 查找 application 并且进行修改
            if self.manifest.applicaionName and self.manifest.applicaionName != "android.app.Application":
                applicaionSmali = "L%s;"%(self.manifest.applicaionName.replace('.','/').strip())
                smali_path,dexitem = self.find_class_path(applicaionSmali, dexdir)
                if not smali_path:
                    print("Can't find application smali")
                    exit()
                exec_command("sed -i %s 's#.super Landroid/app/Application;#.super Lxyz/NoSignApplication;#g' %s.smali"%(self.mac_mach, smali_path))
                exec_command("sed -i %s 's#Landroid/app/Application;->#Lxyz/NoSignApplication;->#g' %s.smali"%(self.mac_mach, smali_path))
                exec_command("%s a %s -o %s && rm -rf %s"%(SMALI, dexitem[0:-4], dexitem, dexitem[0:-4]))
            
            # 拆分classes.dex
            filter_list = ['Landroid/support','Landroidx']
            if self.manifest.applicaionName:
                filter_list.append('L%s'%(self.manifest.applicaionName.replace('.','/').strip()))
            filter_list_str = ','.join([ item for item in filter_list])
            dex_num = exec_command("zipinfo %s \"classes*.dex\" | wc -l"%(self.inApk), allow_fail=False)
            dest_dex = "classes%d.dex"%(int(dex_num)+1)
            exec_command("%s split-dex --input-dex \"%s/classes.dex\" --out-dex \"%s/%s\" --filter \"%s\""%(FIX_SMALI, dexdir, dexdir, dest_dex, filter_list_str), allow_fail=False)
            # 合并dex
            splitdir = "%s/split"%(dexdir)
            exec_command("unzip %s META-INF/*.RSA META-INF/*.DSA -d %s"%(outapk, self.workspace), allow_fail=True)
            for _file in os.listdir("%s/META-INF"%self.workspace):
                if _file.endswith(".RSA") or _file.endswith(".DSA"):
                    cert = self.parse_cert("%s/META-INF/%s"%(self.workspace,_file))
                    exec_command("mkdir %s/smali && cp -rf %s/xyz %s/smali"%(self.workspace, MY_SMALI_DIR, self.workspace), allow_fail=False)
                    exec_command("find %s/smali -name NoSignApplication.smali | xargs sed -i %s 's@### Signatures Data ###@%s@g'"%(self.workspace, self.mac_mach,cert))
                    exec_command("%s a %s/smali -o %s/NoSignApplication.dex"%(SMALI, self.workspace, self.workspace), allow_fail=False)
                    exec_command("rm -rf %s/smali"%(self.workspace))
                    break
            exec_command("mkdir -p %s && mv %s/classes.dex %s"%(splitdir, dexdir, splitdir), allow_fail=False)
            exec_command("mv %s/NoSignApplication.dex %s/classes2.dex"%(self.workspace, splitdir), allow_fail=False)
            exec_command("%s Megedex -i %s -o %s"%(FIX_SMALI, splitdir, dexdir), allow_fail=False)
            exec_command("rm -rf %s"%(splitdir), allow_fail=False)
            exec_command("cd %s && zip -rD %s classes*.dex && cd -"%(dexdir, outapk), allow_fail=False)
            #修改Manifest
            exec_command("unzip %s AndroidManifest.xml -d %s && mv %s/AndroidManifest.xml %s/old.xml"%(outapk, self.workspace, self.workspace, self.workspace), allow_fail=False)
            exec_command("%s modify %s/old.xml %s/app.xml %s && rm -f %s/old.xml"%(AXML, self.workspace, self.workspace, self.manifest.applicaionName, self.workspace), allow_fail=False)
            exec_command("%s modify %s/app.xml %s/AndroidManifest.xml debugable && rm -f %s/app.xml"%(AXML, self.workspace, self.workspace, self.workspace), allow_fail=False)
            exec_command("cd %s && zip -rD %s AndroidManifest.xml && rm -f AndroidManifest.xml && cd -"%(self.workspace, outapk),allow_fail=False)
            self.del_sign()
            return "kill sign check success:\n%s"%outapk
        except Exception as e:
            return "kill sign check failed : %s"%(str(e))
        finally:
            self.clear_workspace()

    @output
    def find_same_class(self):
        try:
            self.create_workspace()
            exec_command("unzip %s classes*.dex -d %s"%(self.inApk ,self.workspace))
            same_classes = []
            diff_classes = []
            dexes = [os.path.join(self.workspace, name) for name in os.listdir(self.workspace) if name.endswith('.dex')]
            for dex in dexes:
                dex_classes_name = exec_command("%s list classes %s"%(BAKSMALI, dex))
                for item in dex_classes_name.split('\n'):
                    if item not in diff_classes:
                        #print("%s not in diff_classes"%item)
                        diff_classes.append(item)
                    else : 
                        #print("%s has same class"%item)
                        same_classes.append(item)
                        pass
                pass
            pass
            return "Find result:\n%s"%(same_classes)
        except Exception as e:
            return "Find same class Error : %s"%(str(e))
        finally:
            self.clear_workspace()

    @output
    def debugable(self):
        try:
            self.create_workspace()
            exec_command("unzip %s AndroidManifest.xml -d %s"%(self.inApk, self.workspace))
            exec_command("cd %s && mv AndroidManifest.xml old.xml && cd -"%(self.workspace))
            exec_command("%s modify %s/old.xml %s/AndroidManifest.xml debugable"%(AXML, self.workspace, self.workspace))
            exec_command("cd %s && rm -f old.xml && zip -rD %s AndroidManifest.xml && cd -"%(self.workspace, self.inApk))
            self.del_sign()
            return "debugable : %s"%(self.inApk)
        except Exception as e:
            return "debugable apk error"
        finally:
            self.clear_workspace()

    def del_sign(self):
        exec_command("zip -d %s \"META-INF/*.RSA\""%(self.inApk), allow_fail=True)
        exec_command("zip -d %s \"META-INF/*.SF\""%(self.inApk), allow_fail=True)
        exec_command("zip -d %s \"META-INF/*.MF\""%(self.inApk), allow_fail=True)
        exec_command("zip -d %s \"META-INF/*.DSA\""%(self.inApk), allow_fail=True, allow_waring=False)

    @output
    def apk_2_smali(self):
        try:
            self.create_workspace()
            if is_dex(self.inApk):
                dexes = [self.inApk]
            elif is_zip(self.inApk):
                exec_command("unzip %s \"classes*.dex\" -d %s"%(self.inApk, self.workspace))
                dexes = [os.path.join(self.workspace, item) for item in os.listdir(self.workspace) if item.endswith(".dex")]
            else :
                raise Exception("Not support file type")
            outdir = "%s_smali"%(os.path.abspath(self.inApk)[0:-4])
            for dex in dexes :
                outdir_dex = "%s/%s"%(outdir, dex[dex.rfind('/')+1:-4])
                exec_command("%s d %s -o %s"%(BAKSMALI, dex , outdir_dex))
            return "Apk to smali success : %s"%outdir
        except Exception as identifier:
            return "Apk to smali error : %s"%(str(identifier))
        finally:
            self.clear_workspace()
    
    @output
    def dex_method_id_count(self):
        try:
            self.create_workspace()
            if is_dex(self.inApk):
                dexes = [self.inApk]
            elif is_zip(self.inApk):
                exec_command("unzip %s \"classes*.dex\" -d %s"%(self.inApk, self.workspace), doing=False)
                dexes = [os.path.join(self.workspace, item) for item in os.listdir(self.workspace) if item.endswith(".dex")]
            else :
                raise Exception("Not support file type")
            print("Calc method id count :")
            total_count = 0
            for dex in dexes :
                methodsid = int(exec_command("hexdump -n 100 -C %s | grep 00000050 | awk -F ' ' '{print $13$12$11$10}'"%dex, status=False, doing=False), 16)
                print("%s : %d"%(os.path.basename(dex), methodsid))
                total_count += methodsid
                #fieldsid = int(exec_command("hexdump -n 100 -C %s | grep 00000050 | awk -F ' ' '{print $5$4$3$2}'"%dexpath, log=False), 16)
                #stringids=  int(exec_command("hexdump -n 100 -C %s | grep 00000030 | awk -F ' ' '{print $13$12$11$10}'" % dexpath, log=False) , 16)
                #typeIds=    int(exec_command("hexdump -n 100 -C %s | grep 00000040 | awk -F ' ' '{print $5$4$3$2}'"%dexpath, log=False), 16)
                #proto=      int(exec_command("hexdump -n 100 -C %s | grep 00000040 | awk -F ' ' '{print $13$12$11$10}'" % dexpath, log=False) , 16)
            return "Total : %d"%(total_count)
        except Exception as identifier:
            return "Calc dex method count error : %s"%(str(identifier))
        finally:
            self.clear_workspace()
    
    @output
    def dex_field_id_count(self):
        try:
            self.create_workspace()
            if is_dex(self.inApk):
                dexes = [self.inApk]
            elif is_zip(self.inApk):
                exec_command("unzip %s \"classes*.dex\" -d %s"%(self.inApk, self.workspace), doing=False)
                dexes = [os.path.join(self.workspace, item) for item in os.listdir(self.workspace) if item.endswith(".dex")]
            else :
                raise Exception("Not support file type")
            print("Calc field id count :")
            total_count = 0
            for dex in dexes :
                fieldsid = int(exec_command("hexdump -n 100 -C %s | grep 00000050 | awk -F ' ' '{print $5$4$3$2}'"%dex, status=False, doing=False), 16)
                print("%s : %d"%(os.path.basename(dex), fieldsid))
                total_count += fieldsid
                #methodsid = int(exec_command("hexdump -n 100 -C %s | grep 00000050 | awk -F ' ' '{print $13$12$11$10}'"%dex, status=False, doing=False), 16)
                #stringids=  int(exec_command("hexdump -n 100 -C %s | grep 00000030 | awk -F ' ' '{print $13$12$11$10}'" % dexpath, log=False) , 16)
                #typeIds=    int(exec_command("hexdump -n 100 -C %s | grep 00000040 | awk -F ' ' '{print $5$4$3$2}'"%dexpath, log=False), 16)
                #proto=      int(exec_command("hexdump -n 100 -C %s | grep 00000040 | awk -F ' ' '{print $13$12$11$10}'" % dexpath, log=False) , 16)
            return "Total : %d"%(total_count)
        except Exception as identifier:
            return "Calc dex method count error : %s"%(str(identifier))
        finally:
            self.clear_workspace()
    
    @output
    def dex_type_id_count(self):
        try:
            self.create_workspace()
            if is_dex(self.inApk):
                dexes = [self.inApk]
            elif is_zip(self.inApk):
                exec_command("unzip %s \"classes*.dex\" -d %s"%(self.inApk, self.workspace), doing=False)
                dexes = [os.path.join(self.workspace, item) for item in os.listdir(self.workspace) if item.endswith(".dex")]
            else :
                raise Exception("Not support file type")
            print("Calc type id count :")
            total_count = 0
            for dex in dexes :
                typeIds=    int(exec_command("hexdump -n 100 -C %s | grep 00000040 | awk -F ' ' '{print $5$4$3$2}'"%dex, status=False, doing=False), 16)
                print("%s : %d"%(os.path.basename(dex), typeIds))
                total_count += typeIds
                #methodsid = int(exec_command("hexdump -n 100 -C %s | grep 00000050 | awk -F ' ' '{print $13$12$11$10}'"%dex, status=False, doing=False), 16)
                #fieldsid = int(exec_command("hexdump -n 100 -C %s | grep 00000050 | awk -F ' ' '{print $5$4$3$2}'"%dexpath, log=False), 16)
                #stringids=  int(exec_command("hexdump -n 100 -C %s | grep 00000030 | awk -F ' ' '{print $13$12$11$10}'" % dexpath, log=False) , 16)
                #proto=      int(exec_command("hexdump -n 100 -C %s | grep 00000040 | awk -F ' ' '{print $13$12$11$10}'" % dexpath, log=False) , 16)
            return "Total : %d"%(total_count)
        except Exception as identifier:
            return "Calc dex method count error : %s"%(str(identifier))
        finally:
            self.clear_workspace()

    def apk_path_on_device(self):
        try:
            self.adbx.path(self.manifest.pkgname)
        except Exception as identifier:
            return "Get Apk install path error : %s"%(str(identifier))