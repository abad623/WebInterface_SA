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


if __name__ == '__main__':
    app.run(debug=True, port=4000)