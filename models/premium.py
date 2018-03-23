#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 14:15 2018
@author: ernstoldenhof

# NB: base_rate should go into the db
# NB: naming of parameters etcetera: make consistent with DB
(or import from DB)

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
                                  base_rate,
                                  db_path,
                                  AZURE_SERVER,
                                  AZURE_USERNAME,
                                  AZURE_PASSWORD,
                                  AZURE_DATABASE,
                                  AZURE_PORT)

## Define parameters
pricing_parameter_ref_keys = ['start_country',
                              'end_country',
                              'airport',
                              'container_type',
                              'start_trucking_time',
                              'end_trucking_time',
                              'temperature_range'
                              ]

pricing_parameter_bus_keys = ['forwarder',
                              'ground_handler']

valid_pricing_parameter_type_names = ['country', 'airport', 'container type']
csv_list_keys = ['airport', 'ground_handler'] # keys for items that need unpacking
driver= '{ODBC Driver 13 for SQL Server}'

def multi_query_azure(sql_list, vals_list):
    # send a list of queries, making only a single db connection for speed
    db_connection = pyodbc.connect((r"DRIVER={driver};PORT={port};SERVER={server};"
                           r"DATABASE={database};UID={username};PWD={password}").format(driver=driver,
                                                    port=AZURE_PORT,
                                                    server=AZURE_SERVER,
                                                    database=AZURE_DATABASE,
                                                    username=AZURE_USERNAME,
                                                    password=AZURE_PASSWORD))
    cursor = db_connection.cursor()
    try:
        for sql, vals in zip(sql_list, vals_list):
            cursor.execute(sql, vals)
            columns = [column[0] for column in cursor.description]
            row = cursor.fetchone()
            #columns_list.append(columns)
            #row_list.append(row)
            yield (columns, row)
    except Exception as e:
        print('Error in multi_query_azure: \n')
        print(e)
    finally:
        db_connection.close()

def calculate_premium(premium_request):
    """
    premium_request : a dictionary

    The contents of the request can be divided into two groups:
    1. elements that result in one parameter per element (multiplier for the premium)
      (airport, container_type, start_country, ....)
    2. general elements that in another way determine the premium or parameter values
      (sum_insured, timestamp, temperature_range, product_id)

    The first group of elements can be subdivided into:
    1.  a)  business partners.
            (forwarder, ground_handler)
        b)  other pricing parameters
            (airport, container_type, start_country, end_country, temperature_range,
            start_trucking_time, end_trucking_time)

    Other pricing parameters depend only on product_id
       (administration, taxes, fees, Base factor)

    This function calculates the premium using the following steps:
       - data transformations (comma-separated strings to list, string to date)
       - retrieving the elements in 2. (sum_insured, timestamp, ... etc)
       - iterate over the elements of 1.b to retrieve the parameters from the DB, and append parameters to list
       - iterate over the elements of 1.a to retrieve the parameters from the DB, and append parameters to list
       - iterate over the other_pricing_params (administration, fees, ) to retrieve those pricing parameters,
         and append to another list
       - calculate the premium using all collected parameters
       - depending on the request, return only the premium or the premium and the details
         (or a message, in case of error)

    """
    # 0. Initializing/setting variables
    include_details = True if ('details' in premium_request) and \
        (premium_request['details'] == 1) else False

    # column names for the Pricing_Param_Ref_Data table
    param_colnames = ['Pricing_Parameter_Value', 'Reference_Data_Name',
                        'Pricing_Parameter_Type_Name']

    # column names for the Pricing_Param_Bus_Partner table
    bus_colnames = ['Pricing_Parameter_Value', 'Business_Partner_Name',
                        'Pricing_Parameter_Type_Name']

    # 1. Data transformation and retrieving elements

    # split comma-separated strings, put into list
    for key in csv_list_keys:
        premium_request[key] = [int(r) for r in
            premium_request[key].split(',')]

    # timestamp. input is a string: 'yyyy-mm-dd'. do datetime
    timestamp = datetime.strptime(premium_request['timestamp'], '%Y-%m-%d')

    # to string (for reply)
    timestamp_str = datetime.strftime(timestamp, '%Y-%m-%d')

    # product_id and amount
    product_id = premium_request['product_id']
    sum_insured = premium_request['sum_insured']

    # put into dictionary
    quote_reply = {'sum_insured': sum_insured,
                   'product_id': product_id,
                   'timestamp': timestamp_str,
                    'parameter_list': []}
    # 2. Iterate over elements of 1.b and 1.a
    # Loop through all items, to search for the "parameters"/premium multipliers
    sql_list, vals_list = [], []
    for key, parameter_ids in premium_request.items():

        # Make sure we can iterate over the parameter id's
        # (if list, fine, else: make single-item list)
        if not type(parameter_ids) == list:
            parameter_ids = [parameter_ids]

        # Test if this is a key that requires a parameter lookup
        # if not, skip it
        if key in pricing_parameter_ref_keys:
            sql = """ SELECT * FROM [dbo].[Pricing_Param_Ref_Data] WHERE
                    Reference_Data_ID = ? AND Product_ID = ? AND
                    Valid_From <= ? AND Valid_To > ?
                  """

        elif key in pricing_parameter_bus_keys:
            sql = """ SELECT * FROM [dbo].[Pricing_Param_Bus_Partner] WHERE
                    Business_Partner_ID = ? AND Product_ID = ? AND
                    Valid_From <= ? AND Valid_To > ?
                  """

        # when the key is one of the parameter keys, do the queries for the parameters
        if (key in pricing_parameter_ref_keys) or (key in pricing_parameter_bus_keys):

            for parameter_id in parameter_ids:
                vals = (parameter_id, product_id, timestamp, timestamp) #Timestamp not used yet!
                sql_list.append(sql)
                vals_list.append(vals)
        else:
            continue # for clarity
            
    for (columns, row) in multi_query_azure(sql_list, vals_list):


        # find the index of the row where the Pricing Parameter Value is located
        # NB: those strings should probably be in config
        try:
            pricing_param_value_index = [i for i, col_name in enumerate(columns)
                               if col_name ==  param_colnames[0]][0]
            ref_data_name_index = [i for i, col_name in enumerate(columns)
                               if col_name == param_colnames[1]][0]
            name_index = [i for i, col_name in enumerate(columns)
                               if col_name == param_colnames[2]][0]
        except:
            pricing_param_value_index = [i for i, col_name in enumerate(columns)
                               if col_name == bus_colnames[0]][0]
            ref_data_name_index = [i for i, col_name in enumerate(columns)
                               if col_name == bus_colnames[1]][0]
            name_index = [i for i, col_name in enumerate(columns)
                               if col_name == bus_colnames[2]][0]

        # Get the values
        pricing_param_value = row[pricing_param_value_index]
        ref_data_name = row[ref_data_name_index]
        pricing_param_type_name = row[name_index]

    # Append to the list

        quote_reply['parameter_list'].append({'type': key,
                            'pricing_param_type_name': pricing_param_type_name,
                            'pricing_param_value': pricing_param_value,
                                'ref_data_name': ref_data_name})





    # Process the obtained data to calculate the premium
    parameters = [item['pricing_param_value'] for item in quote_reply['parameter_list']
                  if 'pricing_param_value' in item.keys() ]
    # Multiply all parameters
    parameters_product = 1
    for par in parameters:
        parameters_product *= par
    premium = (premium_request['sum_insured'] * base_rate * parameters_product)
    if include_details:
        return (premium, quote_reply)
    else:
        return premium



if __name__ == '__main__':

    premium_request= {
      "sum_insured" : 360000,
      "product_id" : 1,
      "temperature_range" : 1405,
      "container_type": 1151,
      "forwarder" : 91,
      "start_trucking_time" : 1457,
      "start_country" : 1266,
      "airport" : "580, 647, 712",
      "ground_handler" : "10, 25, 58",
      "end_trucking_time" : 1455,
      "end_country" : 1293,
      "timestamp":"2018-01-28",
      "details" : 1
    }
    premium, quote_reply = calculate_premium(premium_request)
    print(premium)
    print(quote_reply)
