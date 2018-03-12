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

class Quote(Resource):
    """
    Resource that uses SQLITE database to determine premium

    """
    # Define class attributes
    # parser for the JSON, to ensure the form of the JSON payload
    # NB: action='append' receives a list
    parser = reqparse.RequestParser()
    parser.add_argument('sum_insured', type=float, required=True,
                        help="'sum_insured' cannot be left blank")
    parser.add_argument('product_id', type=int, required=True,
                        help="'product_id' cannot be left blank")
    parser.add_argument('country', type=int, action='append', required=True,
                            help="'sum_insured' cannot be left blank")
    parser.add_argument('container type', type=int, required=True,
                            help="'container type' cannot be left blank")
    parser.add_argument('ground_handlers', type=int, action='append',
                        required=False)
    parser.add_argument('airport', type=int, action='append', required=False,
                        help="'airport' cannot be left blank")
    parser.add_argument('timestamp', type=str, required=True,
                        help="'timestamp' cannot be left blank")

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
            # If there is only a single return item, some error is returned
            # This is communicated by a message
            message = calculate_premium(premium_request)

        if not quote_reply is None:
            return {"premium": premium,
                    "details": quote_reply}, 200
        else:
            return message, 400

# class Quote_test(Resource):
#     """
#     Test resource that gets some arbitrary data from Azure to verify that the database
#     is accessible
#     """
#     # Define class attributes
#     # parser for the JSON, to ensure the form of the JSON payload
#     parser = reqparse.RequestParser()
#     parser.add_argument('amount', type=float, required=True,
#                         help="'Amount' cannot be left blank")
#     parser.add_argument('ground_handlers', type=int, action='append',
#                         required=True,
#                         help="'Ground handlers' cannot be left blank")
#     parser.add_argument('airports', type=int, action='append', required=True,
#                         help="'Airports' cannot be left blank")
#     parser.add_argument('timestamp', type=str, required=True,
#                         help="'Timestamp' cannot be left blank")
#
#     @classmethod
#     # @jwt_required() # Authentication required
#     def post(cls):
#         # First check if this is a valid post ("Error-first approach")
#         # NB: next takes the first element from the generator
#
#         premium_request = cls.parser.parse_args() #premium_request is a dict
#         quote_reply = None
#         try:
#             # premium, quote_reply = calculate_premium(premium_request)
#             premium, quote_reply = testquery_azure(premium_request)
#         except Exception as e:
#             print(e)
#             pass
#             # If quote_reply is missing, this means some error occurred
#             # This is communicated by a message
#             # NB: UNCOMMENT next line after test!
#             # message = calculate_premium(premium_request)
#
#         if not quote_reply is None:
#             return {"premium": premium,
#                     "details": quote_reply}, 200
#         else:
#             return message, 400

if __name__ == '__main__':
    pass
