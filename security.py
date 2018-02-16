#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 16:12:27 2018

@author: ernst
"""
from werkzeug.security import safe_str_cmp #string comparison (dealing with unicode etc.)
from models.user import username_table, userid_table


def authenticate(username, password):
    user = username_table.get(username, None)#.get: can specify default value
    if user and safe_str_cmp(user.password, password):
        return user

def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)
