import base64

# import cimport as cimport
from pyDes import des, CBC, PAD_PKCS5
# cimport cython
Des_key = "felixyou"  # Key,需八位
Des_IV = "\x11\2\x2a\3\1\x27\2\2"  # 自定IV向量


def getCombinNumber( a, b, c, d ):
    # a = self.get_network_info()
    # b = self.get_CPU_info()
    # c = self.get_disk_info()
    # d = self.get_mainboard_info()
    machinecode_str = ""
    machinecode_str = machinecode_str + a[0]['MAC'] + b[0]['Serial Number'] + c[0]['Serial'] + d[0]
    # return machinecode_str
    selectIndex = [4, 10, 15, 16, 17, 22, 11,30, 32, 38, 43, 46, 50, 52, 54, 57, 60, 62]
    macode = ""
    for i in selectIndex:
        macode = macode + machinecode_str[i]
    return macode

def get_the_Encryted( tr):
    k = des(Des_key, CBC, Des_IV, pad=None, padmode=PAD_PKCS5)
    EncryptStr = k.encrypt(tr)
    # print(EncryptStr)
    return base64.b32encode(EncryptStr)  # 转base64编码返回


def checkKeyValid(tr, key):
    EncryptStr = get_the_Encryted(tr)
    if bytes(key, encoding='utf-8') == EncryptStr:
        return True
    else:
        return False


if __name__ == '__main__':
    content = input('input your machine code:')
    print(get_the_Encryted(content))