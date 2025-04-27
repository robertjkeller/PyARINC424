import configparser

class UserConfigs:
    def __init__(self):
        parser = configparser.ConfigParser()
        parser.read('config.ini')

        if not parser.has_section('postgres') and not parser.has_section('sqlite'):
            raise ValueError("No database configuration found in config.ini")

        if parser.has_section('postgres'):
            self.dbtype = 'postgres'
            self.dbname = parser['postgres']['dbname']
            self.user = parser['postgres']['user']
            self.password = parser['postgres']['password']
            self.host = parser['postgres']['host']
            self.port = parser['postgres']['port']

        if parser.has_section('sqlite'):
            self.dbtype = 'sqlite'
            self.dbname = parser['sqlite']['dbname']

        if not parser.has_section('cifp_file'):
            raise ValueError("No cifp_file configuration found in config.ini")

        self.file_loc = parser['cifp_file']['file_loc']