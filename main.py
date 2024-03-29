#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 23:03:49 2018

@author: ernst
"""
from flask import Flask
from flask_restful import Api

# from flask_jwt import JWT

from resources.quote import Quote, Quote_test
# from security import authenticate, identity

app = Flask(__name__)
app.secret_key = 'mothys9410prim'

## 1. Test (as per github demo)

# @app.route('/')
# def hello_world():
#    return 'Hello, World!'

## 2. Actual API

api = Api(app)

# jwt = JWT(app, authenticate, identity) #creates new endpoint: /auth
api.add_resource(Quote, '/quote')
api.add_resource(Quote_test, '/quote_test')




if __name__ == '__main__':
    app.run(port=5000, debug=True)
