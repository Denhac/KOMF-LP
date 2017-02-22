#!/bin/bash
# DENHAC KOMF-LP env setup script
# digimonkey
# Feb 2017
#
# Designed to copy to a newly-installed CentOS server (by itself), then:
# > chmod +x envsetup.sh
# > ./envsetup.sh
#
# To prompt after any errors on important steps, run like this:
# > ./envsetup.sh debug
DEBUG=$1

# Function that displays a message and prompts before continuing, so the user can see errors
function checkresponse(){
	echo "***WARNING: $*"
	if [ "$DEBUG" == "debug" ]; then
		read -p "***Press [Enter] to Continue..."
	else
		echo "***debug off; automatically continuing..."
	fi
}

########################################################
# Script Starts Here
########################################################

# Check for root permissions
if [ "$EUID" -ne 0 ]; then
	echo 'Please sudo to run this script.'
	exit
fi

########################################################

echo 'Creating User...'
adduser apiuser
checkresponse 'Create user failed.'

########################################################

echo 'Installing/Updating packages...'
sudo yum -y install httpd epel-release python-pip python-ldap MySQL-python mod_wsgi git mariadb-server wget ntp ntpdate ntp-doc
sudo yum -y install python-pip  # No idea why it has to be separate, but it won't install with the list above
sudo yum -y update

yes | sudo pip install --upgrade pip
yes | sudo pip install flask flask-cors PyMySQL eyed3 gTTS

########################################################

echo 'Installing ffmpeg/libmp3lame...'
# HUGE FRIGGING THANK YOU TO https://gist.github.com/icaliman/1ee56b7f3ed5abf0dec1
# (Installing ffmpeg and libmp3lame where they worked nicely together!)
# But with replacing this command:
# PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure \
#  --prefix="$HOME/ffmpeg_build" \
#  --extra-cflags="-I$HOME/ffmpeg_build/include" \
#  --extra-ldflags="-L$HOME/ffmpeg_build/lib" \
#  --bindir="$HOME/bin" \
#  --enable-libmp3lame

if [ -d ~/ffmpeg_sources ]; then
	checkresponse 'Directory ~/ffmpeg_sources exists.  Skipping all ffmpeg steps.'
else
	# Get the dependencies:
	sudo yum -y install autoconf automake gcc gcc-c++ git libtool make nasm pkgconfig zlib-devel

	mkdir ~/ffmpeg_sources
	  
	# Install libmp3lame
	cd ~/ffmpeg_sources
	curl -L -O http://downloads.sourceforge.net/project/lame/lame/3.99/lame-3.99.5.tar.gz
	tar xzvf lame-3.99.5.tar.gz
	cd lame-3.99.5
	./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" --disable-shared --enable-nasm
	make
	make install
	make distclean

	# Install ffmpeg
	cd ~/ffmpeg_sources
	git clone --depth 1 git://source.ffmpeg.org/ffmpeg
	cd ffmpeg
	PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure \
	  --prefix="$HOME/ffmpeg_build" \
	  --extra-cflags="-I$HOME/ffmpeg_build/include" \
	  --extra-ldflags="-L$HOME/ffmpeg_build/lib" \
	  --bindir="$HOME/bin" \
	  --enable-libmp3lame
	make
	make install
	make distclean
	hash -r
fi

########################################################

echo 'Updating services...'
sudo systemctl enable mariadb httpd ntpd
sudo systemctl start  mariadb httpd ntpd

sudo systemctl disable firewalld
sudo systemctl stop firewalld

########################################################

echo 'Updating filesystem...'
sudo mkdir -p /var/www/{files,log}
sudo chown -R apache:apache /var/www/{files,log}

sudo touch /var/www/log/apifunctions.log
sudo chmod 777 /var/www/log
sudo chmod 666 /var/www/log/apifunctions.log
sudo chown apiuser:apiuser /var/www/log/apifunctions.log

########################################################

echo 'Installing code...'

if [ -d ~/KOMF-LP ]; then
	checkresponse 'KOMF-LP directory already exists; deleting and re-cloning.'
	rm -rf ~/KOMF-LP
fi

git clone https://github.com/Denhac/KOMF-LP ~/KOMF-LP

sudo cp -r /root/KOMF-LP/api/										/var/www/.
sudo cp    /root/KOMF-LP/configs/etc/httpd/conf.d/komfapi.conf		/etc/httpd/conf.d/.
sudo cp    /root/KOMF-LP/configs/etc/httpd/conf.d/komfpublic.conf	/etc/httpd/conf.d/.

if [ -f /var/www/api/komfpackage/envproperties.py ]; then
	checkresponse 'File /var/www/api/komfpackage/envproperties.py exists.  NOT overwriting...'
else
	sudo mv    /var/www/api/komfpackage/envproperties_example.py		/var/www/api/komfpackage/envproperties.py
fi

########################################################

echo 'Creating database schema...'
mysql < ~/KOMF-LP/sql/denhac_radiodj_setup_1_dbandusers.sql
checkresponse 'DB Core Setup Failed.'

mysql radiodj < ~/KOMF-LP/sql/denhac_radiodj_setup_2_radiodjschema_sps_and_data.sql
checkresponse 'DB RadioDJ Schema Setup Failed.'

########################################################

echo 'Updating SELinux...'
sudo setenforce 0
sudo sed -i 's/SELINUX=.*/SELINUX=disabled/g' /etc/selinux/config

########################################################

echo ''
echo '########################################################'
echo 'Installation Complete'
echo '########################################################'
echo 'Manually import data from the DB if necessary.'
echo 'Restart to complete installation!'
echo '########################################################'
