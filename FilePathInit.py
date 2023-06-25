import configparser
import os,shutil,sys
import win32con, win32api


def get_desktop():
    key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
                              r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders', 0,
                              win32con.KEY_READ)
    return win32api.RegQueryValueEx(key, 'Desktop')[0]

class WorkingDir():
    '''查验用户文件目录'''
    _instance = None
    file_folder = 'files'
    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        return super(WorkingDir, cls).__new__(cls)

    def __init__(self, appointed_user_data_directory: str=None):
        self.appointed_user_data_directory = appointed_user_data_directory
        self.conf = configparser.ConfigParser()

        self.curpath = self.getWorkingDirectory()   # 当前文件路径
        self.ini_file = os.path.join(self.curpath, "filepath.ini")
        self.userpath = None
        self.conf.read(self.ini_file, encoding="GBK")

    def getWorkingDirectory(self):
        return os.environ['working_path']

    def hasUserDirectory(self):
        if self.conf.has_section('user_dir'):
            if not self.conf.has_option('user_dir','dir'):
                return False
            path = self.conf.get('user_dir', 'dir')
            if not os.path.exists(path):
                return False
            return True

        else:
            return False

    def createUserDirctory(self, path:str):
        '''创建用户设置的目录，并且修改配置文件'''
        path=path.strip()
        path=path.rstrip("\\")
        #创建新的目录
        if not os.path.exists(path):
            os.makedirs(path)
        #在原始路径文件中写入用户路径
        if not self.conf.has_section('user_dir'):
            self.conf.add_section('user_dir')

        self.conf.set('user_dir', 'dir', path)
        with open(self.ini_file,mode='w',encoding="GBK") as f:
            self.conf.write(f)

    def getUserDirectory(self):
        if not self.conf.has_section('user_dir'):
            return None
        if not self.conf.has_option('user_dir', 'dir'):
            return None
        path = self.conf.get('user_dir', 'dir')
        if not os.path.exists(path):
            return None
        return path

    def initUserFiles(self):
        '''将配置文件和数据库文件复制到用户文件夹，并且修改当前路径的配置文件'''
        target = self.getUserDirectory()
        working_dir = self.getWorkingDirectory()
        source = os.path.join(working_dir, 'initFiles')
        if target and not os.path.exists(target):
            os.makedirs(target)
        for root, dirs, files in os.walk(source):
            for file in files:
                tgt_file = os.path.join(target, file)
                if os.path.exists(tgt_file):#若文件已存在，则忽略
                    continue
                src_file = os.path.join(root, file)
                shutil.copy(src_file, target)
                print(src_file)

workingDir = WorkingDir()

class UserDir():
    '''An instance of user directory.  '''
    _instance = None
    file_folder = 'files'

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        return super(UserDir, cls).__new__(cls)

    def __init__(self, appointed_user_data_directory: str = None):
        self.appointed_user_data_directory = appointed_user_data_directory
        self.conf = configparser.ConfigParser()
        self.ini_file = None
        if self.appointed_user_data_directory and os.path.exists(self.appointed_user_data_directory):
            self.userpath = self.appointed_user_data_directory
        else:
            self.userpath = workingDir.getUserDirectory()

        if self.userpath:
            self.ini_file = os.path.join(self.userpath, "filepath.ini")
            self.conf.read(self.ini_file, encoding="GBK")

    def reloadDir(self, appointed_user_data_directory:str = None):
        self.userpath = workingDir.getUserDirectory()
        if appointed_user_data_directory == self.userpath:
            return
        if appointed_user_data_directory:
            self.userpath = appointed_user_data_directory
        else:
            pass
        self.ini_file = os.path.join(self.userpath, "filepath.ini")
        self.conf.read(self.ini_file, encoding="GBK")

    def getUserFileDirectory(self):
        return f'{self.userpath}/{self.file_folder}'

    def checkDatabase(self):
        '''数据库文件是否存在'''
        data_base_file = self.getDatabase()
        if data_base_file:
                return True
        else:
            return False

    def getDatabase(self):
        data_base_file_name = self.conf.get('user_dir', 'database_name')
        data_base_file = os.path.join(self.userpath, data_base_file_name)
        if os.path.exists(data_base_file):
            if os.path.isfile(data_base_file):
                return (data_base_file)
        else:
            return None

    def getDrugDataBase(self):
        drug_data_base_file_name = self.conf.get('user_dir', 'database_name')
        drug_data_base_file = os.path.join(self.userpath, drug_data_base_file_name)
        if os.path.exists(drug_data_base_file):
            if os.path.isfile(drug_data_base_file):
                return (drug_data_base_file)
        else:
            return None

    def getUserTheme(self):
        return (self.conf.get('memory', 'theme'))

    def saveUserTheme(self, theme):
        self.conf.set('memory', 'theme', theme)
        with open(self.ini_file, 'w') as f:
            self.conf.write(f)

    def get_last_open(self):
        return (self.conf.get('memory', 'lastopen'))

    def save_last_open(self, path):
        self.conf.set('memory', 'lastopen', path)
        with open(self.ini_file, 'w') as f:
            self.conf.write(f)

    def get_last_save(self):
        return (self.conf.get('memory', 'lastsave'))

    def save_last_save(self, path):
        self.conf.set('memory', 'lastsave', path)
        with open(self.ini_file, 'w') as f:
            self.conf.write(f)

userDir = UserDir()


def changeUserDir(user_dir:str):
    workingDir.conf.set('user_dir', 'dir', user_dir)
    with open(workingDir.ini_file, mode='w', encoding="GBK") as f:
        workingDir.conf.write(f)
    workingDir.createUserDirctory(user_dir)
    workingDir.initUserFiles()
    userDir.reloadDir()
    import ConnSqlite
    ConnSqlite.initDatabase()


if __name__ == '__main__':
    desktop = get_desktop()
    print(desktop)