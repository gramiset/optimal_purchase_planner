from flask import Flask, request
import os
import logging
import src.util.util_log as util_log
import src.processor.data_processor as data_processor

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def home():
    return 'I am running...'


@app.route('/file_process')
def process():
    try:
        file_db_id = request.args.get('id', default=None, type=str)
        return data_processor.process_files(file_db_id)
    except Exception as e:
        logger.error(e)
        return 'File Processing Failed.', 500


if __name__ == '__main__':
    logger.info("*********** File Processor Application Started *************")
    app.run()
