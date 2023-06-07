import psycopg2
import os
import src.util.util_config as util_config
import logging
import src.util.util_log as util_log

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)
config = util_config.get_config()


def create_postgres_conn():
    app_env = os.environ['APP_ENV']
    logger.info('APP_ENV Runtime Variable: ' + str(app_env))
    if app_env == 'gcp':
        return create_gcp_postgres_conn()
    else:
        return create_local_postgres_conn()


def create_local_postgres_conn():
    logger.info("Postgres Local Connection Creation started.")
    cursor = None
    try:
        host = config.get('POSTGRES', 'host').strip()
        logger.info("Postgres Host: " + str(host))
        port = config.get('POSTGRES', 'port').strip()
        logger.info("Postgres Port: " + str(port))
        database = config.get('POSTGRES', 'database').strip()
        logger.info("Postgres Database: " + str(database))
        user = os.environ['PGDB_USER']
        logger.info("Postgres User: " + str(user))
        password = os.environ['PGDB_PWD']
        # logger.info("Postgres Password: " + str(password))
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        logger.info("Postgres Connection: " + str(conn))
        # Creating a cursor object using the cursor() method
        cursor = conn.cursor()
        # Executing function using the execute() method
        cursor.execute("select version()")
        # Fetch a single row using fetchone() method.
        data = cursor.fetchone()
        logger.info("Connection established to: " + str(data))
        return conn
    except Exception as e:
        logger.error(e)
        return None
    finally:
        if cursor is not None:
            cursor.close()


def create_gcp_postgres_conn():
    logger.info("Postgres GCP Connection Creation started.")
    cursor = None
    try:
        user = os.environ['PGDB_USER']
        logger.info("Postgres User: " + str(user))
        password = os.environ['PGDB_PWD']
        # logger.info("Postgres Password: " + str(password))
        database = config.get('POSTGRES', 'database').strip()
        logger.info("Postgres Database: " + str(database))
        connection_name = config.get('POSTGRES', 'connection_name').strip()
        logger.info("Postgres connection_name: " + str(connection_name))
        unix_socket = '/cloudsql/{}'.format(connection_name)
        logger.info("Postgres unix_socket: " + str(unix_socket))
        conn = psycopg2.connect(database=database, user=user, password=password, host=unix_socket)
        logger.info("Postgres Connection: " + str(conn))
        # Creating a cursor object using the cursor() method
        cursor = conn.cursor()
        # Executing function using the execute() method
        cursor.execute("select version()")
        # Fetch a single row using fetchone() method.
        data = cursor.fetchone()
        logger.info("Connection established to: " + str(data))
        return conn
    except Exception as e:
        logger.error(e)
        return None
    finally:
        if cursor is not None:
            cursor.close()


def get_postgres_conn():
    return postgres_conn


postgres_conn = create_postgres_conn()


def get_secret_value(function, name):
    logger.info('Reading Secret Value: ' + str(function) + ', ' + str(name))
    query = """SELECT value from system_secrets WHERE function = %s and name = %s"""
    values = (function, name)
    value = None
    cur = None
    try:
        conn = get_postgres_conn()
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # Results
        row = cur.fetchone()
        if row is not None:
            value = row[0]
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
    finally:
        if cur is not None:
            cur.close()
    return value


def insert_user(first_name, last_name, email, dob, country, gender, password):
    logger.info('Inserting user : ' + str(email))
    query = """INSERT INTO USER_PROFILE (fname, lname, email, dob, country, gender, password) VALUES (%s, %s, %s, %s, 
    %s, %s, %s) RETURNING id;"""
    values = (first_name, last_name, email, dob, country, gender, password)
    user_id = None
    cur = None
    conn = get_postgres_conn()
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # get the generated id back
        user_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        count = cur.rowcount
        logger.info(count + " record inserted successfully into user_profile table. user_id = " + user_id)
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return user_id


def update_user(user_id, first_name, last_name, email, dob, country, gender):
    logger.info('Updating user details: ' + str(user_id))
    query = """UPDATE USER_PROFILE SET fname = %s, lname = %s, email = %s, dob = %s, country = %s, gender = %s, 
    updated_on = current_timestamp WHERE id = %s"""
    values = (first_name, last_name, email, dob, country, gender, user_id)
    conn = get_postgres_conn()
    cur = None
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # commit the changes to the database
        conn.commit()
        count = cur.rowcount
        logger.info(str(count) + " record updated successfully in user_profile table. user_id = " + str(user_id))
        is_success = True
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        is_success = False
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return is_success


def delete_user(user_id):
    logger.info("Deleting user details: " + str(user_id))
    query = """DELETE FROM USER_PROFILE WHERE id = %s"""
    values = (user_id,)
    conn = get_postgres_conn()
    cur = None
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # commit the changes to the database
        conn.commit()
        logger.info("User record delete successfully in user_profile table. user_id = " + str(user_id))
        is_success = True
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        is_success = False
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return is_success


def update_otp(user_id, otp):
    logger.info("Updating user OTP: " + str(user_id))
    query = """UPDATE USER_PROFILE SET otp = %s, is_verified = %s, updated_on = current_timestamp WHERE id = %s"""
    values = (otp, False, user_id)
    conn = get_postgres_conn()
    cur = None
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # commit the changes to the database
        conn.commit()
        count = cur.rowcount
        logger.info(str(count) + " OTP updated successfully in user_profile table. user_id = " + str(user_id))
        is_success = True
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        is_success = False
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return is_success


def make_user_verified(user_id, is_from_login, is_from_forgot_password, password, is_ip_addr_update_req,
                       updated_ip_addr_arr):
    logger.info("Updating user as verified: " + str(user_id))
    query = "UPDATE USER_PROFILE SET is_verified = %s, otp = NULL"
    if is_from_login:
        query = query + ", last_logged_on = current_timestamp, inc_login_att = 0"
    if is_from_forgot_password:
        query = query + ", password = %s"
    if is_ip_addr_update_req:
        query = query + ", ip_addr = %s"
    query = query + ", updated_on = current_timestamp WHERE id = %s"
    if is_ip_addr_update_req:
        if is_from_forgot_password:
            values = (True, password, updated_ip_addr_arr, user_id)
        else:
            values = (True, updated_ip_addr_arr, user_id)
    else:
        if is_from_forgot_password:
            values = (True, password, user_id)
        else:
            values = (True, user_id)
    conn = get_postgres_conn()
    cur = None
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # commit the changes to the database
        conn.commit()
        count = cur.rowcount
        logger.info(str(count) + " user verified updated successfully in user_profile table. user_id = " + str(user_id))
        is_success = True
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        is_success = False
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return is_success


def update_last_logged_on(user_id):
    logger.info("Updating last_logged_on for User: " + str(user_id))
    query = """UPDATE USER_PROFILE SET last_logged_on = current_timestamp, inc_login_att = 0, 
    updated_on = current_timestamp WHERE id = %s"""
    values = (user_id,)
    conn = get_postgres_conn()
    cur = None
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # commit the changes to the database
        conn.commit()
        count = cur.rowcount
        logger.info(str(count) + " user last_logged_on updated in user_profile table. user_id = " + str(user_id))
        is_success = True
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        is_success = False
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return is_success


def update_wrong_login_attempt(user_id, inc_login_att):
    logger.info("Updating inc_login_att for User: " + str(user_id))
    query = """UPDATE USER_PROFILE SET inc_login_att = %s, updated_on = current_timestamp WHERE id = %s"""
    values = (inc_login_att, user_id)
    conn = get_postgres_conn()
    cur = None
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # commit the changes to the database
        conn.commit()
        count = cur.rowcount
        logger.info(
            str(count) + " incremented inc_login_att successfully in user_profile table. user_id = " + str(user_id))
        is_success = True
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        is_success = False
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return is_success


def make_user_unverified(user_id):
    logger.info("Updating user as verified: " + str(user_id))
    query = "UPDATE USER_PROFILE SET is_verified = %s updated_on = current_timestamp WHERE id = %s"
    values = (False, user_id)
    conn = get_postgres_conn()
    cur = None
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # commit the changes to the database
        conn.commit()
        count = cur.rowcount
        logger.info(
            str(count) + " user unverified updated successfully in user_profile table. user_id = " + str(user_id))
        is_success = True
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        is_success = False
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return is_success


def update_password(user_id, password):
    logger.info("Updating Password for User: " + str(user_id))
    query = """UPDATE USER_PROFILE SET password = %s, updated_on = current_timestamp WHERE id = %s"""
    values = (password, user_id)
    conn = get_postgres_conn()
    cur = None
    try:
        conn = get_postgres_conn()
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # commit the changes to the database
        conn.commit()
        count = cur.rowcount
        logger.info(str(count) + " user password updated successfully in user_profile table. user_id = " + str(user_id))
        is_success = True
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        is_success = False
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return is_success


def get_user_from_email(email):
    logger.info("Getting User From Email: " + str(email))
    query = """SELECT id, email, fname, lname, dob, country, gender, password, is_verified, is_admin, otp, ip_addr, 
    last_logged_on, inc_login_att from USER_PROFILE WHERE email = %s"""
    values = (email,)
    cur = None
    try:
        conn = get_postgres_conn()
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # Results
        row = cur.fetchone()
        if row is not None:
            ret_val = (
                True, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                row[12], row[13])
        else:
            ret_val = (True, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        ret_val = (False, None, None, None, None, None, None, None, None, None, None, None, None, None)
    finally:
        if cur is not None:
            cur.close()
    return ret_val


def get_user_from_id(user_id):
    logger.info("Getting User From ID: " + str(user_id))
    query = """SELECT id, email, fname, lname, dob, country, gender, password, is_verified, is_admin, otp, ip_addr, 
    last_logged_on, inc_login_att from USER_PROFILE WHERE id = %s"""
    values = (user_id,)
    cur = None
    try:
        conn = get_postgres_conn()
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # Results
        row = cur.fetchone()
        if row is not None:
            ret_val = (
                True, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                row[12], row[13])
        else:
            ret_val = (True, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        ret_val = (False, None, None, None, None, None, None, None, None, None, None, None, None, None)
    finally:
        if cur is not None:
            cur.close()
    return ret_val


def insert_file(user_id, file_id, is_prod_info_avl, status):
    logger.info('Inserting File : ' + str(file_id))
    query = """INSERT INTO FILES (user_id, file_id, is_prod_info_avl, status) VALUES (%s, %s, %s, %s) RETURNING id;"""
    values = (user_id, file_id, is_prod_info_avl, status)
    file_db_id = None
    conn = get_postgres_conn()
    cur = None
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # get the generated id back
        file_db_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        count = cur.rowcount
        logger.info(str(count) + " record inserted successfully into FILES table. file_db_id = " + str(file_db_id))
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return file_db_id


def update_file_status(user_id, file_id, status):
    logger.info("Updating File Status: " + str(status) + " - user_id: " + str(user_id) + " - file_id: " + str(file_id))
    query = """UPDATE FILES SET status = %s, updated_on = current_timestamp WHERE user_id = %s and file_id=%s"""
    values = (status, user_id, file_id)
    conn = get_postgres_conn()
    cur = None
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # commit the changes to the database
        conn.commit()
        count = cur.rowcount
        logger.info(str(count) + " status updated successfully in FILES table. file_id = " + str(file_id))
        is_success = True
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        is_success = False
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return is_success


def get_file_from_id(user_id, file_id):
    logger.info("Getting file From file_id: " + str(file_id) + " - user_id: " + str(user_id))
    query = """SELECT id, is_prod_info_avl, status from FILES WHERE user_id = %s and file_id=%s"""
    values = (user_id, file_id)
    cur = None
    try:
        conn = get_postgres_conn()
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # Results
        row = cur.fetchone()
        if row is not None:
            ret_val = True, row[0], row[1], row[2]
        else:
            ret_val = True, None, None, None
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        ret_val = False, None, None, None
    finally:
        if cur is not None:
            cur.close()
    return ret_val


def get_user_files(user_id):
    logger.info("Getting user files: user_id: " + str(user_id))
    query = """SELECT id, file_id, is_prod_info_avl, status, created_on from FILES WHERE user_id = %s ORDER BY id DESC"""
    values = (user_id,)
    list()
    cur = None
    try:
        conn = get_postgres_conn()
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # Results
        files = cur.fetchall()
        logger.info("The number of files: " + str(cur.rowcount))
        if cur.rowcount > 0:
            ret_val = True, files
        else:
            ret_val = True, None
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        ret_val = False, None
    finally:
        if cur is not None:
            cur.close()
    return ret_val


def delete_file(user_id, file_id):
    logger.info("Deleting file details: user_id: " + str(user_id) + ", file_id: " + str(file_id))
    query = """DELETE FROM FILES WHERE user_id = %s and file_id = %s"""
    values = (user_id, file_id)
    conn = get_postgres_conn()
    cur = None
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, values)
        # commit the changes to the database
        conn.commit()
        logger.info(
            "File record delete successfully in File table. user_id: " + str(user_id) + ", file_id: " + str(file_id))
        # close communication with the database
        cur.close()
        is_success = True
    except (Exception, psycopg2.Error) as e:
        logger.error(e)
        is_success = False
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return is_success
