from flask import Flask
from src.app.app_home import app_home
from src.app.app_user_profile import app_user_profile
from src.app.app_file_process import app_file_process
from src.app.app_data_explore import app_data_explore
from src.app.app_data_visualize import app_data_visualize
from src.app.app_data_stationary import app_data_stationary
from src.app.app_data_model_test import app_data_model_test
from src.app.app_product_demand import app_product_demand
import os
import logging
import src.util.util_log as util_log

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 3 * 1000 * 1000
app.register_blueprint(app_home)
app.register_blueprint(app_user_profile)
app.register_blueprint(app_file_process)
app.register_blueprint(app_data_explore)
app.register_blueprint(app_data_visualize)
app.register_blueprint(app_data_stationary)
app.register_blueprint(app_data_model_test)
app.register_blueprint(app_product_demand)


if __name__ == '__main__':
    logger.info("*********** Web Application Started *************")
    app.run()

