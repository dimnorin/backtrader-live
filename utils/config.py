import os
import utils.util as utils

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


config = configparser.ConfigParser()
config.read(os.path.join(utils.get_project_root(), 'config.ini'))

TELEGRAM = "Telegram"
BINANCE = "Binance"
CEREBRO = "Cerebro"


def get(section, option):
    return config.get(section, option)


def get_float(section, option):
    return float(get(section, option))
