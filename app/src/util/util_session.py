import logging

from flask import make_response
import src.util.util_log as util_log

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)


def set_user_values(request, session, user_id, first_name, is_valid_session):
    session['user_id'] = user_id
    session['first_name'] = first_name
    session['is_valid_session'] = is_valid_session


def set_value_in_session(request, session, key, value):
    session[key] = value


def get_value_from_session(request, session, key):
    if key in session:
        return session[key]
    else:
        return None


def is_valid_session(request, session):
    return 'is_valid_session' in session and session['is_valid_session'] == 'True'


def set_session_value_from_cooke(request, session, key):
    if key not in session or session[key] is None:
        if key in request.cookies and request.cookies.get(key) is not None:
            session[key] = request.cookies.get(key)


def set_cookie_value_from_session(response, session, key):
    if key in session and session[key] is not None:
        response.set_cookie(key, str(session[key]), max_age=600, expires=600)
    else:
        response.set_cookie(key, '', max_age=600, expires=600)


def populate_session(request, session):
    set_session_value_from_cooke(request, session, 'user_id')
    set_session_value_from_cooke(request, session, 'first_name')
    set_session_value_from_cooke(request, session, 'is_valid_session')
    set_session_value_from_cooke(request, session, 'file_id')


def clear_user_values(response, session):
    session['user_id'] = None
    session['first_name'] = None
    session['is_valid_session'] = None
    session['file_id'] = None
    response.set_cookie('user_id', '', max_age=600, expires=600)
    response.set_cookie('first_name', '', max_age=600, expires=600)
    response.set_cookie('is_valid_session', '', max_age=600, expires=600)
    response.set_cookie('file_id', '', max_age=600, expires=600)


def send_response(session, template):
    response = make_response(template)
    set_cookie_value_from_session(response, session, 'user_id')
    set_cookie_value_from_session(response, session, 'first_name')
    set_cookie_value_from_session(response, session, 'is_valid_session')
    set_cookie_value_from_session(response, session, 'file_id')
    return response


def send_logout_response(session, template):
    response = make_response(template)
    clear_user_values(response, session)
    return response

