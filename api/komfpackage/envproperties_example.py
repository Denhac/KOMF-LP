########################################
# Properties for the DB connection for RadioDJ
radiodj_db_server      = '127.0.0.1'
radiodj_db_user      = 'radiodj'
radiodj_db_password  = 'password'
radiodj_db_schema     = 'radiodj'

########################################
# Session-management variables
session_key         = 'sessionkey'

########################################
# File hosting services base directories
BASE_HOSTING_DIR      = '/files'
UPLOAD_PUBLIC_FOLDER  = '/files/public_upload'
UPLOAD_STAGING_FOLDER = '/files/staging'
UPLOAD_LIBRARY_FOLDER = '/files/library'

# List only the file types that are to be allowed for upload
ALLOWED_EXTENSIONS = set(['mp3'])

# Mapped folder on the client PC
RADIODJ_CLIENT_FOLDER = '\\\\127.0.0.1\\library'

########################################
# Variables primarily for the script importfromdom.py, but could be used by others
URL_FOR_DOM_FILELIST  = "https://www.tempuri.org/filelist.csv"
APACHE_USER_NAME      = "apache"
APACHE_GROUP_NAME     = "apache"
FADE_IN_SEC           = 0
FADE_OUT_SEC          = 2

ERROR_FROM_EMAIL = 'no@noreply.com'
ERROR_TO_EMAIL_LIST = ['no@noreply.com']

########################################
# Variables primarily for the script importfromarchive.org.py, but could be used by others
ARCHIVE_ORG_QUERY_URL = "https://archive.org/advancedsearch.php?"
TRANSCODE_FOLDER      = '/files/transcode'

########################################
# Logging files definitions
API_LOG_FILE          = '/var/www/log/apifunctions.log'
IMPORT_LOG_FILE       = '/var/www/log/importfromdom.log'

########################################
# Used by the text-to-speech engine to detect profanity
ENC_PROFANITY         = 'nahf, nefr, nefrubyr, nff, nff-ung, nff-wnoore , nff-cvengr, nffont, nffonaqvg, nffonatre, nffovgr, nffpybja, nffpbpx, nffpenpxre, nffrf, nffsnpr, nffshpx, nffshpxre, nfftboyva, nffung, nffurnq, nffubyr, nffubccre, nffwnpxre, nffyvpx, nffyvpxre, nffzbaxrl, nffzhapu, nffzhapure, nffavttre, nffcvengr, nfffuvg, nfffubyr, nfffhpxre, nffjnq, nffjvcr, nkjbhaq, onzcbg, onfgneq, ornare, ovgpu, ovgpunff, ovgpurf, ovgpugvgf, ovgpul, oybj, oybjwbo, obyybpxf, obyybk, obare, oebgureshpxre, ohyyfuvg, ohzoyrshpx, ohgg, ohggshpxn, ohggshpxre, pnzry, pnecrgzhapure, purfgvpyr, puvap, puvax, pubnq, pubqr, pyvg, pyvgsnpr, pyvgshpx, pyvgbevf, pyhfgreshpx, pbpx, pbpxnff, pbpxovgr, pbpxohetre, pbpxsnpr, pbpxshpxre, pbpxurnq, pbpxwbpxrl, pbpxxabxre, pbpxznfgre, pbpxzbatyre, pbpxzbatehry, pbpxzbaxrl, pbpxzhapure, pbpxabfr, pbpxahttrg, pbpxfuvg, pbpxfzvgu, pbpxfzbxr, pbpxfzbxre, pbpxfavssre, pbpxfhpxre, pbpxjnssyr, pbbpuvr, pbbpul, pbba, pbbgre, penpxre, phz, phzohooyr, phzqhzcfgre, phzthmmyre, phzwbpxrl, phzfyhg, phzgneg, phaavr, phaavyvathf, phag, phagnff, phagsnpr, phagubyr, phagyvpxre, phagent, phagfyhg, qntb, qnza, qrttb, qvpx, qvp, qvpxont, qvpxorngref, qvpxsnpr, qvpxshpx, qvpxshpxre, qvpxurnq, qvpxubyr, qvpxwhvpr, qvpxzvyx, qvpxzbatre, qvpxf, qvpxfync, qvpxfhpxre, qvpxfhpxvat, qvpxgvpxyre, qvpxjnq, qvpxjrnfry, qvpxjrrq, qvpxjbq, qvxr, qvyqb, qvcfuvg, qbbpuont, qbbxvr, qbhpur, qbhpur-snt, qbhpuront, qbhpurjnssyr, qhznff, qhzo, qhzonff, qhzoshpx, qhzofuvg, qhzfuvg, qlxr, snt, sntont, sntshpxre, snttvg, snttbg, snttbgpbpx, sntgneq, sngnff, sryyngvb, srygpu, synzre, shpx, shpxnff, shpxont, shpxobl, shpxoenva, shpxohgg, shpxohggre, shpxrq, shpxre, shpxrefhpxre, shpxsnpr, shpxurnq, shpxubyr, shpxva, shpxvat, shpxahg, shpxahgg, shpxbss, shpxf, shpxfgvpx, shpxgneq, shpxgneg, shpxhc, shpxjnq, shpxjvg, shpxjvgg, shqtrcnpxre, tnl, tnlnff, tnlobo, tnlqb, tnlshpx, tnlshpxvfg, tnlybeq, tnlgneq, tnljnq, tbqqnza, tbqqnzavg, tbbpu, tbbx, tevatb, thvqb, unaqwbo, uneq, urro, uryy, ub, ubr, ubzb, ubzbqhzofuvg, ubaxrl, uhzcvat, wnpxnff, wntbss, wnc, wrex, wrexnff, wvtnobb, wvmm, whatyr, whatyrohaal, xvxr, xbbpu, xbbgpu, xenhg, xhag, xlxr, ynzrnff, yneqnff, yrfovna, yrfob, yrmmvr, zpsnttrg, zvpx, zvatr, zbgunshpxn, zbgunshpxva, zbgureshpxre, zbgureshpxvat, zhss, zhssqvire, zhatvat, arteb, avtnobb, avttn, avttre, avttref, avtyrg, ahg, ahgfnpx, cnxv, cnabbpu, crpxre, crpxreurnq, cravf, cravfonatre, cravfshpxre, cravfchssre, cvff, cvffrq, cvffrq, cvffsyncf, cbyrfzbxre, cbyybpx, cbba, cbbanav, cbbanal, cbbagnat, cbepu, cbepuzbaxrl, cevpx, chanaal, chagn, chffvrf, chffl, chfflyvpxvat, chgb, dhrrs, dhrre, dhrreonvg, dhrreubyr, erabo, evzwbo, ehfxv, fnaq, fnaqavttre, fpuybat, fpebgr, fuvg, fuvgnff, fuvgont, fuvgonttre, fuvgoenvaf, fuvgoerngu, fuvgpnaarq, fuvgphag, fuvgqvpx, fuvgsnpr, fuvgsnprq, fuvgurnq, fuvgubyr, fuvgubhfr, fuvgfcvggre, fuvgfgnva, fuvggre, fuvggvrfg, fuvggvat, fuvggl, fuvm, fuvmavg, fxnax, fxrrg, fxhyyshpx, fyhg, fyhgont, fzrt, fangpu, fcvp, fcvpx, fcybbtr, fcbbx, fhpxnff, gneq, grfgvpyr, guhaqrephag, gvg, gvgshpx, gvgf, gvgglshpx, gjng, gjngyvcf, gjngf, gjngjnssyr, hapyrshpxre, in-w-w, int, intvan, inwnlwnl, iwnlwnl, jnax, jnaxwbo, jrgonpx, juber, juberont, jubersnpr, jbc'

# These properties are loaded by DenhacEmailLibrary.py:
smtp_server         = 'smtp.gmail.com'
smtp_port            = 465
smtp_user           = 'emailuser'
smtp_password       = 'emailpass'

########################################
# Used by apifunctions, /updateschedules and /deleteschedules services, to restrict access
#schedule_allowed_ips = ['127.0.0.1','192.168.1.10']
#                      The test machine
# Replacing the IP list with this instead:
komf_password_hash = 'pbkdf2:sha1:1000$bnMTi7qI$5f215a8d1c82bc2482ce45f66e2725114683755d'
# In test, this hash is 'password'

# Session-management variables
session_key         = 'sessionkey'

# URLs to receive metadata updates as songs rotate
send_to_radiorethink = True
radiorethink_url = 'http://tempuri.org'

send_to_icecast = True
icecast_url = 'http://tempuri.org'
icecast_user = 'user'
icecast_password = 'password'
