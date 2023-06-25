from PIL import ImageColor
import win32api

DF_Width = win32api.GetSystemMetrics(0)
DF_Length =  win32api.GetSystemMetrics(1)
# DF_Ratio = DF_Width/1600 # 开发时使用的屏幕分辨率为1600*900

class ProjectRGBColour:
    ProjectInAct = (210, 220, 220)
    ProjectOrderTobe  = (250, 210, 190)
    ProjectClearChance = (240, 230, 190)
    ProjectHighlight = (255, 255, 150)
    ProjectToVisit = (125, 180, 140)
    ProjecIsDeal = (125, 180, 230)

class TaskColour:
    TaskIsCritial = (255, 163, 112)
    TaskToDo = (130, 150, 230)

class AlphaChannelFactory:
    obj = None

    def __new__(cls, *args, **kwargs):
        if cls.obj:
            return cls.obj
        else:
            cls.obj =  super.__new__(cls, *args, **kwargs)

    def __init__(self, alpha):
        self.alpha = alpha

    def getAlphaColor(self,rgb_color:tuple):
        r,g,b = rgb_color
        return tuple((r,g,b,self.alpha))
def getAlphaColor(rgb_color:tuple, alpha):
    r,g,b = rgb_color
    return tuple((r,g,b,alpha))

def RGB_to_Hex(rgb):
    # 将RGB格式划分开来
    color = '#'
    for i in rgb:
        num = int(i)
        # 将R、G、B分别转化为16进制拼接转换并大写  hex() 函数用于将10进制整数转换成16进制，以字符串形式表示
        color += str(hex(num))[-2:].replace('x', '0').upper()
    print(color)
