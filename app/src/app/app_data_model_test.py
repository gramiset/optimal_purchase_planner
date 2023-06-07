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

app_data_model_test = Blueprint('app_data_model_test', __name__)


@app_data_model_test.route('/model_test')
def model_test():
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
                            prod_df = util_file.read_csv_file_to_df(prod_file_path)
                            products = prod_df['Product'].to_list()
                            data = [None] * len(products)
                            index = 0
                            for product in products:
                                prod_row_df = prod_df.loc[prod_df['Product'] == product]
                                data[index] = (product,
                                               util_file.get_image_path(user_id, file_id, product,
                                                                        util_file.test_plot_img_name),
                                               (prod_row_df['Best ARIMA model'].tolist()[0],
                                                prod_row_df['Test RMSE'].tolist()[0]))
                                index += 1
                            return util_session.send_response(session, render_template('model_test.html', data=data))
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
