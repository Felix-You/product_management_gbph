import time


class Snow(object):#雪花算法

    def __init__(self, idx=None):
        init_date = time.strptime('2010-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
        self.start = int(time.mktime(init_date))
        self.last = int(time.time())
        self.count_id = 0
        self.idx = idx if idx else 'ig'

    def get(self, type_code:str = None):
        '''

        :param type_code: use type_code in place of idx
        :return:
        '''
        if type_code:
            self.idx = type_code
        now = int(time.time())
        temp = now - self.start # 初始化秒数字符串
        # print(temp)
        if len(str(temp)) < 9:
            length = len(str(temp))
            s = '0' * (9 - length)
            temp = s + str(temp)
        # 检查是否在还在当前一秒钟以内，过秒则从0开始计数（此时temp已更新）
        if now == self.last:
            self.count_id += 1
        else:
            self.count_id = 0
            self.last = now

        if len(str(self.idx)) < 2:
            length = len(str(self.idx))
            s = '0' * (2 - length)
            self.idx = str(self.idx) + s

        if self.count_id == 999:# 计数器已经达到2位，temp还未更新
            time.sleep(1)

        count_id_data = str(self.count_id)
        if len(count_id_data) < 3:
            length = len(count_id_data)
            s = '0' * (3 - length)
            count_id_data = s + count_id_data
        return ''.join([str(self.idx), str(temp), count_id_data])

    def typeGetID(self, tpye_code:str):
        return self.get(tpye_code)
#snow = Snow('096')
#print(snow.get())
ID_Generator = Snow()
if __name__ == '__main__':
    import threading

    snow = Snow('001')
    # print(snow.get())

    # def echo():
    #     print(snow.get())
    #
    #
    # threads = [threading.Thread(target=echo) for i in range(100)]
    # for t in threads:
    #     t.start()
    # for t in threads:
    #     t.join()

