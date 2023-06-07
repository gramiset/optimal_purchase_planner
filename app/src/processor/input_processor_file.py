import warnings

warnings.filterwarnings('ignore')

import src.util.util_db as util_db
import os
import pandas as pd
import uuid
import logging
import src.util.util_log as util_log
import src.util.util_session as util_session
import src.util.util_file as util_file
import threading


logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)


def process_file_upload_input(session, request):
    logger.info("Processing File Upload.")
    try:
        product_info_df = None
        if 'file_1' in request.files and request.files['file_1'].filename != '':
            logger.info("file_1 exist in request.files")
            fileid = str(uuid.uuid1())
            logger.info("fileid: " + str(fileid))
            user_id = util_session.get_value_from_session(request, session, 'user_id')
            userdir = os.path.join(util_file.get_root_dir(), str(user_id))
            util_file.create_dir_if_local(userdir)
            filedir = os.path.join(userdir, fileid)
            util_file.create_dir_if_local(filedir)
            past_sales_df, error = validate_past_sales_csv_file(request, filedir)
            if error is None:
                if 'file_2' in request.files and request.files['file_2'].filename != '':
                    logger.info('Product Info File also uploaded. ')
                    products = list(past_sales_df.columns.values)
                    products.remove('Month')
                    product_info_df, error = validate_prod_info_csv_file(request, products, filedir)
                else:
                    logger.info('Product Info File in not uploaded.')
                if error is None:
                    file_db_id = util_db.insert_file(user_id, fileid, product_info_df is not None,
                                                     util_file.INPROGRESS_STATUS)
                    if file_db_id is not None:
                        try:
                            threading.Thread(name=file_db_id, target=util_file.call_process_files_api, args=(file_db_id, ), daemon=True).start()
                        except:
                            logger.exception("File Data Processing Failed")
                            error = 'Error occurred while processing input files. Please try again later.'
                            util_db.update_file_status(user_id, fileid, util_file.FAILED_STATUS)
                            util_file.delete_dir(filedir)
                    else:
                        error = 'Error occurred while processing input files. Please try again later.'
                        util_file.delete_dir(filedir)
        else:
            error = 'Past Sales CSV file is mandatory.'
    except Exception as e:
        logger.error(e)
        error = 'Error occurred while processing input files. Please try again later.'
        util_file.delete_dir(filedir)
    return error


def validate_past_sales_csv_file(request, filedir):
    filepath = os.path.join(filedir, util_file.past_sales_temp_file_name + util_file.file_ext)
    try:
        past_sales_csv_file = request.files['file_1']
        if past_sales_csv_file and allowed_file(past_sales_csv_file.filename):
            util_file.save_form_file(past_sales_csv_file, filepath)
            past_sales_df = util_file.read_csv_file_to_df(filepath)
            # Removing duplicate rows.
            past_sales_df.drop_duplicates()

            columns = list(past_sales_df.columns.values)

            # Checking for duplicate columns in CSV
            if duplicates_exist(columns):
                return None, 'Past Sales CSV file: has duplicate columns'

            # Checking for Month column in CSV
            if "Month" not in columns:
                return None, 'Past Sales CSV file: Month column is mandatory'

            # Checking for product column in CSV
            if len(columns) == 1:
                return None, 'Past Sales CSV file: At least 1 product data is require to process.'

            # Checking for minimum volume of data
            if past_sales_df.index.size < 36:
                return None, 'Past Sales CSV file: At least last 36 months sales data require to predict next 12 ' \
                             'months demand.'

            # Checking for NaN or Empty values in Month column
            if contains_empty_values(past_sales_df, 'Month'):
                return None, 'Past Sales CSV file: Month column contains empty values.'

            # Checking for incorrect Month values in Month column
            if contains_incorrect_date(past_sales_df, 'Month'):
                return None, 'Past Sales CSV file: Month column contains incorrect date values.'

            # Converting month column as date type
            past_sales_df['Month'] = pd.to_datetime(past_sales_df.Month)
            # Stripping date from month column
            past_sales_df['Month'] = past_sales_df['Month'].dt.strftime('%Y-%m')

            # Checking for duplicate Month value in Month column
            if not past_sales_df['Month'].is_unique:
                return None, 'Past Sales CSV file: Duplicate months exist in Month column.'

            # Sorting dataset on Month
            past_sales_df.sort_values(by='Month', inplace=True)

            # Checking type of sale columns
            dtypes = past_sales_df.dtypes
            for dtype in dtypes[1:]:
                if dtype not in ['int64']:
                    return None, 'Past Sales CSV file: Product sale columns should contain integer data.'
        else:
            return None, 'File has issue and only .csv file allowed. Please check and upload again.'
        past_sales_df = prepare_past_sales_data(past_sales_df)
        util_file.remove_file(filepath)
        util_file.save_df_to_csv_file(past_sales_df, filepath)
        return past_sales_df, None
    except Exception as e:
        logger.error(e)
        return None, 'Error occurred while processing input file. Please try again later.'


def validate_prod_info_csv_file(request, products, filedir):
    filepath = os.path.join(filedir, util_file.product_info_temp_file_name + util_file.file_ext)
    try:
        product_info_csv_file = request.files['file_2']
        if product_info_csv_file and allowed_file(product_info_csv_file.filename):
            util_file.save_form_file(product_info_csv_file, filepath)
            product_info_df = util_file.read_csv_file_to_df(filepath)
            # Removing duplicate rows.
            product_info_df.drop_duplicates()

            columns = list(product_info_df.columns.values)

            # Checking for duplicate columns in CSV
            if duplicates_exist(columns):
                return None, 'Product Info CSV file: has duplicate columns'

            # Checking for required columns in CSV
            req_columns = ['Product', 'Inventory_Cost', 'Stockout_Cost', 'Expecting_Monthly_Stock']
            if set(columns) != set(req_columns):
                return None, 'Product Info CSV file: Product, Inventory_Cost, Stockout_Cost, Expecting_Monthly_Stock ' \
                             'columns mandatory and those 4 columns only allowed in CSV.'

            # Checking for NaN or Empty values in Product column
            if contains_empty_values(product_info_df, 'Product'):
                return None, 'Product Info CSV file: Month column contains empty values.'

            # Checking for duplicate products in Product column
            if not product_info_df['Product'].is_unique:
                return None, 'Product Info CSV file: Duplicate products exist in Product column.'

            # Checking that both files contains same products
            products1 = product_info_df['Product'].values.tolist()
            if set(products) != set(products1):
                return None, 'Product Info CSV file: Products not in sync with Past Sales CSV file.'

            # Checking that both files contains same products
            products1 = product_info_df['Product'].values.tolist()
            if set(products) != set(products1):
                return None, 'Product Info CSV file: Products not in sync with Past Sales CSV file.'

            # Checking type of product columns
            dtypes = product_info_df.dtypes
            for dtype in dtypes[1:]:
                if dtype not in ['int64', 'float64']:
                    return None, 'Product Info CSV file: Inventory_Cost, Stockout_Cost, Expecting_Monthly_Stock ' \
                                 'columns should contain numeric data.'
        else:
            return None, 'File has issue and only .csv file allowed. Please check and upload again.'
        product_info_df = prepare_product_info_data(product_info_df)
        util_file.remove_file(filepath)
        util_file.save_df_to_csv_file(product_info_df, filepath)
        return product_info_df, None
    except Exception as e:
        logger.error(e)
        return None, 'Error occurred while processing input file. Please try again later.'


def prepare_product_info_data(product_info_df):
    # Replace NaN values with 0
    columns = list(product_info_df.columns.values)
    columns.remove('Product')
    for column in columns:
        product_info_df[column].fillna(0, inplace=True)
    return product_info_df


def prepare_past_sales_data(past_sales_df):
    # Add missing data rows
    past_sales_df = add_missing_month_rows(past_sales_df)
    # Replace NaN values with mean
    columns = list(past_sales_df.columns.values)
    columns.remove('Month')
    for column in columns:
        past_sales_df[column].fillna(int(past_sales_df[column].mean()), inplace=True)
    return past_sales_df


def add_missing_month_rows(past_sales_df):
    past_sales_df.set_index('Month', inplace=True)
    past_sales_df_months = pd.DataFrame(
        {'Month': pd.period_range(past_sales_df.index[0], past_sales_df.index[-1], freq='M')})
    past_sales_df_months['Month'] = pd.to_datetime(past_sales_df_months.Month.dt.strftime('%Y-%m')).dt.date
    past_sales_df_months['Month'] = pd.to_datetime(past_sales_df_months.Month).dt.strftime('%Y-%m')
    past_sales_df.reset_index(inplace=True)
    past_sales_df = pd.merge(past_sales_df, past_sales_df_months, on='Month', how='outer')
    past_sales_df.sort_values(by='Month', inplace=True)
    past_sales_df.set_index('Month', inplace=True)
    past_sales_df.reset_index(inplace=True)
    return past_sales_df


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}


def duplicates_exist(columns):
    columns_set = set()
    for column in columns:
        if '.' in column:
            columns_set.add(column.split('.')[0])
        else:
            columns_set.add(column)
    return len(columns) != len(columns_set)


def contains_empty_values(df, column):
    df = df[column]
    return df.eq('').any() | df.isna().any()


def contains_incorrect_date(df, column):
    m1 = df[column].eq('') | df[column].isna()
    m2 = pd.to_datetime(df[column], errors='coerce').isna()
    return not m1.eq(m2).all()
