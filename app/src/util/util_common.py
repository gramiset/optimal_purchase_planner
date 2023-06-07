from __future__ import print_function
from datetime import datetime
import re
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import random
import src.util.util_config as util_config
import src.util.util_db as util_db
import logging
import src.util.util_log as util_log

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)
config = util_config.get_config()
captcha_site_key = util_db.get_secret_value('CAPTCHA', 'site_key')
sib_email = util_db.get_secret_value('SENDINBLUE_EMAIL', 'email')
sib_api_key = util_db.get_secret_value('SENDINBLUE_EMAIL', 'api_key')


def get_ip_addr(request):
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_addr = request.environ['REMOTE_ADDR'].strip()
    else:
        ip_addr = request.environ['HTTP_X_FORWARDED_FOR'].strip()
    return ip_addr


def send_email_sib_api(subject, body, to):
    name = config.get('SENDINBLUE_EMAIL', 'name').strip()
    logger.info("SENDINBLUE_EMAIL: Name : " + name)
    logger.info("SENDINBLUE_EMAIL: Email : " + sib_email)
    sender = {"name": name, "email": sib_email}
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = sib_api_key
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, bcc=None, cc=None, reply_to=None, headers=None,
                                                   html_content=body, sender=sender, subject=subject)
    try:
        api_instance.send_transac_email(send_smtp_email)
        is_email_sent = True
    except ApiException as e:
        logger.info("Exception when calling SMTPApi->send_transac_email.", e)
        is_email_sent = False
    return is_email_sent


def send_otp_email(first_name, last_name, recipient_email, otp):
    subject = config.get('OTP_EMAIL', 'subject').strip()
    body = config.get('OTP_EMAIL', 'body').strip().replace("<FIRST_NAME>", first_name).replace("<OTP>", str(otp))
    to = [{"email": recipient_email, "name": first_name + " " + last_name}]
    logger.info("Email Subject : " + str(subject))
    logger.info("Email Body : " + str(body))
    logger.info("Email recipients : " + str(to))
    return send_email_sib_api(subject, body, to)


def generate_otp():
    return random.SystemRandom().randint(100000, 999999)


def parse_timestamp(timestamp):
    return datetime(*[int(x) for x in re.findall(r'\d+', timestamp)])


def is_last_logged_on_grt_30(timestamp):
    if timestamp is None:
        return False
    else:
        last_logged_on = parse_timestamp(str(timestamp))
        time_between = datetime.now() - last_logged_on
        if time_between.days > 30:
            return True
        else:
            return False


def is_previous_address(ip_addr, prv_ip_addr_arr):
    logger.info("ip_addr: " + str(ip_addr) + ", prv_ip_addr_arr: " + str(prv_ip_addr_arr))
    ip_arr = list()
    if ',' in ip_addr:
        for ip in ip_addr.split(','):
            ip_arr.append(ip.strip())
    else:
        ip_arr.append(ip_addr.strip())

    if prv_ip_addr_arr is not None:
        for prv_ip_arr in prv_ip_addr_arr:
            if set(ip_arr) == set(prv_ip_arr):
                return True
    return False


def is_ip_addr_update_require(ip_addr, prv_ip_addr_arr):
    logger.info("ip_addr: " + str(ip_addr) + ", prv_ip_addr_arr: " + str(prv_ip_addr_arr))

    ip_arr = list()
    if ',' in ip_addr:
        for ip in ip_addr.split(','):
            ip_arr.append(ip.strip())
    else:
        ip_arr.append(ip_addr.strip())

    if prv_ip_addr_arr is None:
        is_ip_addr_update_req = True
        updated_ip_addr_arr = [ip_arr]
    else:
        is_exist = False
        for prv_ip_arr in prv_ip_addr_arr:
            if set(ip_arr) == set(prv_ip_arr):
                is_exist = True
                break
        if is_exist:
            is_ip_addr_update_req = False
            updated_ip_addr_arr = prv_ip_addr_arr
        else:
            is_ip_addr_update_req = True
            if len(prv_ip_addr_arr) >= 5:
                updated_ip_addr_arr = prv_ip_addr_arr[-4:].append(ip_arr)
            else:
                updated_ip_addr_arr = prv_ip_addr_arr.append(ip_arr)
    logger.info(
        "is_ip_addr_update_req: " + str(is_ip_addr_update_req) + ", updated_ip_addr_arr: " + str(updated_ip_addr_arr))
    return is_ip_addr_update_req, updated_ip_addr_arr


def add_error(error, new_error):
    if error is None:
        error = new_error
    else:
        error = error + '<br>' + new_error
    return error
