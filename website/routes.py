import requests
from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify
from werkzeug.security import gen_salt
from werkzeug.urls import url_parse
from authlib.flask.oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from .models import db, User, OAuth2Client, OAuth2AuthorizationCode
from .oauth2 import authorization, require_oauth


bp = Blueprint(__name__, 'home')


def current_user():
  if 'id' in session:
    uid = session['id']
    return User.query.get(uid)
  return None

# endpoint to create new user
@bp.route("/create_user", methods=["GET", "POST"])
def add_user():
  if request.method == 'GET':
    return render_template('new_user.html')
  email = request.form.get('email')
  user = User.query.filter_by(email=email).first()
  if not user:
    new_user = User(**request.form.to_dict(flat=True))
    db.session.add(new_user)
    db.session.commit()
  return redirect("/users_list")

@bp.route("/users_list", methods=["GET"])
def get_user():
  all_users = User.query.all()
  return render_template('users_list.html', users=all_users)


@bp.route('/oauth/applications', methods=['GET'])
def applications():
  user = current_user()
  if user:
      clients = OAuth2Client.query.filter_by(user_id=user.id).all()
  else:
      clients = []
  return render_template('applications.html', user=user, clients=clients)

@bp.route('/')
def home():
  return render_template('home.html')

@bp.route('/login', methods=['POST'])
def login():
  print(request.form.get('email'))
  email = request.form.get('email')
  user = User.query.filter_by(email=email).first()
  print(user.__dict__)
  if not user:
    return render_template('home.html', error="Please check email and password")
  if user.check_password(user.password):
    session['id'] = user.id
    all_users = User.query.all()
    return render_template('users_list.html', users=all_users)
  return render_template('home.html', error="Invalid Password")
  

@bp.route('/logout')
def logout():
    return redirect('/')


@bp.route('/create_client', methods=('GET', 'POST'))
def create_client():
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create_client.html')
    client = OAuth2Client(**request.form.to_dict(flat=True))
    client.user_id = user.id
    client.client_id = gen_salt(24)
    if client.token_endpoint_auth_method == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)
    db.session.add(client)
    db.session.commit()
    return redirect('/')


@bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
  email = request.form.get('email')
  user = User.query.filter_by(email=email).first()
  if request.method == 'GET':
    try:
      grant = authorization.validate_consent_request(end_user=user)
    except OAuth2Error as error:
      return error.error
    return render_template('home.html', user=user, grant=grant)
  if not user:
    return render_template('home.html', error="Please check email and password")
  if user.check_password(user.password):
    grant_user = user
  else:
    grant_user = None
  return authorization.create_authorization_response(request, grant_user)

@bp.route('/callback', methods=['GET'])
def callback():
  authorization_code = request.args.get("code")
  if not authorization_code:
    return render_template("home.html", error="Invalid Authorize code")
  token_path = request.host_url + "oauth/token"
  authorization = OAuth2AuthorizationCode.query.filter_by(code=authorization_code).first()
  client = OAuth2Client.query.filter_by(client_id=authorization.client_id).first()
  post_headers = {'Content-Type': 'application/json'}
  response = requests.post(token_path,  headers=post_headers, auth=(client.client_id, client.client_secret),
    params={"grant_type": "authorization_code", "code": authorization_code, 
    "redirect_uri": client.redirect_uri})
  data = response.json()
  users_list_path = request.host_url + "users_list"
  session["access_token"] = data.get("access_token")
  return redirect("/users_list")
  



@bp.route('/oauth/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()


@bp.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')


@bp.route('/me')
@require_oauth('email')
def api_me():
  user = current_token.user
  return jsonify(id=user.id, username=user.username)
