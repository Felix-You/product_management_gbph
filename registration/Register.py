# -*- coding: utf-8 -*-

import wmi, os
import base64
from pyDes import *
from registration import RegisterView
# from DataCenter import global_logger
from PyQt5.QtWidgets import QApplication
from registration import Encrypt
class Register:
    REGISTER_FILE_NAME = 'register.txt'
    # def __init__(self):
    # 获取硬件信息，输出macode
    # 1、CPU序列号（ID）  2、本地连接 无线局域网 以太网的MAC  3.硬盘序列号（唯一） 4.主板序列号（唯一）
    global s
    s = wmi.WMI()

    # cpu序列号
    def get_CPU_info(self):
        cpu = []
        cp = s.Win32_Processor()
        for u in cp:
            cpu.append(
                {
                    "Name": u.Name,
                    "Serial Number": u.ProcessorId,
                    "CoreNum": u.NumberOfCores
                }
            )
        return cpu

    # 硬盘序列号
    def get_disk_info(self):
        disk = []
        for pd in s.Win32_DiskDrive():
            disk.append(
                {
                    "Serial": s.Win32_PhysicalMedia()[0].SerialNumber.lstrip().rstrip(),  # 获取硬盘序列号，调用另外一个win32 API
                    "ID": pd.deviceid,
                    "Caption": pd.Caption,
                    "size": str(int(float(pd.Size) / 1024 / 1024 / 1024))
                }
            )
        return disk

    # mac地址（包括虚拟机的）
    def get_network_info(self):
        network = []
        for nw in s.Win32_NetworkAdapterConfiguration():
            if nw.MacAddress != None:
                network.append(
                    {
                        "MAC": nw.MacAddress,
                        "ip": nw.IPAddress
                    }
                )
        return network

    # 主板序列号
    def get_mainboard_info(self):
        mainboard = []
        for board_id in s.Win32_BaseBoard():
            mainboard.append(board_id.SerialNumber.strip().strip('.'))
        return mainboard

    # 由于机器码矿太长，故选取机器码字符串部分字符
    def getCombinNumber(self):
        a = self.get_network_info()
        b = self.get_CPU_info()
        c = self.get_disk_info()
        d = self.get_mainboard_info()
        macode = Encrypt.getCombinNumber(a, b, c, d)
        return macode

    # DES+base64加密
    def Encryted(self, tr):
        return Encrypt.Encryted(tr)

    # 获取注册码，验证成功后生成注册文件
    # def register(self, text:str)->bool:
    def getRegistration(self):
        ontent = self.getCombinNumber()
        ok = RegisterView.RegisterDialog.doRegistration(self,ontent, '592398057@qq.com')
        return ok

    def getKey(self):
        ontent = self.getCombinNumber()
        tent = bytes(ontent, encoding='utf-8')
        # 得到加密后机器码
        content = self.Encryted(tent)
        return content


    def register(self, key:str):

        # 由于输入类似“12”这种不符合base64规则的字符串会引起异常，所以需要增加输入判断
        if key:
            ontent = self.getCombinNumber()
            tent = bytes(ontent, encoding='utf-8')
            # 得到加密后机器码
            if Encrypt.checkKeyValid(tent, key):
                print("register succeed.")
                # 读写文件要加判断
                import FilePathInit
                working_dir = FilePathInit.workingDir.getWorkingDirectory()
                file_path = f'{working_dir}/{self.REGISTER_FILE_NAME}'
                with open(file_path, 'w') as f:
                    f.write(key)
                user_dir = FilePathInit.workingDir.getUserDirectory()
                file_path = f'{user_dir}/{self.REGISTER_FILE_NAME}'
                with open(file_path, 'w') as f:
                    f.write(key)
                return True
            else:
                return False
        else:
            return False

    # 打开程序先调用注册文件，比较注册文件中注册码与此时的硬件信息编码后是否一致
    def checkAuthored(self):
        ontent = self.getCombinNumber()
        tent = bytes(ontent, encoding='utf-8')
        # 获得加密后的机器码
        # 读写文件要加判断
        import FilePathInit
        key_found = []

        user_dir = FilePathInit.workingDir.getUserDirectory()
        if user_dir:
            reg_file_path = os.path.join(user_dir,self.REGISTER_FILE_NAME)
            if os.path.exists(reg_file_path):
                with open(reg_file_path) as f:
                    key = f.read()
                    key_found.append(key)
        if os.path.exists(self.REGISTER_FILE_NAME):
            with open(self.REGISTER_FILE_NAME, 'r',encoding='utf-8') as f:
                key = f.read()
                key_found.append(key)

        if not key_found:
            return self.getRegistration()

        for key in key_found:
            if Encrypt.checkKeyValid(tent, key):
                return True
        else:
            return self.getRegistration()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    register = Register()
    ok = register.checkAuthored()
    print(ok)
    sys.exit(app.exec_())