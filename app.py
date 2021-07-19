import firebase_admin
import json
# from functools import wraps

from firebase_admin import credentials, db
from flask import Flask, request, render_template, abort, redirect, url_for

app = Flask(__name__)

cred_obj = credentials.Certificate("fbAdminConfig.json")
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': "https://authtest-3fcb2-default-rtdb.europe-west1.firebasedatabase.app/"
})


def init_user(chat_id,
              student_id=None,
              mail_address=None,
              mail_password=None,
              analytics_login=None,
              analytics_password=None,
              token=None):
    pas = '"tmp": ""'
    st = f'"student_id": {student_id}'
    ma = f'"mail_address": "{mail_address}"'
    mp = f'"mail_password": "{mail_password}"'
    al = f'"analytics_login": "{analytics_login}"'
    ap = f'"analytics_password": "{analytics_password}"'
    t = f'"token": "{token}"'
    request_payload = '''
    {
        "data": {''' + \
              f'{st if student_id else pas},' + \
              f'{ma if mail_address else pas},' + \
              f'{mp if mail_password else pas},' + \
              f'{al if analytics_login else pas},' + \
              f'{ap if analytics_password else pas},' + \
              f'{t if token else pas}' + \
              '''},
              "preferences": {
                  "lang": "en"
              }
          }
          '''
    ref = db.reference(f"/users/{chat_id}")
    ref.update(json.loads(request_payload))


def update_data(chat_id,
                student_id=None,
                mail_address=None,
                mail_password=None,
                analytics_login=None,
                analytics_password=None,
                token=None):
    pas = '"tmp": ""'
    si = f'"student_id": {student_id}'
    ma = f'"mail_address": "{mail_address}"'
    mp = f'"mail_password": "{mail_password}"'
    al = f'"analytics_login": "{analytics_login}"'
    ap = f'"analytics_password": "{analytics_password}"'
    t = f'"token": "{token}"'
    request_payload = '''
        {''' + \
              f'{si if student_id else pas},' + \
              f'{ma if mail_address else pas},' + \
              f'{mp if mail_password else pas},' + \
              f'{al if analytics_login else pas},' + \
              f'{ap if analytics_password else pas},' + \
              f'{t if token else pas}' + \
              '''}
          '''
    ref = db.reference(f"/users/{chat_id}")
    ref.child("data").update(json.loads(request_payload))


@app.route('/')
def index():
    return render_template("index.html")


@app.errorhandler(405)
def not_allowed(error):
    return render_template("page405.html"), 405


@app.errorhandler(404)
def not_found(error):
    return render_template("page404.html"), 404


@app.errorhandler(403)
def forbidden(error):
    return render_template("page403.html"), 403


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/api/signup', methods=["POST"])
def signup_api():
    try:
        username = request.form['username']
        password = request.form['password']
        chat_id = request.form['chat_id']
    except NameError as err:
        return {"Error": "Invalid data"}, 403

    if username is None or password is None or chat_id is None:
        return {'message': 'Error missing email or password or chat ID'}, 400
    try:
        redir = redirect(url_for("index"))
        return redir, {'message': f'Successfully inited user {chat_id}'}

        # init_user(1100101, , mail_password=password)
    except Exception as err:
        print(err)
        return {'message': 'Error initing user'}, 400


@app.route('/api/login', methods=["POST"])
def login_api():
    try:
        username = request.form['username']
        password = request.form['password']
        chat_id = request.form['chat_id']
    except NameError as err:
        return {"Error": "Invalid data"}, 403

    if username is None or password is None or chat_id is None:
        return {'message': 'Error missing email or password or chat ID'}, 400
    try:
        redir = redirect(url_for("index"))
        return redir, {'message': f'Successfully logged as {chat_id}'}

        # init_user(1100101, mail_address=email, mail_password=password)
    except Exception as err:
        print(err)
        return {'message': 'Error logging user'}, 400


if __name__ == '__main__':
    app.run(debug=True, host="10.10.10.80", port=8080)
