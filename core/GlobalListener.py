from dataclasses import dataclass
import logging, os
@dataclass(frozen=True)
class KEY_MOUSE_EVENT:
    MOUSE_LEFT_PRESS = 1
    MOUSE_LEFT_RELEASE = 2
    MOUSE_RIGHT_PRESS = 3
    MOUSE_RIGHT_RELEASE = 4
    KEY_CONTROL_PRESS = 5
    KEY_CONTROL_RELEASE = 6
    KEY_ESCAPE_PRESS = 7
    KEY_ANY_PRESS = 8


class GlobalKeyMouseListener:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance:
           return cls._instance
        else:
            return super(GlobalKeyMouseListener, cls).__new__(cls)

    def __init__(self):
        self.observers = []

    def addObserver(self, obj):
        if obj not in self.observers:
            self.observers.append(obj)

    def removeObserver(self, obj):
        if obj in self.observers:
            self.observers.remove(obj)

    def accept(self, event):
        self.notify(event)

    def notify(self, event):
        for obs in self.observers:
            obs.AcceptMouseKeyEvent(event)
        pass


global_key_mouse_listener = GlobalKeyMouseListener()

def getLogger():
    logger = logging.getLogger('test')
    logger.setLevel(level=logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    from logging import handlers
    path = os.environ['working_path']
    log_file = os.path.join(path,'log/rotating_test.log')
    time_rotating_file_handler = handlers.TimedRotatingFileHandler(filename=log_file, when='W0')
    time_rotating_file_handler.setLevel(logging.INFO)
    time_rotating_file_handler.setFormatter(formatter)

    logger.addHandler(time_rotating_file_handler)
    # logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

global_logger = getLogger()
