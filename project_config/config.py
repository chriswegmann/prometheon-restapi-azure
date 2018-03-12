import os
import data
from collections import namedtuple

## PATHS

DATA_PATH = data.__path__[0]
db_path = os.path.join(DATA_PATH, "pricing.db")
excel_path = os.path.join(DATA_PATH, "pricing_data.xlsx")

AZURE_PORT = 1433
AZURE_SERVER = os.environ['AZURE_SERVER']
AZURE_USERNAME = os.environ['AZURE_USERNAME']
AZURE_PASSWORD = os.environ['AZURE_PASSWORD']
AZURE_DATABASE = os.environ['AZURE_DATABASE']

## SQL PARAMS
table_name_list = ['MAPPING_PAR_REF_AIRPORT', 'MAPPING_PAR_REF_GROUND_HANDLER',
                   'PAR_AIRPORT', 'PAR_GROUND_HANDLER']

required_keys = ['sum_insured', 'timestamp', 'product_id']# Removed airports, ground_handlers

# Define namedtuple that links the table that contains the ID's and
# the parameter (multiplier) ID's with that that contains the parameters
# (multipliers)
TableNames = namedtuple('TableNames', 'table_a table_b column_name')

# Define the dict with the namedtuple TableNames as value, keys are those that
# should be present in the request
sql_parameter_tablename_dict = {}

# The following definitions are a duplicate from SQL.
# Leave only the keys, get rest from
sql_parameter_tablename_dict['airports'] = TableNames('MAPPING_PAR_REF_AIRPORT',
                            'PAR_AIRPORT',
                            'AIRPORT_ID')

sql_parameter_tablename_dict['ground_handlers'] = TableNames('MAPPING_PAR_REF_GROUND_HANDLER',
                            'PAR_GROUND_HANDLER',
                            'GROUND_HANDLER_ID')

## MISCELLANEOUS
base_rate = 1.E-3 # This should be in the database in its own table, with FROM, TO
