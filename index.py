import json
from flask import (Flask,render_template, request, url_for )
from flask_dynamo import Dynamo
import boto3
from werkzeug.exceptions import abort

app = Flask(__name__)

app.config['AWS_REGION']='eu-west-1'
app.config['DYNAMO_TABLES'] = [
    {
         "TableName":'CHD-sourcing-assistant-projects-azad',
         "KeySchema":[dict(AttributeName='username', KeyType='HASH')],
         "AttributeDefinitions" :[dict(AttributeName='abad', AttributeType='S')],
         "ProvisionedThroughput":dict(ReadCapacityUnits=50, WriteCapacityUnits=5)
    }
 ]

dynamo = Dynamo(app)
table = dynamo.tables[app.config['DYNAMO_TABLES'][0]['TableName']]

ALLOWED_EXTENSIONS = set(['pdf', 'mp3'])


def allowed_file(filename):
    tmp = ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)
    return tmp


@app.route('/')
def index():
    response = table.scan(Limit=10)
    projects = table.scan()
    return render_template('index.html', details=response['Items'], projects=projects['Items'])


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
        files = request.files.getlist("file[]")
        # if user does not select file, browser also
        # submit an empty part without filename
        file_names = []
        for file in files:
            if allowed_file(file.filename):
                # s3 = boto3.resource('s3')
                # folder_name = str(datetime.now().strftime('%m-%d-%y-%H-%M-%S'))
                # path = folder_name + '/' + folder_name + '.mp3'
                # s3object = s3.Object(app.config['bucket_name'], path)
                # s3object.put(Body=file)
                # global g_filename
                # g_filename = folder_name
                file_names.append(file.filename)
            else:
                file_names.append('invalid file')
        return render_template('new_project.html', data=file_names)
    else:
        return render_template('new_project.html', data="not attached")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
