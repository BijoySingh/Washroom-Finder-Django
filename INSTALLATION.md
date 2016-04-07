# Installations

- Install required software

```lang=bash
sudo apt-get update
sudo apt-get install python3-pip python3.5-dev libpq-dev postgresql postgresql-contrib memcached \
libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev libxml2-dev libxslt1-dev libffi-dev nodejs \
nodejs-legacy npm
```

- Create a postgresql user and database. Taken from
[postgresql wiki](https://wiki.postgresql.org/wiki/First_steps).

```lang=bash
ppsql # Now you must be in postgresql command line mode

CREATE DATABASE washroom_finder;
CREATE USER washroom_finder WITH PASSWORD 'washroom_finder';
GRANT ALL PRIVILEGES ON DATABASE washroom_finder TO washroom_finder;
\q
exit
```

- Install configured lint tools
```lang=bash
sudo npm install -g csslint jsonlint jscs
```
