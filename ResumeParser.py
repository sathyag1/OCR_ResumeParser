#!/usr/bin/env python
# coding: utf-8

#importing library
import traceback
import os
import requests
import io
import traceback
import logging
logging.getLogger().setLevel(logging.CRITICAL)
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS
from dotenv import load_dotenv
from elasticapm.contrib.flask import ElasticAPM
from elasticapm.handlers.logging import LoggingHandler
from datetime import datetime, date
from authlib.jose import jwt
from functools import wraps
import time
import BusinessLayer as BL

load_dotenv()

Service_Name = os.getenv('SERVICE_NAME')
Server_Url = os.getenv('SERVER_URL')
Secret_token = os.getenv('SECRET_TOKEN')
Environment = os.getenv('ENVIRONMENT')
log_level = os.getenv('LOG_LEVEL')

public_key = os.getenv('PUBLIC_KEY')


key = '-----BEGIN PUBLIC KEY-----\n' + public_key + '\n-----END PUBLIC KEY-----'
key_binary = key.encode('ascii')




def token_required(f):
    """ function for authenticating 
            using keyclock token
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers['Authorization']
        if not token:
            return jsonify({"message": "Token is missing "}), 401

        try:
            claims = jwt.decode(token, key_binary)
            claims.validate()
            if (claims is not None ) and (time.time() < claims['exp']):
                print("Token Verified!!! ")

            else:
                print("Token is expired!!")

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return jsonify({'msg':'some token error!!!'}), 401
        return f(*args, **kwargs)
    return decorated



#Flask app
app = Flask(__name__)

#Adding CORS
CORS(app)
cors = CORS(app, resources={ 
    r"/*": { 
        "Access_Control_Allow_Origin": "*",
        "origins": "*",
        "allowedHeaders" :'Content-Type, Authorization, Origin, X-Requested-With, Accept',
        "method":['GET','POST','PATCH','DELETE','PUT']
           }
})

app.config['ELASTIC_APM'] = {
    'SERVICE_NAME':Service_Name,
    'SERVER_URL': Server_Url,
    'SECRET_TOKEN': Secret_token,
    'ENVIRONMENT' : Environment,
    'LOG_LEVEL' : log_level 
}

apm = ElasticAPM(app)

# Custom middleware to Protection header to all responses
@app.after_request
def add_security_headers(resp):
    resp.headers['Content-Security-Policy']='default-src \'self\''
    resp.headers['X-XSS-Protection'] = '1; mode=block'
    resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return resp


@app.route('/ResumeParser', methods=['POST'])
@token_required
def ResumeParser():
    try:
        resume_path = request.json['file_path']
        paragraph = BL.extraction_para_dict(BL.keywords_dict, resume_path)
        resume_extraction = BL.extracting_resume_dict(resume_path, paragraph)
        
        output = {**resume_extraction, **paragraph}
        return jsonify(output)
    
    except Exception as e:
        return jsonify({'msg':e })




'''API Call'''
if __name__ == '__main__':
    handler = LoggingHandler(client=apm.client)
    handler.setLevel(logging.WARN)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5000)
    # app.run(host='127.0.0.1', port=5000)
#     app.run()











