#!/usr/bin/env bash
# Get password to be used with sudo commands
# Script still requires password entry during rvm and heroku installs
echo -n "Enter password to be used for sudo commands:"
read -s password

# Function to issue sudo command with password
function sudo-pw {
    echo $password | sudo -S $@
}

# Start configuration

# Install and configure mysql-server
sudo-pw apt-get -y update
sudo-pw debconf-set-selections <<< 'mysql-server mysql-server/root_password password root'
sudo-pw debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'
sudo-pw apt-get -y update
sudo-pw apt-get -y -y install mysql-server
sed -i "s/^bind-address/#bind-address/" /etc/mysql/my.cnf
mysql -u root -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root' WITH GRANT OPTION; FLUSH PRIVILEGES;"

echo -e "\n--- Setting up our MySQL user and db ---\n"
mysql -uroot -proot -e "CREATE DATABASE opendsa"
mysql -uroot -proot -e "GRANT ALL ON opendsa.* TO 'opendsa'@'localhost' IDENTIFIED BY 'opendsa'"

sudo-pw /etc/init.d/mysql restart

# Install OpenDSA-server
sudo-pw apt-get -y autoremove

sudo-pw apt-get -y install -y dkms     # For installing VirtualBox guest additions
sudo-pw apt-get -y install curl
sudo-pw apt-get -y install screen
sudo-pw apt-get -y install libxml2-dev libxslt-dev
sudo-pw apt-get -y install nodejs
sudo-pw apt-get -y install git
sudo-pw apt-get -y install libpq-dev
sudo-pw apt-get -y install vim
sudo-pw apt-get -y install emacs
sudo-pw apt-get -y install python
sudo-pw apt-get -y install python-feedvalidator
sudo-pw apt-get -y install python-software-properties
sudo-pw apt-get -y install libmysqlclient-dev
sudo-pw apt-get -y install libmariadbclient-dev
sudo-pw apt-get -y install libcurl4-gnutls-dev
sudo-pw apt-get -y install python-pip
sudo-pw apt-get -y install libevent-dev
sudo-pw apt-get -y install libffi-dev
sudo-pw apt-get -y install libssl-dev
sudo-pw apt-get -y install python-dev
sudo-pw apt-get -y install build-essential

sudo-pw apt-get -y update


# clone OpenDSA-server
# ####################
sudo-pw rm -rf /vagrant/OpenDSA-server
sudo-pw git clone https://github.com/OpenDSA/OpenDSA-server.git /vagrant/OpenDSA-server

# create link to assets
ln -s /vagrant/OpenDSA-server/ODSA-django/assets/* /vagrant/OpenDSA-server/ODSA-django/static



# Checkout NewKA branch
cd /vagrant/OpenDSA-server/
git checkout NewKA
cd /vagrant/OpenDSA-server/ODSA-django

# Create media folder
sudo-pw mkdir /vagrant/OpenDSA-server/ODSA-django/media
sudo-pw touch /vagrant/OpenDSA-server/ODSA-django/media/daily_stats.json

# Install requirements
sudo-pw pip install git+http://git@github.com/penzance/canvas_python_sdk#egg=canvas_sdk
sudo-pw pip install -r requirements.txt

# suncdb
python manage.py syncdb

# Run development server
python manage.py runserver 0.0.0.0:8080

# clone OpenDSA
# #############
# sudo-pw rm -rf /vagrant/OpenDSA
# sudo-pw git clone https://github.com/OpenDSA/OpenDSA.git /vagrant/OpenDSA

# # Checkout LTI branch
# cd /vagrant/OpenDSA/
# git checkout LTI
# cd /vagrant/OpenDSA/
# make pull

# # Run development server
# screen
# sudo-pw ./Webserver
# screen -d

