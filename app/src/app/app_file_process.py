import os

from flask import Blueprint, request, session, render_template, send_from_directory
import pandas as pd
import src.processor.input_processor_file as input_processor_file
import logging
import src.util.util_log as util_log
import src.util.util_db as util_db
import src.util.util_common as util_common
import src.util.util_session as util_session
import src.util.util_file as util_file

logging.basicConfig(format=util_log.logging_format, datefmt=util_log.logging_date_format, level=util_log.logging_level)
logger = logging.getLogger(__name__)
app_file_process = Blueprint('app_file_process', __name__, static_folder='static')


@app_file_process.route('/download_sample/<path:filename>')
def download_sample(filename):
    return send_from_directory('static/sample', filename, as_attachment=True)


@app_file_process.route('/file_upload', methods=['GET', 'POST'])
def file_upload():
    util_session.populate_session(request, session)
    if not util_session.is_valid_session(request, session):
        return util_session.send_response(session,
                                          render_template("login.html", captcha_site_key=util_common.captcha_site_key))
    else:
        sample_files=util_file.get_sample_file_paths()
        util_file.get_sample_file_paths()
        if request.method == 'POST':
            error = input_processor_file.process_file_upload_input(session, request)
            if error is None:
                return render_show_files('')
            else:
                return util_session.send_response(session, render_template("file_upload.html", error=error, sample_files=sample_files))
        else:
            return util_session.send_response(session, render_template("file_upload.html", sample_files=sample_files))


def render_show_files(error):
    user_id = util_session.get_value_from_session(request, session, 'user_id')
    is_success, files = util_db.get_user_files(user_id)
    if is_success:
        if files is not None:
            return util_session.send_response(session, render_template("show_files.html", files=files, error=error))
        else:
            sample_files = util_file.get_sample_file_paths()
            return util_session.send_response(session, render_template("file_upload.html", error=error +
                                                                                                 " You don't have any uploaded files. Please upload files to proceed.", sample_files=sample_files))
    else:
        return util_session.send_response(session, render_template("show_files.html",
                                                                   error=error + " Showing files failed. Please try again later."))


@app_file_process.route('/show_files')
def show_files():
    util_session.populate_session(request, session)
    if not util_session.is_valid_session(request, session):
        return util_session.send_response(session,
                                          render_template("login.html", captcha_site_key=util_common.captcha_site_key))
    else:
        return render_show_files('')


@app_file_process.route('/file_data')
def file_data():
    util_session.populate_session(request, session)
    if not util_session.is_valid_session(request, session):
        return util_session.send_response(session,
                                          render_template("login.html", captcha_site_key=util_common.captcha_site_key))
    else:
        try:
            user_id = util_session.get_value_from_session(request, session, 'user_id')
            file_id = request.args.get('file_id', default=None, type=str)
            if file_id is None:
                file_id = util_session.get_value_from_session(request, session, 'file_id')
            if file_id is not None:
                is_success, id, is_prod_info_avl, status = util_db.get_file_from_id(user_id, file_id)
                if is_success:
                    if id is not None:
                        if status == "SUCCESS":
                            sales_file_path = os.path.join(util_file.get_root_dir(), str(user_id), file_id,
                                                           util_file.past_sales_file_name + util_file.file_ext)
                            pd.set_option('colheader_justify', 'center')
                            sales_df = util_file.read_csv_file_to_df(sales_file_path)
                            columns = list(sales_df.columns.values)
                            columns = [x for x in columns if "MA_12_Month" not in x]
                            columns = [x for x in columns if "MA_25_Month" not in x]
                            sales_df = sales_df[columns]
                            # Display only the first 100 rows
                            sales_df_100 = sales_df.head(100)
                            if is_prod_info_avl:
                                prod_file_path = os.path.join(util_file.get_root_dir(), str(user_id), file_id,
                                                              util_file.product_file_name + util_file.file_ext)
                                prod_df = util_file.read_csv_file_to_df(prod_file_path)
                                prod_info_df = prod_df[
                                    ['Product', 'Inventory_Cost', 'Stockout_Cost', 'Expecting_Monthly_Stock']]
                                # Display only the first 100 rows
                                prod_info_df_100 = prod_info_df.head(100)
                                util_session.set_value_in_session(request, session, 'file_id', file_id)
                                return util_session.send_response(session, render_template("file_data.html",
                                                                                           sales_data_table=sales_df_100.to_html(
                                                                                               classes='table_style',
                                                                                               index_names=False,
                                                                                               index=False),
                                                                                           prod_info_table=prod_info_df_100.to_html(
                                                                                               classes='table_style',
                                                                                               index_names=False,
                                                                                               index=False)))
                            else:
                                util_session.set_value_in_session(request, session, 'file_id', file_id)
                                return util_session.send_response(session, render_template("file_data.html",
                                                                                           sales_data_table=sales_df_100.to_html(classes='table_style',
                                                                                             index_names=False,
                                                                                             index=False)))
                        else:
                            util_session.set_value_in_session(request, session, 'file_id', None)
                            return render_show_files("File which selected is in not in SUCCESS state. Please select "
                                                     "the success file from your files list.")
                    else:
                        util_session.set_value_in_session(request, session, 'file_id', None)
                        return render_show_files("File not exist or you are not the owner of the file. "
                                                 "Please select the success file from your files list.")
                else:
                    util_session.set_value_in_session(request, session, 'file_id', None)
                    return render_show_files('File loading failed. Please try again later.')
            else:
                util_session.set_value_in_session(request, session, 'file_id', None)
                return render_show_files('File not selected. Please select the file.')
        except Exception as e:
            util_session.set_value_in_session(request, session, 'file_id', None)
            logger.error(e)
            return render_show_files('File loading failed. Please try again later.')


@app_file_process.route('/delete_file')
def delete_file():
    util_session.populate_session(request, session)
    if not util_session.is_valid_session(request, session):
        return util_session.send_response(session, render_template("login.html", captcha_site_key=util_common.captcha_site_key))
    else:
        try:
            user_id = util_session.get_value_from_session(request, session, 'user_id')
            file_id = request.args.get('file_id', default=None, type=str)
            if file_id is not None:
                is_success, id, is_prod_info_avl, status = util_db.get_file_from_id(user_id, file_id)
                if is_success:
                    if id is not None:
                        if status != "IN-PROGRESS":
                            util_session.set_value_in_session(request, session, 'file_id', None)
                            if util_db.delete_file(user_id, file_id):
                                file_dir = os.path.join(util_file.get_root_dir(), str(user_id), file_id)
                                util_file.delete_dir(file_dir)
                                return render_show_files('')
                            else:
                                return render_show_files('File delete failed. Please try again later.')

                        else:
                            return render_show_files("File which selected is in IN-PROGRESS state. You can't delete "
                                                     "this file. Please retry after it move from IN-PROGRESS state")
                    else:
                        return render_show_files("File not exist or you are not the owner of the file. You can't delete"
                                                 " this file.")
                else:
                    return render_show_files('File delete failed. Please try again later.')
            else:
                return render_show_files('file_id missed in request. Please send the file_id to delete file.')
        except Exception as e:
            logger.error(e)
            return render_show_files('File delete failed. Please try again later.')
