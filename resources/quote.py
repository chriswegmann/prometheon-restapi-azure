#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
class Quote is the contact point for the API:
    it receives a POST, parses arguments, runs the method that returns the
    premium, and returns the details of the premium through the API
"""

from flask_jwt import JWT, jwt_required
from flask import Flask, request
from flask_restful import Resource, reqparse
from models.premium import calculate_premium
{
  "sum_insured" : 360000,
  "product_id" : 1,
  "temperature_range" : 1405,
  "container_ type": 1151,
  "forwarder" : 91,
  "start_trucking_time" : 1457,
  "start_country" : 1266,
  "airport" : "580, 647, 712",
  "ground_handler" : "10, 25, 58",
  "end_trucking_time" : 1455,
  "end_country" : 1293,
  "timestamp":"2018-01-28"
}
class Quote(Resource):
    """
    Resource that uses SQLITE database to determine premium

    """
    # Define class attributes
    # parser for the JSON, to ensure the form of the JSON payload
    # NB: action='append' receives a list
    parser = reqparse.RequestParser()

    ## All integers
    parser.add_argument('sum_insured', type=float, required=True,
                        help="'sum_insured' cannot be left blank")
    parser.add_argument('product_id', type=int, required=True,
                        help="'product_id' cannot be left blank")
    parser.add_argument('temperature_range', type=int, required=True,
                        help="'temperature_range' cannot be left blank")
    parser.add_argument('container_type', type=int, required=True,
                        help="'container_type' cannot be left blank")
    parser.add_argument('forwarder', type=int, required=True,
                        help="'forwarder' cannot be left blank")
    parser.add_argument('start_trucking_time', type=int, required=True,
                        help="'start_trucking_time' cannot be left blank")
    parser.add_argument('start_country', type=int, action='append', required=True,
                        help="'start_country' cannot be left blank")
    parser.add_argument('end_trucking_time', type=int, required=True,
                        help="'end_trucking_time' cannot be left blank")
    parser.add_argument('end_country', type=int, required=True,
                        help="'end_country' cannot be left blank")
    parser.add_argument('details', type=int, required=False,
                        help="'details has to be an integer (1: include details)")

    ## All lists, formatted as comma separated strings
    parser.add_argument('airport', type=str, required=False,
                        help="'airport' has to be a string (comma separated array)")
    parser.add_argument('timestamp', type=str, required=True,
                        help="'timestamp' has to be a string (yyyy-mm-dd)")
    parser.add_argument('ground_handler', type=str, required=False,
                        help="'ground_handler' has to be a string (comma separated array)")
    @classmethod
    # @jwt_required() # Authentication required
    def post(cls):
        # First check if this is a valid post ("Error-first approach")
        # NB: next takes the first element from the generator

        premium_request = cls.parser.parse_args() #premium_request is a dict
        quote_reply = None
        reply = calculate_premium(premium_request)
        try:
            premium, quote_reply = reply
        except TypeError as e:
            # If there is only a single return item, an error has occurred
            # Then, the tuple unpacking will fail (with a TypeError)
            # The error is communicated by a message
            message = calculate_premium(premium_request)

        if not quote_reply is None:
            return {"premium": premium,
                    "details": quote_reply,
                    "premium_request": premium_request}, 200
        else:
            return message, 400

if __name__ == '__main__':
    pass
