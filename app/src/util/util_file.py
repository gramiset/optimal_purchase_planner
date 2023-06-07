import uuid
import src.util.util_config as util_config
import logging
import src.util.util_log as util_log
import shutil
import os
import pandas as pd
import numpy as np
from google.cloud import storage
import requests
import json

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)

logger = logging.getLogger(__name__)
config = util_config.get_config()
gcs_bucket = "gs://purc-plan"
gcs_bucket_name = "purc-plan"
local_root_dir = "static/files"
gcp_root_dir = "files"
product_file_name = "Product"
test_file_name = "Test"
past_sales_file_name = "Sales"
past_sales_temp_file_name = "Sales_Temp"
product_info_temp_file_name = "Product_Info_Temp"
decompose_plot_img_name = "_Decompose.png"
stationary_plot_img_name = "_Stationary.png"
test_plot_img_name = "_Test.png"
file_ext = ".csv"
INPROGRESS_STATUS = "IN-PROGRESS"
SUCCESS_STATUS = "SUCCESS"
FAILED_STATUS = "FAILED"
gcs_bucket_url = "https://storage.cloud.google.com/purc-plan/"


def get_root_dir():
    if os.environ['APP_ENV'] == 'gcp':
        return gcp_root_dir
    else:
        return local_root_dir


def read_csv_file_to_df(filepath):
    if os.environ['APP_ENV'] == 'gcp':
        return read_gcp_csv_file_to_df(filepath)
    else:
        return read_local_csv_file_to_df(filepath)


def read_local_csv_file_to_df(filepath):
    return pd.read_csv(filepath)


def read_gcp_csv_file_to_df(filepath):
    try:
        return pd.read_csv(os.path.join(gcs_bucket, filepath))
    except:
        logger.exception("read_gcp_csv_file_to_df failed.")
        return None


def save_df_to_csv_file(df, filepath):
    if os.environ['APP_ENV'] == 'gcp':
        return save_df_to_gcp_csv_file(df, filepath)
    else:
        return save_df_to_local_csv_file(df, filepath)


def save_df_to_local_csv_file(df, filepath):
    np.set_printoptions(threshold=100000)
    df.to_csv(filepath, index=False)


def save_df_to_gcp_csv_file(df, filepath):
    try:
        temp_file_name = str(uuid.uuid1()) + ".csv"
        temp_file_path = os.path.join("/tmp", temp_file_name)
        np.set_printoptions(threshold=100000)
        df.to_csv(temp_file_path, index=False)

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(gcs_bucket_name)
        blob = bucket.blob(filepath)
        blob.upload_from_filename(temp_file_path)
        remove_local_file(temp_file_path)
    except:
        logger.exception("save_df_to_gcp_csv_file failed.")


def get_products_from_sales_df(past_sales_df):
    products = list(past_sales_df.columns.values)
    products = [x for x in products if "MA_12_Month" not in x]
    products = [x for x in products if "MA_25_Month" not in x]
    products.remove('Month')
    return products


def create_dir_if_local(dirpath):
    if os.environ['APP_ENV'] == 'local':
        create_local_dir(dirpath)


def create_dir(dirpath):
    if os.environ['APP_ENV'] == 'gcp':
        return create_gcp_dir(dirpath)
    else:
        return create_local_dir(dirpath)


def create_local_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
        logger.info(str(dirpath) + " directory is created.")
    else:
        logger.info(str(dirpath) + " directory already exists.")


def create_gcp_dir(dirpath):
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(gcs_bucket_name)
        blob = bucket.blob(os.path.join(dirpath, "temp"))
        blob.upload_from_string('')
        logger.info(str(dirpath) + " directory is created.")
    except:
        logger.exception("create_gcp_dir failed.")


def remove_file(filepath):
    if os.environ['APP_ENV'] == 'gcp':
        return delete_gcp_file_or_dir(filepath)
    else:
        return remove_local_file(filepath)


def remove_local_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(str(filepath) + " file is deleted.")
    else:
        logger.info(str(filepath) + " file not exist to delete.")


def delete_dir(dirpath):
    if os.environ['APP_ENV'] == 'gcp':
        return delete_gcp_file_or_dir(dirpath)
    else:
        return delete_local_dir(dirpath)


def delete_local_dir(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)
        logger.info(str(dirpath) + " dir is deleted.")
    else:
        logger.info(str(dirpath) + " dir not exist to delete.")


def delete_gcp_file_or_dir(path):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(gcs_bucket_name)
        blob = bucket.blob(path)
        blob.reload()
        generation_match_precondition = blob.generation
        blob.delete(if_generation_match=generation_match_precondition)
        logger.info(str(path) + " is deleted.")
    except:
        logger.exception("delete_gcp_file_or_dir failed.")


def save_form_file(plt, imagepath):
    if os.environ['APP_ENV'] == 'gcp':
        return save_form_file_gcp(plt, imagepath)
    else:
        return save_form_file_local(plt, imagepath)


def save_form_file_local(form_file, filepath):
    form_file.save(filepath)


def save_form_file_gcp(form_file, filepath):
    try:
        temp_file_name = str(uuid.uuid1()) + ".csv"
        temp_file_path = os.path.join("/tmp", temp_file_name)
        form_file.save(temp_file_path)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(gcs_bucket_name)
        blob = bucket.blob(filepath)
        blob.upload_from_filename(temp_file_path)
        remove_local_file(temp_file_path)
    except:
        logger.exception("save_form_file_gcp failed.")


def save_plot_image(plt, imagepath):
    if os.environ['APP_ENV'] == 'gcp':
        return save_plot_image_gcp(plt, imagepath)
    else:
        return save_plot_image_local(plt, imagepath)


def save_plot_image_local(plt, imagepath):
    plt.savefig(imagepath)


def save_plot_image_gcp(plt, imagepath):
    try:
        temp_img_name = str(uuid.uuid1()) + ".png"
        temp_img_path = os.path.join("/tmp", temp_img_name)
        plt.savefig(temp_img_path)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(gcs_bucket_name)
        blob = bucket.blob(imagepath)
        blob.upload_from_filename(temp_img_path)
        remove_local_file(temp_img_path)
    except:
        logger.exception("save_plot_image_gcp failed.")


def get_sample_file_paths():
    if os.environ['APP_ENV'] == 'gcp':
        return (gcs_bucket_url + "sample/Past_Monthly_Sales_Data.csv",
                gcs_bucket_url + "sample/Product_Info.csv")
    else:
        return ("download_sample/Past_Monthly_Sales_Data.csv",
                "download_sample/Product_Info.csv")


def get_image_path(user_id, file_id, product, img_name):
    img_path = os.path.join(get_root_dir(), str(user_id), file_id, product + img_name)
    if os.environ['APP_ENV'] == 'gcp':
        return gcs_bucket_url + img_path
    else:
        return img_path


def call_process_files_api(file_db_id):
    parameters = {
        "id": file_db_id
    }
    api = config.get('FILE_PROCESS_API', 'url').strip()
    response = requests.get(f"{api}", params=parameters)
    if response.status_code == 200:
        logger.info("file-process api call success. " + str(response.text))
    else:
        logger.error("file-process api call failed. " + str(response.text))
