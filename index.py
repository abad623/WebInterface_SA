import json
from flask import (Flask,render_template, request, url_for )
from flask_dynamo import Dynamo
import errors
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
    response = table.scan()
    return render_template('index.html', details=response['Items'])

@app.route('/', methods=['POST'])
def my_form_post():

    if request.method == 'POST':
        project_id = request.form['prompt']

    if len(project_id) > 0:
            try:
                response = table.get_item(TableName='CHD-sourcing-assistant-projects-azad', Key={'proj_id': project_id.strip()})
                if "Item" in response:
                    return render_template('project_info.html', details=response['Item'])
                else:
                    return render_template('index.html', error=errors.errors_msg['EMPTY_REC'])
            except Exception as err:
                print(err)


    else:
        response = table.scan()
        return render_template('index.html', error=errors.errors_msg['EMPTY_BOX'], details=response['Items'])

    # data = url_for('static', filename='projtest.json')
    return render_template('index.html', projects= response['Item'])


@app.route('/project/<proj>')
def project(proj):
    details = url_for('static', filename='test.json')
    return render_template('project.html', details=details, proj=proj)



@app.route('/employee/<num>', methods=['GET'])
def home(num):
    pass
   # data = requests.get('https://jsonplaceholder.typicode.com/todos/'+str(num))
   # print(data.json())
   # return render_template('index.html', projects=data.json())


if __name__ == '__main__':
    app.run(debug=True, port=4000)