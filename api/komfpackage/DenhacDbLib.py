#!/usr/bin/python

# Import Python mysql bindings
#import MySQLdb
# To make this available, as root run: `pip install pymysql`
import pymysql

# File that stores environment-specific configs like URLs, usernames, etc.
import envproperties

# The Python 2.6-and-later way to define abstract base classes
# See http://dbader.org/blog/abstract-base-classes-in-python for further details why you want this.
from abc import ABCMeta, abstractmethod

# Other imports
from collections import defaultdict

class DenhacDb:
    __metaclass__   = ABCMeta
    _connect        = None
    _lastUsedCursor = None

    # This method is overrided by the child classes
    @abstractmethod
    def connect(self):
        pass

    def executeQueryNoResult(self, sql, params):
        self.connect()
        cursor = self._connect.cursor()
        cursor.execute(sql, params)
        self._connect.commit()
        cursor.close()

    def executeQueryGetCursor(self, sql, params):
        self.connect()
        self._lastUsedCursor = self._connect.cursor(pymysql.cursors.DictCursor)
        self._lastUsedCursor.execute(sql, params)
        return self._lastUsedCursor

    def executeQueryGetAllRows(self, sql, params):
        cur = self.executeQueryGetCursor(sql, params)
        return cur.fetchall()

    # Best practice to always explicitly close!
    def __del__(self):
        if self._lastUsedCursor is not None:
            self._lastUsedCursor.close()
        if self._connect is not None:
            self._connect.close()

class DenhacRadioDjDb(DenhacDb):
    def connect(self):
        if self._connect is None:
            self._connect = pymysql.connect(envproperties.radiodj_db_server,
                                            envproperties.radiodj_db_user,
                                            envproperties.radiodj_db_password,
                                            envproperties.radiodj_db_schema)

    def getGenreIdByName(self, name):
        self.connect()
        sql = "select id from genre where name = %s"
        return self.executeQueryGetAllRows(sql, [name])[0]['id']

    def upsertSongs(self, path, song_type, id_genre, duration, artist, album, year, copyright, title, publisher, composer):
        sql = "CALL `komf_upsert_songs`(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        self.executeQueryNoResult(sql, [path, song_type, id_genre, duration, artist, album, year, copyright, title, publisher, composer])
