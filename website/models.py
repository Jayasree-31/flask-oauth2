import time
from flask_sqlalchemy import SQLAlchemy
from authlib.flask.oauth2.sqla import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)

db = SQLAlchemy()


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(40))
  password = db.Column(db.String(40))
  email = db.Column(db.String(40), unique=True)

  def __str__(self):
    return self.username
  def __init__(self, username, email, password):
    self.username = username
    self.email = email
    self.password = password

  def as_dict(self):
    return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

  def get_user_id(self):
    return self.id

  def check_password(self, password):
    return password == self.password


class OAuth2Client(db.Model, OAuth2ClientMixin):
  __tablename__ = 'oauth2_client'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(
      db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
  user = db.relationship('User')

  def as_dict(self):
    return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')

    def is_refresh_token_expired(self):
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at < time.time()
