#!/usr/bin/python3.9

import requests as rq
import logging as log

from essential import LOGIN_URL_LETOVO
from flask import Flask, request, render_template, abort, redirect, url_for
from essential import update_data

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(500)
def internal_server_error(error):
    log.error(error)
    return render_template(template_name_or_list="pageError.html",
                           error="500 Internal Server Error",
                           explain="",
                           fix=""), 500


@app.errorhandler(422)
def unprocessable_entity(error):
    log.error(error)
    return render_template(template_name_or_list="pageError.html",
                           error="422 Unprocessable Entity",
                           explain="[Possibly missing query string parameters]",
                           fix="Use the link that bot provided"), 422


@app.errorhandler(418)
def im_a_teapot(error):
    log.error(error)
    return render_template(template_name_or_list="pageError.html",
                           error="418 I'm a teapot",
                           explain="[This server is a teapot, not a coffee machine]",
                           fix=""), 418


@app.errorhandler(405)
def method_not_allowed(error):
    log.error(error)
    return render_template(template_name_or_list="pageError.html",
                           error="405 Method Not Allowed",
                           explain="",
                           fix=""), 405


@app.errorhandler(404)
def not_found(error):
    log.error(error)
    return render_template(template_name_or_list="pageError.html",
                           error="404 Not Found",
                           explain="[The page you are looking for does not exist]",
                           fix=""), 404


@app.errorhandler(403)
def forbidden(error):
    log.error(error)
    return render_template(template_name_or_list="pageError.html",
                           error="403 Forbidden",
                           explain="[You have no access to this page]",
                           fix=""), 403


@app.errorhandler(401)
def unauthorized(error):
    log.error(error)
    return render_template(template_name_or_list="pageError.html",
                           error="401 Unauthorized",
                           explain="[Possibly wrong credentials provided]",
                           fix=""), 401


@app.route("/login", methods=["GET"])
def login():
    chat_id = request.args.get("chat_id")
    if chat_id is None:
        abort(422)
    return render_template(template_name_or_list="login.html", context=chat_id)


@app.route("/api/login", methods=["POST"])
def login_api():
    try:
        analytics_login = request.form["login"]
        analytics_password = request.form["password"]
        chat_id = request.form["chat_id"]
    except KeyError:
        abort(422)
        return

    login_data = {
        "login": analytics_login,
        "password": analytics_password
    }
    try:
        if not rq.post(url=LOGIN_URL_LETOVO, data=login_data).status_code == 200:
            abort(401)
    except rq.ConnectionError:
        abort(400)  # ConnectionError
    try:
        update_data(analytics_login=analytics_login, analytics_password=analytics_password, chat_id=chat_id)
        return redirect(url_for("index")), {"message": f"Successfully logged as {analytics_login}"}
    except Exception as err:
        print(err)
        abort(400)


@app.route("/coffee", methods=["GET"])
def brew_coffee():
    abort(418)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
