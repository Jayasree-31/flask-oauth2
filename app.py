import os
from website.app import create_app
from website.models import db


basedir = os.path.abspath(os.path.dirname(__file__))
app = create_app({
    'SECRET_KEY': 'secret',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + os.path.join(basedir, 'flask_oauth2.sqlite')
})


@app.cli.command()
def initdb():
  db.create_all()

def create_app():
  db.init_app(app)
  return app
