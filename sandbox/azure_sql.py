#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 10:22:02 2018

@author: ernst
"""
import pyodbc
server = 'prometheon.database.windows.net' 

database = 'Prometheon'
username = 'wegmannc'
password = 'Aphathi_96'
driver= '{ODBC Driver 13 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()
# cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
cursor.execute('SELECT * FROM Reference_Data_Value WHERE Reference_Data_ID=575')
allrows = cursor.fetchall()
cnxn.close()
print(allrows[:10])
