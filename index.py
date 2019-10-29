import json
from flask import (Flask, render_template, request, url_for, redirect)
from flask_dynamo import Dynamo
import boto3
import requests
from werkzeug.exceptions import abort

app = Flask(__name__)

app.config['AWS_REGION'] = 'eu-west-1'
app.config['DYNAMO_TABLES'] = [
    {
         "TableName": 'CHD-sourcing-assistant-projects-azad',
         "KeySchema": [dict(AttributeName='username', KeyType='HASH')],
         "AttributeDefinitions": [dict(AttributeName=   'abad', AttributeType='S')],
         "ProvisionedThroughput": dict(ReadCapacityUnits=50, WriteCapacityUnits=5)
    }
 ]
app.config['AIRFLOW_SETTINGS'] = [
    {
        "HOST": 'http://localhost:5050',
        "DAG_ID": '1'
    }
]

dynamo = Dynamo(app)
table = dynamo.tables[app.config['DYNAMO_TABLES'][0]['TableName']]
uploaded = ""

# ALLOWED_EXTENSIONS = set(['pdf', 'mp3'])


def allowed_file(filename):
    tmp = ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)
    return tmp


@app.route('/')
def index():
    response = table.scan(Limit=10)
    projects = table.scan()
    msg = ""
    global uploaded
    if uploaded != "":
        msg = uploaded
        uploaded = ""
    return render_template('index.html', details=response['Items'], projects=projects['Items'], msg=msg)


@app.route('/project/<proj>')
def project(proj):
    if len(proj) > 0:
        try:
            projects = table.scan()
            response = table.get_item(TableName='CHD-sourcing-assistant-projects-azad',
                                      Key={'proj_id': proj})
            if "Item" in response:
                return render_template('project.html', details=response['Item'], projects=projects['Items'])
            else:
                return render_template('index.html', error=errors.errors_msg['EMPTY_REC'])
        except Exception as err:
            print(err)


@app.route('/new/project/', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        # files = request.files.getlist("file[]")
        # # if user does not select file, browser also
        # # submit an empty part without filename
        # file_names = []
        # for file in files:
        #     if allowed_file(file.filename):
        #         # s3 = boto3.resource('s3')
        #         # folder_name = str(datetime.now().strftime('%m-%d-%y-%H-%M-%S'))
        #         # path = folder_name + '/' + folder_name + '.mp3'
        #         # s3object = s3.Object(app.config['bucket_name'], path)
        #         # s3object.put(Body=file)
        #         # global g_filename
        #         # g_filename = folder_name
        #         file_names.append(file.filename)
        #     else:
        #         file_names.append('invalid file')
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('architrave-sourcing-assistant')
        try:
            proj_name = request.form['project_name']
        except Exception as err:
            print(err)
        try:
            cust_name = request.form['customer_name']
        except Exception as err:
            print(err)
        path = cust_name + '/' + proj_name + '/'
        objs = list(bucket.objects.filter(Prefix=path))
        if len(objs) > 0 and objs[0].key == path:
            return render_template('new_project.html', msg="Project exists already for this customer")
        else:
            airflow_url = app.config['AIRFLOW_SETTINGS'][0]['HOST'] \
                          + '/api/experimental/dags/' \
                          + app.config['AIRFLOW_SETTINGS'][0]['DAG_ID'] \
                          + '/dag_runs'
            data = {"conf": {"customer": cust_name, "project_id": proj_name}}
            requests.post(airflow_url, json=data)
            global uploaded
            uploaded = "Project triggered, please wait until it appears in the list below"
            return redirect(url_for('index'))
    else:
        return render_template('new_project.html', data="not attached")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
