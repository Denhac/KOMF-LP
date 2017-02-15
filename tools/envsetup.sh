# Just started this.  Work in progress.
# Execute as root.

yum -y install httpd epel-release python-pip python-ldap MySQL-python mod_wsgi git mariadb-server wget ntp ntpdate ntp-doc
yum -y install python-pip  # No idea why it has to be separate, but it won't install with the list above
#yum -y update

yes | pip install --upgrade pip
yes | pip install flask flask-cors PyMySQL eyed3 gTTS


mkdir /var/www/{files,log}
chown -R apache:apache /var/www/{files,log}

touch /var/www/log/apifunctions.log
chmod 777 /var/www/log
chmod 666 /var/www/log/apifunctions.log

#adduser apiuser
## AS ROOT:
##   > visudo
##   Add this line:
##     apiuser    ALL=(ALL:ALL) ALL

systemctl enable mariadb httpd ntpd
systemctl start  mariadb httpd ntpd

systemctl disable firewalld
systemctl stop firewalld


cd /root
git clone https://github.com/Denhac/KOMF-LP

cp -r /root/KOMF-LP/api/ /var/www/.
cp    /root/KOMF-LP/configs/etc/httpd/conf.d/komfapi.conf /etc/httpd/conf.d/.
mv    /var/www/api/komfpackage/envproperties_example.py /var/www/api/komfpackage/envproperties.py

cd /root/KOMF-LP/sql
mysql < denhac_radiodj_setup_1_dbandusers.sql
mysql radiodj < denhac_radiodj_setup_2_radiodjschema_sps_and_data.sql


apachectl restart


# HUGE FRIGGING THANK YOU TO https://gist.github.com/icaliman/1ee56b7f3ed5abf0dec1
# (Installing ffmpeg and libmp3lame where they worked nicely together!)
# But with replacing this command:
# PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure \
#  --prefix="$HOME/ffmpeg_build" \
#  --extra-cflags="-I$HOME/ffmpeg_build/include" \
#  --extra-ldflags="-L$HOME/ffmpeg_build/lib" \
#  --bindir="$HOME/bin" \
#  --enable-libmp3lame