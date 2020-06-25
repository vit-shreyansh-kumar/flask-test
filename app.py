
# load os and flask libraries
import os
import datetime
from flask import jsonify
from flask import Flask, flash, request, redirect, url_for, render_template,Response

# custom import libraries
from werkzeug.utils import secure_filename
import pandas as pd

# custom variables
ALLOWED_EXTENSIONS = ['csv']
UPLOAD_FOLDER = 'files'

app = Flask(__name__)

#application cinfiguration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/',methods=['GET'])
def index():
    """
    renders the view.html
    :return: view.html
    """
    return render_template('view.html')


@app.route('/reverse',methods=['GET'])
def reverse():
    """
    read the number in the UI
    :return: reverse of the number
    """
    num = request.args.get('data')
    num = int(num)
    reverse = 0

    while num > 0:
        rem = num % 10
        reverse = reverse * 10 + rem
        num = num // 10

    return jsonify(
        data=reverse,
        status=200,
        message='success'
    )


@app.route('/upload_csv',methods=['POST'])
def upload_csv():
    """
    Upload the csv files to the files folder
    :return:
    """
    try:
        if request.method == 'POST':
            if 'file' not in request.files:
                return jsonify(
                    data='',
                    status=200,
                    message='No files selected to upload'
                )

            else:
                file = request.files['file']
                if not file.filename:
                    return jsonify(
                        data='',
                        status=200,
                        message='No files selected to upload'
                    )

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    return jsonify(
                        status=201,
                        success=True,
                        message="Successfully Uploaded."
                    )
    except Exception as e:
        return jsonify(
            status=401,
            success=False,
            message="Error in uploaded",
            error=str(e)
        )

@app.route('/read_csv',methods=['GET'])
def read_csv():
    """
    Reads the csv files from the recently uploaded csv files
    :return: json format of csv
    """

    file_path = os.path.join(app.config['UPLOAD_FOLDER'],'sales.csv')
    file_data_frame = pd.read_csv(file_path)
    sku = file_data_frame['SKU'].unique()
    sku_container=[
        {
            'name':sku[0],
            'data':list()
        },
        {
            'name':sku[1],
            'data':list()
        },
        {
            'name':sku[2],
            'data':list()
        }
                     ]

    months = []

    for _,data in file_data_frame.iterrows():

        sr = pd.Series([data['Date']])

        # get_month = sr.dt.month_name(locale='English')
        # months.append(get_month)

        if data['SKU'] == sku[0]:
            sku_container[0]['data'].append(data['Sales'])
        elif data['SKU'] == sku[1]:
            sku_container[1]['data'].append(data['Sales'])
        elif data['SKU'] == sku[2]:
            sku_container[2]['data'].append(data['Sales'])

    return jsonify(
        data=sku_container,
        status=200,
        message='Get Json data',
        success=True
    )


@app.route('/fetch_data_for_datatable',methods=['POST'])
def fetch_data_for_datatable():
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'sales.csv')
        file_data_frame = pd.read_csv(file_path)

        container_datatable = dict()
        container_datatable = list()

        for _,data in file_data_frame.iterrows():
            container_datatable.append({'Date':data['Date'],'SKU':data['SKU'],'Sales':data['Sales']})

        return jsonify(
            data=container_datatable,
            status=200,
            success=True,
            message="fetched data."
        )
    except Exception as e:
        print(e)
        return jsonify(
            data=[],
            status=401,
            success=False,
            message='No Data Found'
        )


if __name__ == "__main__":
    app.run(debug=True)
