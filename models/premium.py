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
import pyodbc
import sqlite3
import os.path

# from numpy import product as npproduct
# from numpy import array as nparray
from datetime import datetime

from project_config.config import (sql_parameter_tablename_dict,
                                  required_keys,
                                  base_rate,
                                  db_path,
                                  AZURE_SERVER,
                                  AZURE_USERNAME,
                                  AZURE_PASSWORD,
                                  AZURE_DATABASE,
                                  AZURE_PORT)

valid_pricing_parameter_type_names = ['country', 'airport', 'container type']
# NB: base_rate should go into the db


driver= '{ODBC Driver 13 for SQL Server}'

def calculate_premium(premium_request):
    """
    :premium_request : a dictionary

    Looks into the database to search for the parameters, and appends the
    results to a DataFrame.
    Returns the quote amount, and a list of dictionaries with detailed info
    """
    ## Assert that all required keys to calculate a premium are provided
    for key in required_keys:
        assert key in premium_request.keys(), ('Aborting: key "{}" missing in '
                                            'request'.format(key))

    ## Get values from request: timestamp, amount insured, product_id
    # timestamp
    try:
        # The following works when a list is given of [Y, M, D]
        timestamp = datetime(*premium_request['timestamp'])
    except:
        # When input is a string: 'yyyy-mm-dd'
        timestamp = datetime.strptime(premium_request['timestamp'], '%Y-%m-%d')

    # To filter valid_from/to (not implemented yet)
    timestamp_str = datetime.strftime(timestamp, '%Y-%m-%d')

    # product_id and amount
    product_id = premium_request['product_id']
    sum_insured = premium_request['sum_insured']

    # init the list that contains the elements that determine the premium
    quote_reply = [{'sum_insured': sum_insured,
                   'product_id': product_id,
                   'timestamp': timestamp_str}]

    # Loop through all items, to search for the "parameters"/premium multipliers
    for key, parameter_ids in premium_request.items():

        # Test if this is a key that requires a parameter lookup
        # if not, skip it
        if key in valid_pricing_parameter_type_names:
            sql = """ SELECT * FROM [dbo].[Pricing_Param_Ref_Data] WHERE
                    Reference_Data_ID = ? and Product_ID = ?
                  """

            # Make database connection
            db_connection = pyodbc.connect((r"DRIVER={driver};PORT={port};SERVER={server};"
                           r"DATABASE={database};UID={username};PWD={password}").format(driver=driver,
                                                    port=AZURE_PORT,
                                                    server=AZURE_SERVER,
                                                    database=AZURE_DATABASE,
                                                    username=AZURE_USERNAME,
                                                    password=AZURE_PASSWORD))
            # Create database cursor
            cursor = db_connection.cursor()
            try:
                for parameter_id in parameter_ids:
                    vals = (parameter_id, product_id) #Timestamp not used yet!
                    cursor.execute(sql, vals)

                    # fetch the result
                    columns = [column[0] for column in cursor.description]

                    # find the index of the row where the Pricing Parameter Value is located
                    # NB: those strings should probably be in config
                    pricing_param_value_index = [i for i, col_name in enumerate(columns)
                                       if col_name == 'Pricing_Parameter_Value'][0]
                    ref_data_name_index = [i for i, col_name in enumerate(columns)
                                       if col_name == 'Reference_Data_Name'][0]
                    pricing_param_type_name_index = [i for i, col_name in enumerate(columns)
                                       if col_name == 'Pricing_Parameter_Type_Name'][0]

                    # Get the values
                    row = cursor.fetchone()
                    pricing_param_value = row[pricing_param_value_index]
                    ref_data_name = row[ref_data_name_index]
                    pricing_param_type_name = row[pricing_param_type_name_index]

                    # Append dictionaries to the list


                    quote_reply.append({'type': key,
                                        'pricing_param_type_name': pricing_param_type_name,
                                        'pricing_param_value': pricing_param_value,
                                        'ref_data_name': ref_data_name})
            except Exception as e:
                print(e)
                return {'message': ('parameter_id {} for key {} for date'
                                '{} not found').format(
                                    parameter_id, key, timestamp_str)}
            finally:
                db_connection.close()
        else:
            continue # for clarity

    # Process the obtained data to calculate the premium
    parameters = [item['pricing_param_value'] for item in quote_reply if 'pricing_param_value' in item.keys() ]
    # Multiply all parameters
    parameters_product = 1
    for par in parameters:
        parameters_product *= par
    premium = (premium_request['sum_insured'] * base_rate * parameters_product)
    return (premium, quote_reply)


# def calculate_premium(premium_request):
#     """
#     :premium_request : a dictionary
#
#     Looks into the database to search for the parameters, and appends the
#     results to a DataFrame.
#     Returns the quote amount, and a list of dictionaries with detailed info
#     """
#     # Assert that all required keys to calculate a premium are provided
#     for key in required_keys:
#         assert key in premium_request.keys(), ('Aborting: key "{}" missing in '
#                                             'request'.format(key))
#
#     # get the timestamp from the request
#     try:
#         # The following works when a list is given of [Y, M, D]
#         timestamp = datetime(*premium_request['timestamp'])
#     except:
#         # Expecting input as a string: 'yyyy-mm-dd'
#         timestamp = datetime.strptime(premium_request['timestamp'], '%Y-%m-%d')
#
#
#     # init the list that contains the elements that determine the premium
#     quote_reply = []
#
#     # Loop through all items, to search for the "parameters"/premium multipliers
#     for key, parameter_ids in premium_request.items():
#
#         # Test if this is a key that requires a parameter lookup
#         # if not, skip it altogether
#         if key in sql_parameter_tablename_dict.keys():
#             assert type(parameter_ids) == list, ('The values to determine the factors '
#                        'must be given as a list')
#
#             # Create the sql string for the key (airports, ground_handlers, ..)
#             # Use .format() together with the ._asdict() method of the
#             # named tuple to "pre-format" the string
#             # Use ?'s as placeholders (NB: for other sql servers,
#             # the placeholder syntax will be somewhat different)
#             sql = ('SELECT B.PARAMETER_VALUE FROM {table_a} AS A '
#                    'JOIN {table_b} AS B ON A.PARAMETER_ID = B.PARAMETER_ID '
#                    'WHERE A.{column_name} = ? AND '
#                    'B.VALID_FROM <= ? AND B.VALID_TO > ?').format(
#             **sql_parameter_tablename_dict[key]._asdict())
#
#             # Make database connection
#             db_connection = sqlite3.connect(db_path)
#
#             # Create database cursor
#             cursor = db_connection.cursor()
#             try:
#                 for parameter_id in parameter_ids:
#                     vals = (parameter_id, timestamp, timestamp)
#                     cursor.execute(sql, vals)
#
#                     # fetch the result
#                     factor = cursor.fetchone()[0]
#
#                     # Append to the list, by using a dictionary
#                     # awkward format (repeating amount and timestamp)
#                     # , improve when required format is better known
#                     timestamp_str = datetime.strftime(timestamp, '%Y-%m-%d')
#
#                     quote_reply.append({'date':timestamp_str,
#                                         'amount':premium_request['amount'],
#                                         'type':key,
#                                         'parameter_id':parameter_id,
#                                         'factor':factor })
#             except TypeError:
#                 return {'message': ('parameter_id {} for key {} for date'
#                                 '{} not found').format(
#                                     parameter_id, key, timestamp_str)}
#             finally:
#                 db_connection.close()
#
#     # Process the obtained data to calculate the premium
#     parameters = nparray([item['factor'] for item in quote_reply])
#     parameters_product = npproduct(parameters)
#     premium = (premium_request['amount'] * base_rate * parameters_product)
#     return (premium, quote_reply)
#
#
#
# def testquery_azure(premium_request):
#     """
#     Test function for Azure SQL
#
#     """
#     driver= '{ODBC Driver 13 for SQL Server}'
#     cnxn = pyodbc.connect((r"DRIVER={driver};PORT={port};SERVER={server};"
#                            r"DATABASE={database};UID={username};PWD={password}").format(driver=driver,
#                                                     port=AZURE_PORT,
#                                                     server=AZURE_SERVER,
#                                                     database=AZURE_DATABASE,
#                                                     username=AZURE_USERNAME,
#                                                     password=AZURE_PASSWORD))
#     cursor = cnxn.cursor()
#     # cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
#     cursor.execute('SELECT * FROM Reference_Data_Value WHERE Reference_Data_ID=575')
#     row = cursor.fetchone()
#     cnxn.close()
#     quote_reply = [{'date':'01-01-0000',
#                     'amount':row[9],
#                     'text': row[6],
#                     'type':'TEST_RESULT',
#                     'parameter_id': 575,
#                     'factor': '1.23456' }]
#     return (1234, quote_reply)


######################################################
### Tests           ##################################
#######################################################
# Define some tests here:
def do_tests():
    pass


if __name__ == '__main__':
    premium_request = { 'product_id': 1,
                        'sum_insured' : 360E3,
                        'container type' : [1147],
                        'airport' : [651, 652, 890],
                        'timestamp' : (2018, 1, 7),
                          'country': [1217]} #Y, M, D
    premium, quote_reply = calculate_premium(premium_request)
    print(premium)
    print(quote_reply)
