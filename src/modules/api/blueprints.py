from flask import Blueprint
from flask import request
from flask import session
from flask import jsonify
from flask import url_for
from flask import flash
from flask import g

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

import random
import string
import facebook

api = Blueprint('api', __name__)

import re as regex
import time


@api.route('/login/standard', methods=['POST'])
def player_login():

    if (request.form['username'].strip() == '') \
            or (request.form['password'].strip() == ''):
        return jsonify({'error': g.l['login_err_2']}), 401

    name = request.form['username']
    pw = request.form['password']

    g.cursor.execute(
        'SELECT id, password FROM users WHERE username = %s OR mail = %s', [
            name, name]
    )
    player = g.cursor.fetchone()

    if(player):
        if check_password_hash(player[1], pw) is True:
            session['player_login'] = True
            session['player_id'] = player[0]
            return jsonify({})
        else:
            return jsonify({'error': g.l['login_err_1']}), 401
    else:
        return jsonify({'error': g.l['login_err_1']}), 401


@api.route('/account/create', methods=['POST'])
def player_creation():

    name = request.form['username']
    mail = request.form['mail']
    pw = request.form['password']
    pwr = request.form['passwordr']

    errors = {}

    if name.strip() == '':
        errors['username'] = g.l['signup_error_1']
    elif len(name) > 15 or len(name) < 3:
        errors['username'] = g.l['signup_error_3']
    elif regex.match("^[a-zA-Z0-9-=?!@:_.-]+$", name) is None:
        errors['username'] = g.l['signup_error_4']
    elif name.startswith('MOD-'):
        errors['username'] = g.l['signup_error_9']
    else:
        g.cursor.execute(
            'SELECT null FROM users WHERE username = %s', [name]
        )
        check = g.cursor.fetchone()

        if check:
            errors['username'] = g.l['signup_error_5']

    if mail.strip() == '':
        errors['mail'] = g.l['signup_error_1']
    elif regex.match(
        "^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", mail
    ) is None:
        errors['mail'] = g.l['signup_error_6']
    else:
        g.cursor.execute(
            'SELECT null FROM users WHERE mail = %s', [mail]
        )
        check = g.cursor.fetchone()

        if check:
            errors['mail'] = g.l['signup_error_7']

    if pw.strip() == '':
        errors['password'] = g.l['signup_error_1']
    elif len(pw) < 6:
        errors['password'] = g.l['signup_error_8']

    if pwr.strip() == '':
        errors['passwordr'] = g.l['signup_error_1']

    if pw != pwr:
        errors['password'] = g.l['signup_error_2']
        errors['passwordr'] = g.l['signup_error_2']

    if not errors:
        sql = """
       INSERT INTO users (username, mail, password, account_created, ip_reg, ip_last)
            VALUES (%s, %s, %s, %s, %s, %s);"""

        g.cursor.execute(
            sql, [
                name, mail, generate_password_hash(pw), int(
                    time.time()), request.remote_addr, request.remote_addr
            ]
        )
        g.db.commit()
        session['player_login'] = True
        session['player_id'] = g.cursor.lastrowid
        return jsonify({})
    else:
        return jsonify(errors), 401


@api.route('/login/facebook', methods=['POST'])
def player_login_facebook():
    token = request.form['access_token']
    graph = facebook.GraphAPI(access_token=token)

    args = {'fields': 'id, name, email'}
    profile = graph.get_object('me', **args)

    mail = profile['email']
    fbid = profile['id']

    g.cursor.execute(
        'SELECT id, username FROM users WHERE mail = %s', [mail]
    )
    player = g.cursor.fetchone()

    if player:
        g.lcursor.execute('SELECT * FROM social_links WHERE mail = ?', (mail,))
        link = g.lcursor.fetchone()

        if(link):
            session['player_login'] = True
            session['player_id'] = player[0]
            return jsonify({'redirect': url_for('main.homepage')})
        else:
            return '', 401
    else:
        name, domain = mail.split('@')
        player_name = name[0:12] + str(random.randint(100, 999))
        player_pw = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(6))

        sql = """
       INSERT INTO users (username, mail, password, account_created, ip_reg, ip_last)
            VALUES (%s, %s, %s, %s, %s, %s);"""
        g.cursor.execute(
            sql, (
                player_name, mail, generate_password_hash(player_pw), int(
                    time.time()), request.remote_addr, request.remote_addr)
        )
        g.db.commit()

        g.lcursor.execute(
            'INSERT INTO social_links (mail, fb_id) VALUES (?, ?)', (mail, fbid,)
        )
        g.ldb.commit()

        session['player_login'] = True
        session['player_id'] = g.cursor.lastrowid

        flash(g.l['welcome_flash'] + player_pw)

        return jsonify({'redirect': url_for('main.welcome')})
