import psycopg2
from psycopg2 import pool
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


def update_file_status(file_db_id, status):
    logger.info("Updating File Status: file_db_id: " + str(file_db_id))
    query = """UPDATE FILES SET status = %s, updated_on = current_timestamp WHERE id=%s"""
    values = (status, file_db_id, )
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
        logger.info(str(count) + " status updated successfully in FILES table. file_db_id: " + str(file_db_id))
        is_success = True
    except:
        logger.exception("Query failed.")
        is_success = False
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return is_success


def get_file_from_id(file_db_id):
    logger.info("Getting file From file_db_id: " + str(file_db_id))
    query = """SELECT user_id, file_id, is_prod_info_avl, status from FILES WHERE id=%s"""
    values = (file_db_id, )
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
            ret_val = True, row[0], row[1], row[2], row[3]
        else:
            ret_val = True, None, None, None, None
    except:
        logger.exception("Query failed.")
        ret_val = False, None, None, None, None
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return ret_val
