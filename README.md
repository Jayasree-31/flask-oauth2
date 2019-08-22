To run the application, we need to install all the dependencies:
  $ pip install -r requirements.txt
  Create a virtualenv and install all the requirements.

# disable check https for development(DO NOT SET THIS IN PRODUCTION)
  $ export AUTHLIB_INSECURE_TRANSPORT=1

Create Database and run the development server:

  $ flask initdb
  $ flask run

To connect Database in shell:
  from app import create_app
  app = create_app()
  app.app_context().push()
  from website.models import db
  from website.models import User
