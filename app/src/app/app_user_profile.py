from flask import Blueprint, render_template, request, session
import src.processor.input_processor_user_profile as input_processor_user_profile
import src.util.util_db as util_db
import src.util.util_common as util_common
import logging
import src.util.util_log as util_log
import src.util.util_session as util_session
import src.app.app_file_process as app_file_process

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)

app_user_profile = Blueprint('app_user_profile', __name__)


@app_user_profile.route("/signup", methods=['GET', 'POST'])
def signup():
    util_session.populate_session(request, session)
    if util_session.is_valid_session(request, session):
        return util_session.send_response(session, render_template("home.html"))
    else:
        if request.method == 'POST':
            error = input_processor_user_profile.process_signup_input(session, request)
            if error is None:
                return util_session.send_response(session, render_template("validate_otp.html",
                                                                           info_message='OTP sent to email. Please enter OTP to activate '
                                                    'your profile.'))
            else:
                return util_session.send_response(session, render_template("signup.html", captcha_site_key=util_common.captcha_site_key, error=error,
                                                                           fname=request.form['fname'], lname=request.form['lname'],
                                                                           email=request.form['email'], dob=request.form['dob'],
                                                                           country=request.form['country'], gender=request.form['gender']))
        else:
            return util_session.send_response(session, render_template("signup.html", captcha_site_key=util_common.captcha_site_key))


@app_user_profile.route('/validate_otp', methods=['GET', 'POST'])
def validate_otp():
    util_session.populate_session(request, session)
    if util_session.is_valid_session(request, session):
        return util_session.send_response(session, render_template("home.html"))
    else:
        referrer_action = input_processor_user_profile.get_previous_referrer_action(request)
        if referrer_action.lower() in ['signup', 'login', 'forgot_password']:
            if request.method == 'POST':
                error, next_template_html, password = input_processor_user_profile.process_otp_input(session, request, referrer_action)
                if error is None:
                    if next_template_html == 'show_files':
                        return app_file_process.render_show_files('')
                    else:
                        return util_session.send_response(session, render_template(next_template_html, captcha_site_key=util_common.captcha_site_key))
                else:
                    return util_session.send_response(session, render_template("validate_otp.html", error=error, password=password))
            else:
                return util_session.send_response(session, render_template("validate_otp.html"))
        else:
            return util_session.send_response(session, render_template("validate_otp.html",
                                                                       error="OTP validation should invoke from signup, login or forgot password."))


@app_user_profile.route('/login', methods=['GET', 'POST'])
def login():
    util_session.populate_session(request, session)
    if util_session.is_valid_session(request, session):
        return util_session.send_response(session, render_template("home.html"))
    else:
        if request.method == 'POST':
            error, is_otp_check, otp_info_message = input_processor_user_profile.process_login_input(session, request)
            if error is None:
                if is_otp_check:
                    return util_session.send_response(session, render_template("validate_otp.html", info_message=otp_info_message))
                else:
                    return app_file_process.render_show_files('')
            else:
                return util_session.send_response(session, render_template("login.html", captcha_site_key=util_common.captcha_site_key, error=error,
                                                                           email=request.form['email']))
        else:
            return util_session.send_response(session, render_template("login.html", captcha_site_key=util_common.captcha_site_key))


@app_user_profile.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    util_session.populate_session(request, session)
    if util_session.is_valid_session(request, session):
        return util_session.send_response(session, render_template("home.html"))
    else:
        if request.method == 'POST':
            error, password = input_processor_user_profile.process_forgot_password_input(session, request)
            if error is None:
                return util_session.send_response(session, render_template("validate_otp.html",
                                                                           info_message='OTP sent to email. Please enter OTP to update '
                                                    'the password.', password=password))
            else:
                return util_session.send_response(session, render_template("forgot_password.html", captcha_site_key=util_common.captcha_site_key, error=error,
                                                                           email=request.form['email']))
        else:
            return util_session.send_response(session, render_template("forgot_password.html", captcha_site_key=util_common.captcha_site_key))


@app_user_profile.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    util_session.populate_session(request, session)
    if not util_session.is_valid_session(request, session):
        return util_session.send_response(session, render_template("login.html"))
    else:
        user_id = util_session.get_value_from_session(request, session, 'user_id')
        user_tuple = util_db.get_user_from_id(user_id)
        # id, email, fname, lname, dob, country, gender, password, is_verified, is_admin, otp, ip_addr,
        # last_logged_on, inc_login_att
        if request.method == 'POST':
            error = input_processor_user_profile.process_update_profile_input(session, request)
            if error is None:
                return util_session.send_response(session, render_template("home.html"))
            else:
                return util_session.send_response(session, render_template("update_profile.html", error=error, fname=request.form['fname'],
                                                                           lname=request.form['lname'], email=request.form['email'],
                                                                           dob=request.form['dob'], country=request.form['country'],
                                                                           gender=request.form['gender']))
        else:
            return util_session.send_response(session, render_template("update_profile.html", fname=user_tuple[3], lname=user_tuple[4],
                                                                       email=user_tuple[2], dob=user_tuple[5], country=user_tuple[6], gender=user_tuple[7]))


@app_user_profile.route('/change_password', methods=['GET', 'POST'])
def change_password():
    util_session.populate_session(request, session)
    if not util_session.is_valid_session(request, session):
        return util_session.send_response(session, render_template("login.html"))
    else:
        if request.method == 'POST':
            error = input_processor_user_profile.process_change_password_input(session, request)
            if error is None:
                return util_session.send_response(session, render_template("home.html"))
            else:
                return util_session.send_response(session, render_template("change_password.html", error=error))
        else:
            return util_session.send_response(session, render_template("change_password.html"))


@app_user_profile.route('/logout')
def logout():
    util_session.populate_session(request, session)
    return util_session.send_logout_response(session, render_template("home.html"))
