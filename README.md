# WhoYou-Server
This is a learning project. The goal was to address redundant data entry by providing an app where users an manage their own content

The live site can be viewed at [https://whoyou-client.herokuapp.com/login](https://whoyou-client.herokuapp.com/login)

The client code can be found at [https://github.com/mgjeffries/whoyou-client](https://github.com/mgjeffries/whoyou-client)

The server is hosted at: [mgjeffries.pythonanywhere.com](mgjeffries.pythonanywhere.com) until 7 April 2021.

## Running the server locally
Dependencies:
Python 3.8

1. Clone the repo: `git clone https://github.com/mgjeffries/WhoYou-Server`
1. Activate the virtual environment: `pipenv shell`
1. Install the dependencies for the virtual environment: `pipenv install`
1. Setup the database from the fixtures by running the seed file `sh seed.sh`
1. Run the server `python manage.py runserver`

## Deploying changes to the "production server" 

1. If new packages have been installed in the pipenv, run `pipenv lock -r > requirements.txt` to save these dependencies to the virtual environment
1. Push your changes to github, create a pr, and after approval, it will be the new main branch
1. Log into pythonAnywhere, open the bash script for whoYou, and `git pull origin main` to get the changes
1. If changes have been made to the dependencies, run `pip install -r requirements.txt` , note that the server uses a different virtual environment(virtualenv instead of pipenv. This should already be running.)
1. Reload the web app: In pythonanywhere, navigate to the webapp, and click the big green button that says `reload web app` 

FYI, the server has a custom wsgi config file. Here is a copy for reference: 
```
# +++++++++++ DJANGO +++++++++++
# To use your own django app use code like this:
import os
import sys

# assuming your django settings file is at '/home/mgjeffries/mysite/mysite/settings.py'
# and your manage.py is is at '/home/mgjeffries/mysite/manage.py'
path = '/home/mgjeffries/WhoYou-Server'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'whoYouServer.settings'

# then:
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```