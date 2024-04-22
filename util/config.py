import os, configparser
CONFIG = configparser.ConfigParser()
pathConfig = os.path.join('.','server','config','config.ini')
CONFIG.read(pathConfig)