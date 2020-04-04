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

    # This method is overridden by the child classes
    @abstractmethod
    def connect(self):
        pass

    def escapeString(self, str):
        return self._connect.escape_string(str)

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
        self.connect()
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
        sql = "select id from genre where name = %s"
        rows = self.executeQueryGetAllRows(sql, [name])

        # If genre not found, find the ID for "UNKNOWN" instead
        if len(rows) == 0:
            sql = "select id from genre where name = 'UNKNOWN'"
            rows = self.executeQueryGetAllRows(sql, None)

        return rows[0]['id']

    def getSubcategoryIdByName(self, name):
        sql = "select ID from subcategory where name = %s"
        rows = self.executeQueryGetAllRows(sql, [name])

        # If subcategory not found, find the ID for "UNKNOWN" instead
        if len(rows) == 0:
            sql = "select ID from subcategory where name = 'UNKNOWN'"
            rows = self.executeQueryGetAllRows(sql, None)
        return rows[0]['ID']

    def upsertSongs(self, path, song_type, id_subcat, id_genre, duration, artist, album, year, copyright, title, publisher, composer, cue_times, enabled, comments, play_limit, limit_action):
        sql = "CALL `komf_upsert_songs`(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        self.executeQueryNoResult(sql, [path, song_type, id_subcat, id_genre, duration, artist, album, year, copyright, title, publisher, composer, cue_times, enabled, comments, play_limit, limit_action])

    def getSongByPath(self, path):
        sql = "SELECT * FROM songs WHERE path = %s"
        rows = self.executeQueryGetAllRows(sql, [path])
        return rows[0]

    def setSongExtended(self, song_id, bayesian, mean, explicit, post_date):
        sql = "CALL `komf_upsert_song_extended`(%s,%s,%s,%s,%s)"
        self.executeQueryNoResult(sql, [song_id, bayesian, mean, explicit, post_date])

    def deleteSong(self, path):
        sql = "CALL `komf_delete_song`(%s)"
        self.executeQueryNoResult(sql, [path])

    def autoUpdatePath(self):
        sql = "UPDATE songs SET path = CONCAT('\\\\\\\\192.168.22.15\\\\library',mid(path,3)) where path like 'p:%'"
        self.executeQueryNoResult(sql, None)

    def getThemeblockTotals(self):
        sql = """SELECT s.name as themeblock, sum(r.duration)/60 as minutes 
                FROM radiodj.songs r
                JOIN subcategory s ON s.ID = r.id_subcat
                GROUP BY r.id_subcat
                ORDER BY minutes DESC
                """
        return self.executeQueryGetAllRows(sql, None)

    def getThemeblockEnabledTotals(self):
        sql = """SELECT s.name as themeblock, sum(r.duration)/60 as minutes 
                FROM radiodj.songs r
                JOIN subcategory s ON s.ID = r.id_subcat AND r.enabled = 1
                GROUP BY r.id_subcat
                ORDER BY minutes DESC
                """
        return self.executeQueryGetAllRows(sql, None)

    def getThemeblockDisabledTotals(self):
        sql = """SELECT s.name as themeblock, sum(r.duration)/60 as minutes 
                FROM radiodj.songs r
                JOIN subcategory s ON s.ID = r.id_subcat AND r.enabled = 0
                GROUP BY r.id_subcat
                ORDER BY minutes DESC
                """
        return self.executeQueryGetAllRows(sql, None)

    def getGenreTotals(self):
        sql = """SELECT g.name as genre, sum(r.duration)/60 as minutes
                FROM radiodj.songs r
                JOIN subcategory s ON s.ID = r.id_subcat
                JOIN genre g ON g.id = r.id_genre
                GROUP BY g.name
                ORDER BY minutes DESC"""
        return self.executeQueryGetAllRows(sql, None)

    def getGenreEnabledTotals(self):
        sql = """SELECT g.name as genre, sum(r.duration)/60 as minutes
                FROM radiodj.songs r
                JOIN subcategory s ON s.ID = r.id_subcat AND r.enabled = 1
                JOIN genre g ON g.id = r.id_genre
                GROUP BY g.name
                ORDER BY minutes DESC"""
        return self.executeQueryGetAllRows(sql, None)

    def getGenreDisabledTotals(self):
        sql = """SELECT g.name as genre, sum(r.duration)/60 as minutes
                FROM radiodj.songs r
                JOIN subcategory s ON s.ID = r.id_subcat AND r.enabled = 0
                JOIN genre g ON g.id = r.id_genre
                GROUP BY g.name
                ORDER BY minutes DESC"""
        return self.executeQueryGetAllRows(sql, None)

    def getEnabledTotals(self):
        sql = """SELECT s.enabled, sum(s.duration)/60 as minutes
                FROM radiodj.songs s
                GROUP BY s.enabled
                ORDER BY minutes DESC"""
        return self.executeQueryGetAllRows(sql, None)

    def getUnknownSongs(self):
        sql = "select * from songs where id_genre = 60 or id_subcat = 11"
        return self.executeQueryGetAllRows(sql, None)

    def getSchedules(self):
        sql = "SELECT * FROM komf_scheduled_shows"
        return self.executeQueryGetAllRows(sql, None)

    def upsertSchedule(self, playlist_id, project, day, time_string):
        if playlist_id:
            sql = "CALL komf_upsert_komf_scheduled_shows(%s, %s, %s, %s);"
            return self.executeQueryNoResult(sql, [playlist_id, project, day, time_string])
        else:
            sql = "CALL komf_upsert_komf_scheduled_shows(null, %s, %s, %s);"
            return self.executeQueryNoResult(sql, [project, day, time_string])

    def deleteSchedule(self, playlist_id):
        sql = "DELETE FROM komf_scheduled_shows WHERE playlist_id = %s"
        return self.executeQueryNoResult(sql, [playlist_id])

    def getVerifiedSchedules(self):
        sql = "SELECT * FROM komf_scheduled_show_verification"
        return self.executeQueryGetAllRows(sql, None)

    def getRotationSchedules(self):
        sql = "select a.*, b.name from komf_rotation_schedule a inner join subcategory b where b.ID = a.ThemeBlockID"
        return self.executeQueryGetAllRows(sql, None)

    def deleteRotationSchedule(self, rotation_id):
        sql = "DELETE FROM komf_rotation_schedule WHERE ID = %s"
        return self.executeQueryNoResult(sql, [rotation_id])

    def getThemeBlocksForUserSelection(self):
        sql = "SELECT * FROM subcategory WHERE ID <= 10"
        return self.executeQueryGetAllRows(sql, None)

    def addRotationSchedule(self, RotationName, StartTime, ThemeBlockID, Days, KickoffTrackID):
        if KickoffTrackID:
            sql = "INSERT INTO komf_rotation_schedule(RotationName, StartTime, ThemeBlockID, Days, KickoffTrackID) values (%s,%s,%s,%s,%s)"
            return self.executeQueryNoResult(sql, [RotationName, StartTime, ThemeBlockID, Days, KickoffTrackID])
        else:
            sql = "INSERT INTO komf_rotation_schedule(RotationName, StartTime, ThemeBlockID, Days) values (%s,%s,%s,%s)"
            return self.executeQueryNoResult(sql, [RotationName, StartTime, ThemeBlockID, Days])

    def updateAutoRotation(self):
        sql = "CALL komf_update_auto_rotation()"
        return self.executeQueryNoResult(sql, None)

    def getRotationVerification(self):
        sql = "SELECT * FROM komf_rotation_verification"
        return self.executeQueryGetAllRows(sql, None)

    def getScheduledShowVerification(self):
        sql = "select * from komf_scheduled_show_verification"
        return self.executeQueryGetAllRows(sql, None)

    def getKomfTrackSummary(self):
        sql = "select ks.*, s.path from komf_track_summary ks, songs s where s.ID = ks.songID"
        return self.executeQueryGetAllRows(sql, None)

    def addSetMetadata(self, metadata):
        sql = "INSERT INTO `setmetadata` (`metadata`) VALUES (%s)"
        return self.executeQueryNoResult(sql, [metadata])

    def getSetMetadata(self, is_processed):
        sql = "SELECT * FROM `setmetadata` WHERE `processed` = %d"
        return self.executeQueryGetAllRows(sql, [is_processed])

    def setSetMetadataProcessed(self, id, processed):
        sql = "UPDATE `setmetadata` SET `processed`=%d WHERE ID = %d"
        return self.executeQueryNoResult(sql, [processed, id])

    def setLastImportDatetime(self):
        sql = "CALL komf_update_last_import_datetime()"
        return self.executeQueryNoResult(sql, None)

    def setLastMaintenanceDatetime(self):
        sql = "CALL komf_update_last_maintenance_datetime()"
        return self.executeQueryNoResult(sql, None)

    def getLastImportDatetime(self):
        sql = """SELECT TIMESTAMPDIFF(SECOND, last_import_datetime, NOW()) AS seconds_since_last_import,
        		 TIMESTAMPDIFF(SECOND, last_maintenance_datetime, NOW()) AS seconds_since_last_maintenance,
                 a.*
                 FROM komf_last_import_datetime a"""
        return self.executeQueryGetAllRows(sql, None)

    def deleteSongImportFailures(self):
        sql = "TRUNCATE TABLE komf_song_import_failures"
        return self.executeQueryNoResult(sql, None)

    def setSongImportFailure(self, song_title, song_link, error_type, error_message, traceback):
        sql = "CALL komf_insert_song_import_failures(%s,%s,%s,%s,%s)"
        return self.executeQueryNoResult(sql, [song_title, song_link, error_type, error_message, traceback])

    def getSongImportFailures(self):
        sql = "SELECT * FROM komf_song_import_failures"
        return self.executeQueryGetAllRows(sql, None)
