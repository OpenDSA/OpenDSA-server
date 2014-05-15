# OpenDSA-server

The OpenDSA project's server-side support to collect and manage data on student performance on web-based exercises.

## Installation and Setup

### Windows
- Install Python
- Download [get-pip.py](https://raw.github.com/pypa/pip/master/contrib/get-pip.py) and run:

```
python get-pip.py
pip install Django
```

- Install MySQL Server
- Start a MySQL command prompt

```
CREATE DATABASE <database_name>;
GRANT ALL ON <database_name>.* TO '<database_user>'@'localhost' IDENTIFIED BY '<database_user_password>';
exit
```

- See "Both" section for remaining instructions


### Linux
```
sudo apt-get install python
curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py
sudo python get-pip.py
sudo pip install Django

// Install and setup mysql
sudo apt-get install mysql-server
mysql -u root -p [ENTER]
```

Enter your password when prompted, then from the mysql pseudo-shell, run:

```
CREATE DATABASE <database_name>;
GRANT ALL ON <database_name>.* TO '<database_user>'@'localhost' IDENTIFIED BY '<database_user_password>';
exit
```

- See "Both" section for remaining instructions

### Both
- pip install MySQL-python
  - If this doesn't work in Windows, you can install from an [EXE](https://code.google.com/p/soemin/downloads/detail?name=MySQL-python-1.2.3.win32-py2.7.exe)

- See requirements.txt in ODSA-django directory (listed below for convenience), remove sudo for Windows

```
sudo pip install oauth2
sudo pip install simplejson
sudo pip install feedparser
sudo pip install icalendar
sudo pip install mimeparse
sudo pip install python-dateutil
sudo pip install django-tastypie

// Install memcache
sudo pip install python-memcached

// Install user agent (http://pypi.python.org/pypi/django-user_agents)
sudo pip install pyyaml ua-parser user-agents
sudo pip install django-user-agents

git clone https://YOURGITHUBID@github.com/OpenDSA/OpenDSA-server.git ODSAserver
cd ODSAserver/ODSA-django
```

- Edit settings.py
  - Update 'BASE_URL' to have the IP and port of the Django server (optional?)

    Ex: BASE_URL = "127.0.0.1:8000"
    
  - Edit 'TEMPLATE_LOADERS', if necessary

  - Update 'DATABASES'
```
'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
'NAME': '<database_name>',         #g3et_path('test.db'),            # Or path to database file if using sqlite3.
'USER': '<database_user>',                  # Not used with sqlite3.
'PASSWORD': '<database_user_password>',                  # Not used with sqlite3.
'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
```

- python manage.py syncdb
  - Create an administrator (superuser) account when prompted

- python manage.py runserver 0.0.0.0:8000
- In your web browser, go to: http://127.0.0.1:8000/admin/

### Note
  - Due to cross-domain communication issues, the files communicating with the Django server must be hosted by a webserver and that server must be listed in the 'XS_SHARING_ALLOWED_ORIGINS' variable in settings.py.  For OpenDSA development, we are hosting our files on 'http://algoviz-beta.cc.vt.edu'
  - To enable OpenDSA to communicate with the Django server, you must set the "backend_address" field in your book's config file to the base URL of your server
