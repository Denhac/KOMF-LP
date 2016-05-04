########################################
# Properties for the DB connection for RadioDJ
radiodj_db_server 	 = '127.0.0.1'
radiodj_db_user 	 = 'user'
radiodj_db_password  = 'pass'
radiodj_db_schema	 = 'schema'

########################################
# File hosting services base directories
BASE_HOSTING_DIR      = '/files'
UPLOAD_PUBLIC_FOLDER  = '/files/public_upload'
UPLOAD_STAGING_FOLDER = '/files/staging'
UPLOAD_LIBRARY_FOLDER = '/files/library'

ALLOWED_EXTENSIONS = set(['mp3'])

########################################
URL_FOR_DOM_FILELIST  = "https://www.tempuri.org/"
APACHE_USER_NAME  = "apache"
APACHE_GROUP_NAME = "apache"
