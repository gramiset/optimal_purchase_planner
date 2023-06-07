import configparser
import os
import logging
import src.util.util_log as util_log

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)
config = configparser.ConfigParser()


def read_config():
    app_env = os.environ['APP_ENV']
    logger.info('APP_ENV Runtime Variable: ' + str(app_env))
    config.read('config/common.config')
    config.read('config/' + app_env + '.config')
    app_env_name = config.get('APP', 'APP_ENV').strip()
    logger.info('APP.APP_ENV from config_file_data: ' + str(app_env_name))
    return config


def get_config():
    if len(config.sections()) == 0:
        logger.info("Config is Empty. Reading config file.")
        return read_config()
    else:
        return config
