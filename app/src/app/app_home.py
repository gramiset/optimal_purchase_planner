from flask import Blueprint, render_template, session, request
import logging
import src.util.util_log as util_log
import src.util.util_session as util_session

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)
app_home = Blueprint('app_home', __name__)


@app_home.route('/')
@app_home.route('/home')
def home():
    util_session.populate_session(request, session)
    return util_session.send_response(session, render_template('home.html'))
