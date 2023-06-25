#这个模块不用在最终的程序中
#
import pandas as pd
from pandas import DataFrame
import json

def makeProvince(data:DataFrame):
    dictProvince  = {}
    dictCity = {}
    dictTown = {}
    for i in range(data.shape[0]):
        code = data.iloc[i][0]
        if code % 10000 == 0:
            dictProvince[code//10000] = data.iloc[i][1]
            dictCity[code//10000] = {}
        elif code % 100 == 0:
            if code // 10000 in dictTown.keys() == False:
                dictTown[code // 10000] = {}
            dictCity[code // 10000][code//100] = data.iloc[i][1]
            dictTown[code // 100] = {}
        else :
            if not code // 100 in dictTown.keys():
                dictTown[code // 100] = {}
            dictTown[code // 100][code] = data.iloc[i][1]
    #json.dump(dictProvince)
    print(dictProvince)
    print(dictCity)
    print(dictTown)

if __name__ == '__main__':
    data = pd.read_excel('E:\\SourceCodes\\product_management_web\\migrate_by_hand\\P020210406391660415696.xls')
    makeProvince(data)

