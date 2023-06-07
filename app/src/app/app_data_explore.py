from flask import Blueprint, render_template, session, request
import os
import src.util.util_db as util_db
import src.util.util_common as util_common
import src.util.util_file as util_file
import logging
import src.util.util_log as util_log
import src.app.app_file_process as app_file_process
import src.util.util_session as util_session

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)

app_data_explore = Blueprint('app_data_explore', __name__)


def distribution_string_to_array(data):
    data_list = list()
    if data is not None and data.strip() != '':
        data = data.replace('[', '').replace(']', '').replace('\n', '')
        data_arr = data.split(' ')
        for val in data_arr:
            data_list.append(float(val))
    return data_list


@app_data_explore.route('/explore')
def explore():
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
                            prod_mean_std_df = prod_df[
                                ['Product', 'Mean', 'Standard Deviation']]
                            prod_dist_df = prod_df[
                                ['Product', 'Normal Distribution (Probability Density Function)']]
                            prod_dist_df['Normal Distribution (Probability Density Function)'] = \
                                prod_dist_df['Normal Distribution (Probability Density Function)'].map(
                                    distribution_string_to_array)

                            # Pass the mean and standard deviation table and the bar chart data to the template
                            return util_session.send_response(session, render_template('explore.html',
                                                                                       mean_std_table=prod_mean_std_df.to_html(classes='table_style',
                                                                                           table_id="mean_std_table", index_names=False, index=False),
                                                                                       distribution_table=prod_dist_df.to_html(classes='table_style',
                                                                                           table_id="distribution_table", index_names=False, index=False)))
                        else:
                            error = "File which selected is in not in SUCCESS state. Please select the success file " \
                                    "from your files list."
                            return app_file_process.render_show_files(error)
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
