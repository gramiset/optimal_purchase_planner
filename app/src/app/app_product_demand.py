from flask import Blueprint, render_template, session, request
import os
import src.util.util_db as util_db
import src.util.util_common as util_common
import logging
import src.util.util_log as util_log
import src.app.app_file_process as app_file_process
import src.util.util_session as util_session
import src.util.util_file as util_file

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)

app_product_demand = Blueprint('app_product_demand', __name__)


def string_to_array(data):
    data_list = list()
    if data is not None and data.strip() != '':
        data = data.replace('[', '').replace(']', '').replace('\n', '').replace(',', '')
        data_arr = data.split(' ')
        for val in data_arr:
            data_list.append(int(float(val)))
    return data_list


@app_product_demand.route('/product_demand')
def product_demand():
    util_session.populate_session(request, session)
    if not util_session.is_valid_session(request, session):
        return util_session.send_response(session, render_template("login.html", captcha_site_key=util_common.captcha_site_key))
    else:
        try:
            user_id = util_session.get_value_from_session(request, session, 'user_id')
            file_id = util_session.get_value_from_session(request, session, 'file_id')
            if file_id is not None:
                is_success, id, is_prod_info_avl, status = util_db.get_file_from_id(user_id, file_id)
                if is_success:
                    if id is not None:
                        if status == "SUCCESS":
                            prod_file_path = os.path.join(util_file.get_root_dir(), str(user_id), file_id,
                                                          util_file.product_file_name + util_file.file_ext)
                            product_df = util_file.read_csv_file_to_df(prod_file_path)
                            product_df['Estimated Future Product Demand'] = product_df['Estimated Future Product Demand'].map(string_to_array)
                            future_demand_df = product_df[['Product', 'Estimated Future Product Demand']].set_index('Product').T
                            column_names = future_demand_df.columns.values.tolist()
                            future_demand_df = future_demand_df.explode(column_names).reset_index(drop=True)
                            future_demand_df.insert(0, 'Month', range(1, 1 + len(future_demand_df)))
                            future_demand_df = future_demand_df.set_index('Month')
                            future_demand_df.reset_index(inplace=True)

                            if is_prod_info_avl:
                                product_df['Estimated Shortfalls'] = product_df['Estimated Shortfalls'].map(string_to_array)
                                shortfalls_df = product_df[['Product', 'Estimated Shortfalls']].set_index('Product').T
                                column_names = shortfalls_df.columns.values.tolist()
                                shortfalls_df = shortfalls_df.explode(column_names).reset_index(drop=True)
                                shortfalls_df.insert(0, 'Month', range(1, 1 + len(shortfalls_df)))
                                shortfalls_df = shortfalls_df.set_index('Month')
                                shortfalls_df.reset_index(inplace=True)

                                total_cost_df = product_df[['Product', 'Estimated Total Cost']].set_index('Product').T
                                column_names = total_cost_df.columns.values.tolist()
                                total_cost_df = total_cost_df.explode(column_names).reset_index(drop=True)
                                total_cost_df.insert(0, 'Month', range(1, 1 + len(total_cost_df)))
                                total_cost_df = total_cost_df.set_index('Month')

                                return util_session.send_response(session, render_template("product_demand.html",
                                                                                           future_demand_table=future_demand_df.to_html(
                                                           classes='table_style', table_id="future_demand_table", index_names=False, index=False),
                                                                                           shortfalls_table=shortfalls_df.to_html(classes='table_style',
                                                                                              table_id="shortfalls_table", index_names=False, index=False),
                                                                                           total_cost_table=total_cost_df.to_html(classes='table_style',
                                                                                              table_id="total_cost_table", index_names=False, index=False)))
                            else:
                                return util_session.send_response(session, render_template("product_demand.html",
                                                                                           future_demand_table=future_demand_df.to_html(
                                                           classes='table_style', table_id="future_demand_table", index_names=False, index=False)))
                        else:
                            return app_file_process.render_show_files("File which selected is in not in SUCCESS "
                                                                      "state. Please select the success file from "
                                                                      "your files list.")
                    else:
                        return app_file_process.render_show_files("File not exist or you are not the owner of the file."
                                                                  "Please select the success file from your files list.")
                else:
                    return app_file_process.render_show_files('File loading failed. Please try again later.')
            else:
                return app_file_process.render_show_files('File not selected. Please select the file.')
        except Exception as e:
            logger.error(e)
            return app_file_process.render_show_files('File loading failed. Please try again later.')
