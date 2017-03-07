## Description
This is a LDAP integrated voting site for use in the CCoWMU officer elections. It utilizes Flask/WTForms with Bootstrap&Chart.js to allow the user to login, drag and drop the nominees into the order they desire, and vote. The app tracks what user is logged in and if they have voted on the current ballot so there can't be re-votes. After a user has voted it redirects them to the results page so they can track the election results (and so they can't vote again).

###Documentation
###Login
![login.html](/docs/images/login.png)
The login page hooks into LDAP to authenticate the user and creates a user object consisting of ID and Username to record the users vote. Note this does not record the password.
###Ballot
![ballot.html](/docs/images/ballot.png)
The ballot page uses jQuery to create a drag-and-drop reorderable list for users to vote. The votes are scored by points descending for how many users are in the list (e.g. if the votes are submitted in order personA, personB, personC, points will be assigned as personA:3, personB:2, personC:1). The list of nominees is driven by a comma delimited list that should be set in the app config. Each time the app is started it will check if the current list (alphabetically ordered) exists in the ballot database table. If the ballot does not exist in the database, the application automatically generates a new ballot entry; all new votes will be applied to the new ballot via ID. This makes it trivial to start a new vote as you only need to update the one line in the config. Votes cannot currently be recast.
###Results
![results.html](/docs/images/results.png)
The results page uses Chart.js to generate an interactive pie chart to display the results. The key is sorted in ascending order of votes and you can mouse-over any pie slice for the exact score. Clicking any of the keys will hide that slice and redraw the chart for a more granular view. The data for the results is loaded thru an AJAX call so it can be set to automatically reload at a time interval if desired.


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

Browse to `http://yoursite.tld/results` to view the current results

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
     
     cclub-voting
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
