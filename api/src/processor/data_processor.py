import warnings
from multiprocessing import Process

warnings.filterwarnings('ignore')

import src.util.util_db as util_db
import os
import pandas as pd
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt
from scipy.stats import norm
from numpy import finfo
import logging
import src.util.util_log as util_log
import pmdarima as pm
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import seaborn as sns
import src.util.util_file as util_file

sns.set_style('white', {'axes.spines.right': False, 'axes.spines.top': False})

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)


def process_files(file_db_id):
    try:
        is_success, user_id, file_id, is_prod_info_avl, status = util_db.get_file_from_id(int(file_db_id))
        if is_success:
            if user_id is not None and file_id is not None:
                if status == 'IN-PROGRESS':
                    P = Process(name=file_id, target=process_data,
                                    args=(file_db_id, user_id, file_id, is_prod_info_avl), daemon=True)
                    P.start()
                    logger.info("Background processing of files started: FILE_ID: " + str(file_id))
                    return "File Processing Completed.", 200
                else:
                    error, code = "File status is " + status + ". Only IN-PROGRESS status will be processed.", 400
            else:
                error, code = "File not exist. file_db_id: " + str(file_db_id), 400
        else:
            error, code = "File Get Query Failed. Please trigger api after sometime. file_db_id: " + str(file_db_id), 500
    except:
        logger.exception("Query failed.")
        error, code = "File Get Query Failed. Please trigger api after sometime. file_db_id: " + str(file_db_id), 500
    logger.error(error)
    return error, code


def process_data(file_db_id, user_id, file_id, is_prod_info_avl):
    filedir = os.path.join(util_file.get_root_dir(), str(user_id), file_id)
    past_sales_filepath = os.path.join(filedir,
                                       util_file.past_sales_temp_file_name + util_file.file_ext)
    product_info_filepath = os.path.join(filedir,
                                         util_file.product_info_temp_file_name + util_file.file_ext)
    try:
        past_sales_df = util_file.read_csv_file_to_df(past_sales_filepath)
        product_info_df = None
        if is_prod_info_avl:
            product_info_df = util_file.read_csv_file_to_df(product_info_filepath)
        logger.error("File Process Started: FILE_ID: " + str(file_id))
        product_df, past_sales_df, test_df = predict_results(past_sales_df, product_info_df)
        logging.info('product_df head - {}'.format(product_df.head()))
        logging.info('past_sales_df head - {}'.format(past_sales_df.head()))
        logging.info('test_df head - {}'.format(test_df.head()))
        products = util_file.get_products_from_sales_df(past_sales_df)
        save_decompose_plot_images(past_sales_df, products, filedir)
        save_stationary_plot_images(past_sales_df, products, filedir)
        save_test_plot_images(test_df, products, filedir)
        util_file.save_df_to_csv_file(product_df,
                                  os.path.join(filedir, util_file.product_file_name + util_file.file_ext))
        util_file.save_df_to_csv_file(past_sales_df,
                                  os.path.join(filedir, util_file.past_sales_file_name + util_file.file_ext))
        util_file.save_df_to_csv_file(test_df,
                                  os.path.join(filedir, util_file.test_file_name + util_file.file_ext))
        util_db.update_file_status(int(file_db_id), util_file.SUCCESS_STATUS)
        logger.info("Files process completed successfully. FILE_ID: " + str(file_id))
    except:
        logger.exception("File Data Processing Failed")
        util_db.update_file_status(int(file_db_id), util_file.FAILED_STATUS)
        util_file.delete_dir(filedir)
    finally:
        util_file.remove_file(past_sales_filepath)
        if is_prod_info_avl:
            util_file.remove_file(product_info_filepath)


def predict_results(past_sales_df, product_info_df):
    product_df, past_sales_df1 = get_mean_std_df(past_sales_df)
    logger.info("Mean and Standard Deviation Calculation completed.")
    product_df = add_normal_distribution(product_df, past_sales_df1)
    logger.info("Normal Distribution Calculation completed.")
    products = list(past_sales_df.columns.values)
    products.remove('Month')
    logger.info("Products: " + str(products))
    past_sales_df, product_df = adding_rolling_mean_stationary_cols(past_sales_df, product_df, products)
    test_df, arima_best_model_list, rmse_list, prediction_list = create_model_and_predict(past_sales_df, products)
    product_df = add_calculated_columns(product_df, products, arima_best_model_list, rmse_list, prediction_list)
    if product_info_df is not None:
        product_df = add_product_info_columns(product_df, product_info_df)
        product_df = add_shortfalls_column(product_df)
        product_df = add_total_cost_column(product_df)
    return product_df, past_sales_df, test_df


def get_mean_std_df(past_sales_df):
    columns = list(past_sales_df.columns.values)
    columns.remove('Month')
    past_sales_df1 = past_sales_df[columns]
    mean_df = pd.DataFrame(past_sales_df1.mean())
    mean_df.columns = ['Mean']
    std_df = pd.DataFrame(past_sales_df1.std())
    std_df.columns = ['Standard Deviation']
    product_df = mean_df.join(std_df, how='inner')
    product_df.reset_index(inplace=True)
    product_df = product_df.rename(columns={"index": "Product"})
    return product_df, past_sales_df1


def add_normal_distribution(product_df, past_sales_df):
    product_df['Normal Distribution (Probability Density Function)'] = product_df.apply(
        lambda row: normal_distribution(past_sales_df, row), axis=1)
    return product_df


# Calculate the normal distribution (probability density function) using mean and standard deviation
def normal_distribution(past_sales_df, row):
    epsilon = finfo(float).eps
    return norm.pdf(past_sales_df[row['Product']], row['Mean'], row['Standard Deviation'] + epsilon)


def create_rolling_mean_cols(past_sales_df, product):
    if past_sales_df.index.size > 12:
        past_sales_df[product + '_MA_12_Month'] = past_sales_df[product].rolling(window=12).mean()
        past_sales_df[product + '_MA_25_Month'] = past_sales_df[product].rolling(window=25).mean()
    return past_sales_df


def get_stationary_vals(past_sales_df, product):
    sales = past_sales_df[product].dropna()
    # Perform an Ad Fuller Test
    # the default alpha = .05 stands for a 95% confidence interval
    adf_test = pm.arima.ADFTest(alpha=0.05)
    adf_test_result = adf_test.should_diff(sales)
    logger.info("As per ARIMA ADF Test: ")
    adf_p_value = adf_test_result[0]
    logger.info("P-value: " + str(adf_p_value))
    if adf_test_result[1]:
        is_adf_stationary = 'Yes'
        logger.info("Yes, Data is Stationary.");
    else:
        is_adf_stationary = 'No'
        logger.info("No, Data is Non-Stationary.");

    logger.info("\nadfuller test result: ")
    dftest = adfuller(past_sales_df[product], autolag='AIC')
    adfuller_adf_value = dftest[0]
    logger.info("1. ADF : " + str(adfuller_adf_value))
    adfuller_p_value = dftest[1]
    logger.info("2. P-Value : " + str(adfuller_p_value))
    adfuller_no_of_lags = dftest[2]
    logger.info("3. Num Of Lags : " + str(adfuller_no_of_lags))
    adfuller_no_of_obs_used = dftest[3]
    logger.info("4. Num Of Observations Used For ADF Regression:" + str(adfuller_no_of_obs_used))
    logger.info("5. Critical Values :")
    adfuller_critical_vals = list()
    for key, val in dftest[4].items():
        logger.info("\t" + str(key) + ": " + str(val))
        adfuller_critical_vals.append(val)

    print("\nAs per adfuller Test: ")
    if dftest[1] <= 0.05:
        is_adfuller_stationary = 'Yes'
        print("Yes, P-Value is less than or equal to 0.5. Data is Stationary.");
    else:
        is_adfuller_stationary = 'No'
        print("No, P-Value is greater than 0.5. Data is Non-Stationary.\n");
    return adf_p_value, is_adf_stationary, adfuller_adf_value, adfuller_p_value, adfuller_no_of_lags, adfuller_no_of_obs_used, adfuller_critical_vals, is_adfuller_stationary


def adding_rolling_mean_stationary_cols(past_sales_df, product_df, products):
    adf_p_value_list = list()
    is_adf_stationary_list = list()
    adfuller_adf_value_list = list()
    adfuller_p_value_list = list()
    adfuller_no_of_lags_list = list()
    adfuller_no_of_obs_used_list = list()
    adfuller_critical_vals_1_list = list()
    adfuller_critical_vals_5_list = list()
    adfuller_critical_vals_10_list = list()
    is_adfuller_stationary_list = list()
    for product in products:
        past_sales_df = create_rolling_mean_cols(past_sales_df, product)
        adf_p_value, is_adf_stationary, adfuller_adf_value, adfuller_p_value, adfuller_no_of_lags, \
            adfuller_no_of_obs_used, adfuller_critical_vals, is_adfuller_stationary = \
            get_stationary_vals(past_sales_df, product)
        adf_p_value_list.append(adf_p_value)
        is_adf_stationary_list.append(is_adf_stationary)
        adfuller_adf_value_list.append(adfuller_adf_value)
        adfuller_p_value_list.append(adfuller_p_value)
        adfuller_no_of_lags_list.append(adfuller_no_of_lags)
        adfuller_no_of_obs_used_list.append(adfuller_no_of_obs_used)
        adfuller_critical_vals_1_list.append(adfuller_critical_vals[0])
        adfuller_critical_vals_5_list.append(adfuller_critical_vals[1])
        adfuller_critical_vals_10_list.append(adfuller_critical_vals[2])
        is_adfuller_stationary_list.append(is_adfuller_stationary)

    stationary_df = pd.DataFrame(
        {'Product': products, 'ADF Test P-Value': adf_p_value_list,
         'Is Data Stationary Based on ADF Test': is_adf_stationary_list,
         'Adfuller Test ADF Value': adfuller_adf_value_list, 'Adfuller Test P-Value': adfuller_p_value_list,
         'Adfuller Test No.of Lags': adfuller_no_of_lags_list,
         'Adfuller Test No.of Observations Used': adfuller_no_of_obs_used_list,
         'Adfuller Test Critical Value 1%': adfuller_critical_vals_1_list,
         'Adfuller Test Critical Value 5%': adfuller_critical_vals_5_list,
         'Adfuller Test Critical Value 10%': adfuller_critical_vals_10_list,
         'Is Data Stationary Based on Adfuller Test': is_adfuller_stationary_list})
    stationary_df.set_index('Product', inplace=True, drop=True)
    product_df.set_index('Product', inplace=True, drop=True)
    product_df = product_df.join(stationary_df, how='inner')
    product_df.reset_index(inplace=True)
    return past_sales_df, product_df


def create_model_and_predict(past_sales_df, products):
    index = 0
    arima_best_model_list = list()
    rmse_list = list()
    prediction_list = [None] * len(products)
    for product in products:
        stepwise_fit = auto_arima(past_sales_df[product], trace=True, suppress_warnings=True)
        logger.info("Best model ===> " + str(stepwise_fit.order))
        arima_best_model_list.append(stepwise_fit.order)
        X = past_sales_df[product].values
        size = int(len(X) * 0.66)
        train, test = X[0:size], X[size:len(X)]
        history = [x for x in train]
        predictions = list()
        for t in range(len(test)):
            model = ARIMA(history, order=stepwise_fit.order)
            model_fit = model.fit()
            output = model_fit.forecast()
            yhat = output[0]
            predictions.append(yhat)
            obs = test[t]
            history.append(obs)
            logger.info("predicted=" + str(yhat) + ", expected=" + str(obs))
        # create a dataframe with predicted values
        test_df1 = pd.DataFrame({product + '_test_sales': test, product + '_predicted': predictions})
        test_df1 = test_df1[[product + '_test_sales', product + '_predicted']]
        if index == 0:
            test_df = test_df1
        else:
            test_df = test_df.join(test_df1, how='inner')
        rmse = sqrt(mean_squared_error(test, predictions))
        rmse_list.append(rmse)
        predictions = stepwise_fit.predict(n_periods=12, return_conf_int=False)
        predictions = [int(prediction) for prediction in predictions]
        prediction_list[index] = list(predictions)
        index += 1
    logger.info("Arima Best Models: " + str(arima_best_model_list))
    logger.info("RSME: " + str(rmse_list))
    logger.info("Predictions: " + str(list(predictions)))
    return test_df, arima_best_model_list, rmse_list, prediction_list


def add_calculated_columns(product_df, products, arima_best_model_list, rmse_list, prediction_list):
    future_demand_df = pd.DataFrame(
        {'Product': products, 'Best ARIMA model': arima_best_model_list, 'Test RMSE': rmse_list,
         'Estimated Future Product Demand': prediction_list})
    future_demand_df.set_index('Product', inplace=True, drop=True)
    product_df.set_index('Product', inplace=True, drop=True)
    product_df = product_df.join(future_demand_df, how='inner')
    product_df.reset_index(inplace=True)
    return product_df


def add_product_info_columns(product_df, product_info_df):
    product_info_df.set_index('Product', inplace=True, drop=True)
    product_df.set_index('Product', inplace=True, drop=True)
    product_df = product_df.join(product_info_df, how='inner')
    product_df.reset_index(inplace=True)
    return product_df


def add_shortfalls_column(product_df):
    product_df['Estimated Shortfalls'] = product_df.apply(lambda row: estimate_shortfalls(row), axis=1)
    return product_df


def estimate_shortfalls(row):
    shortfalls = []
    for month in range(len(row['Estimated Future Product Demand'])):
        monthly_shortfall = row['Estimated Future Product Demand'][month] - row['Expecting_Monthly_Stock']
        shortfalls.append(monthly_shortfall)
    return shortfalls


def add_total_cost_column(product_df):
    product_df['Estimated Total Cost'] = product_df.apply(lambda row: evaluate_total_cost(row), axis=1)
    return product_df


def evaluate_total_cost(row):
    return sum([cost if shortfall >= 0 else -(row['Inventory_Cost']) * shortfall
                for shortfall, cost in zip(row['Estimated Shortfalls'],
                                           [row['Stockout_Cost'] * abs(shortfall) for shortfall in
                                            row['Estimated Shortfalls']])])


def save_decompose_plot_images(past_sales_df, products, filedir):
    for product in products:
        decomp_viz = seasonal_decompose(past_sales_df[product], model='multiplicative', period=12)
        fig = decomp_viz.plot()
        fig.set_size_inches((10, 6))
        # Tight layout to realign things
        fig.tight_layout()
        util_file.save_plot_image(plt, os.path.join(filedir, product + util_file.decompose_plot_img_name))


def save_stationary_plot_images(past_sales_df, products, filedir):
    for product in products:
        # Visualize the data
        fig, ax = plt.subplots(figsize=(16, 8))
        plt.title(product + " Sales", fontsize=14)
        labels = [product, 'MA_12_Month', 'MA_25_Month']
        if past_sales_df.index.size > 12:
            sns.lineplot(data=past_sales_df[[product, product + '_MA_25_Month', product + '_MA_12_Month']],
                         palette=sns.color_palette("mako_r", 3))
            plt.legend(title='Smoker', loc='upper left', labels=labels)
        else:
            sns.lineplot(data=past_sales_df[[product]])
        fig.set_size_inches((16, 8))
        # Tight layout to realign things
        fig.tight_layout()
        util_file.save_plot_image(plt, os.path.join(filedir, product + util_file.stationary_plot_img_name))


def save_test_plot_images(test_df, products, filedir):
    for product in products:
        # Visualize the data
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.plot(test_df[product + '_test_sales'].values)
        plt.plot(test_df[product + '_predicted'].values, color='red')
        fig.set_size_inches((10, 6))
        # Tight layout to realign things
        fig.tight_layout()
        util_file.save_plot_image(plt, os.path.join(filedir, product + util_file.test_plot_img_name))
