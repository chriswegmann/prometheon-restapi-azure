
import sqlite3

# NB: class User is not a resource, but a helper. The API does not deal with
# this class directly
# A model is an internal representation of an object
# A resource is what the API interacts with


class UserModel(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id

users = [
    UserModel(1, '832l7xjj', 'dlTks7lK'),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}
