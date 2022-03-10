import configparser

class UserConfigs:
    def __init__(self):
        parser = configparser.ConfigParser()
        parser.read('config.ini')

        self.dbname = parser['postgres']['dbname']
        self.user = parser['postgres']['user']
        self.password = parser['postgres']['password']
        self.host = parser['postgres']['host']
        self.port = parser['postgres']['port']
        self.file_loc = parser['cifp_file']['file_loc']
