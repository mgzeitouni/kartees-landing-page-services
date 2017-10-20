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
 
if 'VCAP_SERVICES' in os.environ:

     cloudant_service = json.loads(os.environ['VCAP_SERVICES'])['cloudantNoSQLDB'][0]
     credentials = cloudant_service['credentials']

else:
    from credentials import *
    credentials = cloudant_credentials


client = Cloudant(credentials['username'], credentials['password'], url="https://%s"%credentials['host'])
# Connect to the account
client.connect()

app = Flask(__name__)
CORS(app)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response




@app.route('/new-email',  methods=['POST', 'OPTIONS'])
def new_email():

    app_type="test"
    
    if 'kartees.com' in request.headers.origin:
        app_type="prod"

    email = request.form['email']

    db = client['%s_emails' %app_type]

    doc = db["landing_page_emails"]

    doc['emails'].append(str(email))

    doc.save()

    return jsonify({"db_type":app_type, "address":email, "message":"Email %s added to DB" %email})


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
