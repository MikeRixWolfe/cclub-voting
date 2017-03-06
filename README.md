## Description
This is a LDAP integrated voting site for use in the CCoWMU officer elections. It utilizes Flask/WTForms with JQuery&Bootstrap to allow the user to login, drag and drop the nominees into the order they desire, and vote. The app tracks what user is logged in and if they have voted on the current ballot so there can't be re-votes. After a user has voted it redirects them to the results page so they can track the election results (eventually in real time after I get it refreshing thru AJAX).

## Installation
Install python 2.7.x and then run the following

     git clone https://github.com/MikeRixWolfe/cclub-voting.git
     sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
     sudo pip2 install -r requirements.txt

## Setup
Rename app.cfg.default to app.cfg and enter desired information.

## Usage
#### Server
Run `./run` in a screen/tmux session or with nohup/wsgi/whatever.
#### Client
Browse to `http://yoursite.tld/login` to login with LDAP.

Browse to `http://yoursite.tld/results` to view the current results (this is dummy data for now until I get the graphing library working)

## Requirements
* Python 2.7.x
* libsasl2-dev python-dev libldap2-dev libssl-dev
* Flask
* Flask-Login
* Flask-SQLAlcheny
* Flask-WTF
* Python-LDAP

## License
This software is licensed under the **GPL v3** license. The terms are as follows:
     
     ccowmu-voting
     Copyright (C) 2017  Computer Club at Western Michigan University
     
     This program is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 3 of the License, or
     (at your option) any later version.
     
     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.
     
     You should have received a copy of the GNU General Public License
     along with this program.  If not, see <http://www.gnu.org/licenses/>.
