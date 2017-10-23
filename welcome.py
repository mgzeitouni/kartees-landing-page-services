# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, jsonify, request
from cloudant.client import Cloudant
import json
from flask_cors import CORS
from flask.ext.cors import CORS, cross_origin

 
if 'VCAP_SERVICES' in os.environ:

     cloudant_service = json.loads(os.environ['VCAP_SERVICES'])['cloudantNoSQLDB'][0]
     credentials = cloudant_service['credentials']

else:
    from credentials import *
    credentials = cloudant_credentials




app = Flask(__name__)
CORS(app)

cache = {"requests":0, "data":[]}

@app.route('/new-email',  methods=['POST', 'OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def new_email():

    client = Cloudant(credentials['username'], credentials['password'], url="https://%s"%credentials['host'])
    # Connect to the account
    client.connect()

    status = False

    response = {}

    cache['requests']+=1

    # try:
    app_type="test"
    
    if 'Origin' in request.headers.keys() and 'prod' in request.headers['Origin']:
        app_type="prod"

    email = request.form['email']

    timestamp = request.form['timestamp']

    new_data = {"timestamp":timestamp,"email":str(email), "app_type":app_type}

    cache['data'].append(new_data)

    db = client['%s_emails' %app_type]

    doc = db["landing_page_emails"]

    doc['emails'].append(new_data)

    doc['requests']+=1

    doc.save()

    status=True

    response = {"db_type":app_type, "address":email, "message":"Email %s added to DB" %email}

    # except:

       # print ('Error with request')

    response['status'] = status


    return jsonify(response)

@app.route('/get-num-requests', methods=["GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_num_requests():

    return jsonify(cache)

@app.route('/')
def Welcome():
    return app.send_static_file('index.html')

@app.route('/myapp')
def WelcomeToMyapp():
    return 'Welcome again to my app running on Bluemix!'

@app.route('/api/people')
def GetPeople():
    list = [
        {'name': 'John', 'age': 28},
        {'name': 'Bill', 'val': 26}
    ]
    return jsonify(results=list)

@app.route('/api/people/<name>')
def SayHello(name):
    message = {
        'message': 'Hello ' + name
    }
    return jsonify(results=message)

port = os.getenv('PORT', '5001')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port), debug=True)
