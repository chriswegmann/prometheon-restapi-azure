#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 14:15 2018
@author: ernstoldenhof

# NB: no need for premiumcalculator to be a class with a method
# .calculate_premium(). Keep it as a function for the time being

"""


######################################################
### Imports         ##################################
######################################################

## General imports
import sqlite3
import os.path
from numpy import array as nparray
from numpy import product as npproduct
from datetime import datetime

from project_config.config import (sql_parameter_tablename_dict,
                                  required_keys,
                                  base_rate,
                                  db_path)

# NB: base_rate should go into the db

def calculate_premium(premium_request):
    """
    :premium_request : a dictionary

    Looks into the database to search for the parameters, and appends the
    results to a DataFrame.
    Returns the quote amount, and a list of dictionaries with detailed info
    """
    # Assert that all required keys to calculate a premium are provided
    for key in required_keys:
        assert key in premium_request.keys(), ('Aborting: key "{}" missing in '
                                            'request'.format(key))

    # get the timestamp from the request
    try:
        # The following works when a list is given of [Y, M, D]
        timestamp = datetime(*premium_request['timestamp'])
    except:
        # Expecting input as a string: 'yyyy-mm-dd'
        timestamp = datetime.strptime(premium_request['timestamp'], '%Y-%m-%d')


    # init the list that contains the elements that determine the premium
    quote_reply = []

    # Loop through all items, to search for the "parameters"/premium multipliers
    for key, parameter_ids in premium_request.items():

        # Test if this is a key that requires a parameter lookup
        # if not, skip it altogether
        if key in sql_parameter_tablename_dict.keys():
            assert type(parameter_ids) == list, ('The values to determine the factors '
                       'must be given as a list')

            # Create the sql string for the key (airports, ground_handlers, ..)
            # Use .format() together with the ._asdict() method of the
            # named tuple to "pre-format" the string
            # Use ?'s as placeholders (NB: for other sql servers,
            # the placeholder syntax will be somewhat different)
            sql = ('SELECT B.PARAMETER_VALUE FROM {table_a} AS A '
                   'JOIN {table_b} AS B ON A.PARAMETER_ID = B.PARAMETER_ID '
                   'WHERE A.{column_name} = ? AND '
                   'B.VALID_FROM <= ? AND B.VALID_TO > ?').format(
            **sql_parameter_tablename_dict[key]._asdict())

            # Make database connection
            db_connection = sqlite3.connect(db_path)

            # Create database cursor
            cursor = db_connection.cursor()
            try:
                for parameter_id in parameter_ids:
                    vals = (parameter_id, timestamp, timestamp)
                    cursor.execute(sql, vals)

                    # fetch the result
                    factor = cursor.fetchone()[0]

                    # Append to the list, by using a dictionary
                    # awkward format (repeating amount and timestamp)
                    # , improve when required format is better known
                    timestamp_str = datetime.strftime(timestamp, '%Y-%m-%d')

                    quote_reply.append({'date':timestamp_str,
                                        'amount':premium_request['amount'],
                                        'type':key,
                                        'parameter_id':parameter_id,
                                        'factor':factor })
            except TypeError:
                return {'message': ('parameter_id {} for key {} for date'
                                '{} not found').format(
                                    parameter_id, key, timestamp_str)}
            finally:
                db_connection.close()

    # Process the obtained data to calculate the premium
    parameters = nparray([item['factor'] for item in quote_reply])
    parameters_product = npproduct(parameters)
    premium = (premium_request['amount'] * base_rate * parameters_product)
    return (premium, quote_reply)





######################################################
### Tests           ##################################
#######################################################
# Define some tests here:
def do_tests():
    pass


if __name__ == '__main__':
    premium_request = {
                    'amount' : 360E3,
                    'ground_handlers' : [1, 5, 10],
                    'airports' : [650, 652, 890],
                    'timestamp' : (2018, 1, 7)} #Y, M, D
    premium, quote_reply = calculate_premium(premium_request)
    print(premium)
    print(quote_reply)
