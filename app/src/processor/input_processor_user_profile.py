import src.util.util_common as util_common
import src.util.util_db as util_db
import json
import urllib.request
import bcrypt
import logging
import src.util.util_log as util_log
import src.util.util_session as util_session

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)

captcha_secret_key = util_db.get_secret_value('CAPTCHA', 'secret_key')
captcha_error_message = 'CAPTCHA Response Error'


def process_signup_input(session, request):
    error = None
    response = request.form.get('g-recaptcha-response')
    if not check_recaptcha(response):
        error = util_common.add_error(error, captcha_error_message)
    else:
        email = request.form['email'].strip()
        user_tuple = util_db.get_user_from_email(email)
        # id, email, fname, lname, dob, country, gender, password, is_verified, is_admin, otp, ip_addr,
        # last_logged_on, inc_login_att
        if user_tuple[0]:
            if user_tuple[1] is None:
                first_name = request.form['fname'].strip()
                last_name = request.form['lname'].strip()
                dob = request.form['dob'].strip()
                country = request.form['country']
                gender = request.form['gender'][0:1]
                password = request.form['pwd'].strip().encode('utf-8')
                hash_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
                user_id = util_db.insert_user(first_name, last_name, email, dob, country, gender, hash_password)
                if user_id is not None:
                    otp = util_common.generate_otp()
                    if util_common.send_otp_email(first_name, last_name, email, otp) \
                            and util_db.update_otp(user_id, otp):
                        util_session.set_user_values(request, session, user_id, first_name, 'False')
                    else:
                        error = util_common.add_error(error, 'OTP sending failed. Please try again later.')
                        util_db.delete_user(user_id)
                else:
                    error = util_common.add_error(error, 'User Registration failed. Please try again later.')
            else:
                error = util_common.add_error(error,
                                              'Email already exist. If you already registered, please use login.')
        else:
            error = util_common.add_error(error, 'User Registration failed. Please try again later.')
    logger.error("SignUp Form Error: " + str(error))
    return error


def process_otp_input(session, request, referrer_action):
    next_template_html = None
    password = None
    error = None
    user_id = util_session.get_value_from_session(request, session, 'user_id')
    if user_id is not None:
        user_tuple = util_db.get_user_from_id(user_id)
        # id, email, fname, lname, dob, country, gender, password, is_verified, is_admin, otp, ip_addr,
        # last_logged_on, inc_login_att
        if user_tuple[0]:
            if user_tuple[11] is not None:
                if request.form['otp'] == user_tuple[11]:
                    ip_addr = util_common.get_ip_addr(request)
                    prv_ip_addr_arr = user_tuple[12]
                    is_ip_addr_update_req, updated_ip_addr_arr = util_common.is_ip_addr_update_require(ip_addr,
                                                                                                       prv_ip_addr_arr)
                    is_from_forgot_password = False
                    if referrer_action.lower() in ['signup', 'forgot_password']:
                        if referrer_action.lower() == 'forgot_password':
                            is_from_forgot_password = True
                            password = request.form['pwd'].strip()
                        if util_db.make_user_verified(user_id, False, is_from_forgot_password, password,
                                                      is_ip_addr_update_req, updated_ip_addr_arr):
                            util_session.set_user_values(request, session, None, None, 'False')
                            next_template_html = 'login.html'
                        else:
                            error = util_common.add_error(error, 'OTP verification failed. Please try again later.')
                    else:
                        if util_db.make_user_verified(user_id, True, False, None, is_ip_addr_update_req,
                                                      updated_ip_addr_arr):
                            util_session.set_value_in_session(request, session, 'is_valid_session', 'True')
                            next_template_html = 'show_files'
                        else:
                            error = util_common.add_error(error, 'OTP verification failed. Please try again later.')
                else:
                    error = util_common.add_error(error, 'Incorrect OTP. Please check email and re-enter correct OTP.')
            else:
                error = util_common.add_error(error, 'OTP verification failed. Please try again later.')
        else:
            error = util_common.add_error(error, 'OTP verification failed. Please try again later.')
    else:
        error = util_common.add_error(error,
                                      'OTP verification failed. Please come through signup, login ot forgot password to '
                                      'validate OTP.')
    logger.error("OTP Form Error: " + str(error))
    logger.info("next_template_html: " + str(next_template_html))
    return error, next_template_html, password


def process_login_input(session, request):
    error = None
    is_otp_check = False
    otp_info_message = None
    response = request.form.get('g-recaptcha-response')
    if not check_recaptcha(response):
        error = util_common.add_error(error, captcha_error_message)
    else:
        email = request.form['email'].strip()
        user_tuple = util_db.get_user_from_email(email)
        # id, email, fname, lname, dob, country, gender, password, is_verified, is_admin, otp, ip_addr,
        # last_logged_on, inc_login_att
        logger.info("Data Query is success ?: " + str(user_tuple[0]))
        if user_tuple[0]:
            logger.info("User ID ?: " + str(user_tuple[1]))
            if user_tuple[1] is not None:
                password = request.form['pwd'].strip().encode('utf-8')
                password_check = bcrypt.checkpw(password, user_tuple[8].encode('utf-8'))
                logger.info("password_check: " + str(password_check))
                if password_check:
                    util_session.set_user_values(request, session, user_tuple[1], user_tuple[3], 'False')
                    logger.info("User ID: " + str(user_tuple[1]))
                    logger.info("First Name: " + str(user_tuple[3]))
                    logger.info("Last Name: " + str(user_tuple[4]))
                    logger.info("Is User Already Verified: " + str(user_tuple[9]))
                    logger.info("Last Login IP Addresses: " + str(user_tuple[12]))
                    logger.info("Last Logon Time: " + str(user_tuple[13]))
                    ip_addr = util_common.get_ip_addr(request)
                    logger.info("Current IP Address: " + str(ip_addr))
                    if not user_tuple[9]:
                        is_otp_check = True
                        otp_info_message = 'OTP sent to email. Please enter OTP to verify.'
                    elif not util_common.is_previous_address(ip_addr, user_tuple[12]):
                        is_otp_check = True
                        otp_info_message = 'New IP Address if compare with last 5. OTP sent to email. ' \
                                           'Please enter OTP to verify.'
                    elif util_common.is_last_logged_on_grt_30(user_tuple[13]):
                        is_otp_check = True
                        otp_info_message = 'Not logged in last 30 days. OTP sent to email. Please enter OTP to verify.'
                    if not is_otp_check:
                        if util_db.update_last_logged_on(user_tuple[1]):
                            util_session.set_value_in_session(request, session, 'is_valid_session', 'True')
                        else:
                            util_session.set_user_values(request, session, None, None, 'False')
                            error = util_common.add_error(error, 'Login failed. Please try again later.')
                    else:
                        otp = util_common.generate_otp()
                        if util_common.send_otp_email(user_tuple[3], user_tuple[4], email, otp) \
                                and util_db.update_otp(user_tuple[1], otp):
                            util_session.set_value_in_session(request, session, 'is_valid_session', 'False')
                        else:
                            error = util_common.add_error(error, 'OTP sending failed. Please try again later.')
                else:
                    error_message = 'Incorrect password. '
                    logger.info("Incorrect Login Attempts: " + str(user_tuple[14]))
                    incorrect_login_attempt = user_tuple[14] + 1
                    util_db.update_wrong_login_attempt(user_tuple[1], incorrect_login_attempt)
                    error_message = error_message + str(incorrect_login_attempt) + " wrong attempt(s). "
                    if incorrect_login_attempt >= 5:
                        util_db.make_user_unverified(user_tuple[1])
                        error_message = error_message + 'Account inactivated due to several wrong attempts. Please ' \
                                                        'use forgot password to reset password.'
                    else:
                        error_message = error_message + 'Account will be inactivated after 5 wrong attempts.'
                    error = util_common.add_error(error, error_message)
            else:
                error = util_common.add_error(error, 'Email not exist. Please use signup.')
        else:
            error = util_common.add_error(error, 'Login failed. Please try again later.')
    logger.error("Login Form Error: " + str(error))
    logger.info("is_otp_check: " + str(is_otp_check))
    logger.info("otp_info_message: " + str(otp_info_message))
    return error, is_otp_check, otp_info_message


def process_forgot_password_input(session, request):
    error = None
    hash_password = None
    response = request.form.get('g-recaptcha-response')
    if not check_recaptcha(response):
        error = util_common.add_error(error, captcha_error_message)
    else:
        email = request.form['email'].strip()
        user_tuple = util_db.get_user_from_email(email)
        # id, email, fname, lname, dob, country, gender, password, is_verified, is_admin, otp, ip_addr,
        # last_logged_on, inc_login_att
        logger.info("Data Query is success ? " + str(user_tuple[0]))
        if user_tuple[0]:
            logger.info("User ID ?: " + str(user_tuple[1]))
            if user_tuple[1] is not None:
                util_session.set_user_values(request, session, user_tuple[1], user_tuple[3], 'False')
                otp = util_common.generate_otp()
                if util_common.send_otp_email(user_tuple[3], user_tuple[4], email, otp) \
                        and util_db.update_otp(user_tuple[1], otp):
                    password = request.form['pwd'].strip().encode('utf-8')
                    hash_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
                else:
                    error = util_common.add_error(error, 'OTP sending failed. Please try again later.')
            else:
                error = util_common.add_error(error, 'Email not exist. Please use signup.')
        else:
            error = util_common.add_error(error, 'Failed. Please try again later.')
    logger.info("Forgot Password Error: " + str(error))
    return error, hash_password


def process_update_profile_input(session, request):
    error = None
    email = request.form['email'].strip()
    first_name = request.form['fname'].strip()
    last_name = request.form['lname'].strip()
    dob = request.form['dob'].strip()
    country = request.form['country']
    gender = request.form['gender'][0:1]
    user_id = util_session.get_value_from_session(request, session, 'user_id')
    if util_db.update_user(user_id, first_name, last_name, email, dob, country, gender):
        util_session.set_value_in_session(request, session, 'first_name', first_name)
    else:
        error = util_common.add_error(error, 'Profile update failed. Please try again later.')
    logger.info("Update Profile Form Error: " + str(error))
    return error


def process_change_password_input(session, request):
    error = None
    user_id = util_session.get_value_from_session(request, session, 'user_id')
    user_tuple = util_db.get_user_from_id(user_id)
    # id, email, fname, lname, dob, country, gender, password, is_verified, is_admin, otp, ip_addr,
    # last_logged_on, inc_login_att
    old_password = request.form['opwd'].strip().encode('utf-8')
    password_check = bcrypt.checkpw(old_password, user_tuple[8].encode('utf-8'))
    logger.info("password_check: " + str(password_check))
    if password_check:
        new_password = request.form['pwd'].strip().encode('utf-8')
        hash_password = bcrypt.hashpw(new_password, bcrypt.gensalt()).decode('utf-8')
        if not util_db.update_password(user_id, hash_password):
            error = util_common.add_error(error, 'Change password failed. Please try again later.')
    else:
        error = util_common.add_error(error, 'Incorrect old password.')
    logger.info("Change Password Form Error: " + str(error))
    return error


def check_recaptcha(response):
    url = 'https://www.google.com/recaptcha/api/siteverify?'
    url = url + 'secret=' + str(captcha_secret_key)
    url = url + '&response=' + str(response)
    jsonobj = json.loads(urllib.request.urlopen(url).read())
    return jsonobj['success']


def get_previous_referrer_action(request):
    logger.info("Previous Referrer Page: " + str(request.referrer))
    referrer_action = None
    if request.referrer is not None:
        referrer_action = request.referrer.rsplit('/', 1)[-1]
        if '?' in referrer_action:
            referrer_action = referrer_action.split('?')[0].strip()
    logger.info("Previous Referrer Action: " + str(referrer_action))
    return referrer_action
