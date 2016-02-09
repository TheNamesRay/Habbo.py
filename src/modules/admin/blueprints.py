from flask import Blueprint
from flask import render_template
from flask import request
from flask import g
from flask import flash
from flask import url_for
from flask import redirect
from flask import session

from datetime import datetime

from src import notadmins_only
from src import admins_only

from werkzeug.security import check_password_hash

admin = Blueprint('admin', __name__, template_folder='./templates',
                  static_folder='./static', static_url_path='/public')


@admin.route('/', methods=['GET', 'POST'])
@notadmins_only
def index():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        pw = request.form['password']
        sql = """
            SELECT id, password, username
              FROM users
             WHERE username = %s
                OR mail = %s
               AND rank > 3;"""
        g.cursor.execute(sql, [username, username])
        check = g.cursor.fetchone()
        if check:
            if check_password_hash(check[1], pw) is True:
                session['player_login'] = True
                session['admin_login'] = True
                session['player_id'] = check[0]
                i = datetime.now()
                log = '[' + i.strftime('%Y/%m/%d %H:%M:%S') + \
                    '] ' + check[2] + ' logged in'
                g.lcursor.execute(
                    'INSERT INTO admin_logs (ocurrence) VALUES (?)', (log,))
                g.ldb.commit()
                return redirect(url_for('admin.dashboard'))
            else:
                error = 'You were not logged in'
        else:
            error = 'You were not logged in'

    return render_template('admin_index.html', error=error)


@admin.route('/dashboard', methods=['GET', 'POST'])
@admins_only
def dashboard():
    if request.method == 'POST':
        body = request.form['note']
        g.lcursor.execute('SELECT body FROM admin_note')
        current_note = g.lcursor.fetchone()
        if body != current_note[0]:
            g.lcursor.execute('UPDATE admin_note SET body = ?',
                              (request.form['note'],))
            g.ldb.commit()
            i = datetime.now()
            log = '[' + i.strftime('%Y/%m/%d %H:%M:%S') + '] ' + \
                g.player['username'] + ' posted a note'
            g.lcursor.execute(
                'INSERT INTO admin_logs (ocurrence) VALUES (?)', (log,))
            g.ldb.commit()

    g.lcursor.execute(
        'SELECT ocurrence FROM admin_logs ORDER BY id DESC LIMIT 8')
    logs = g.lcursor.fetchall()
    g.lcursor.execute('SELECT body FROM admin_note')
    note = g.lcursor.fetchone()
    return render_template('admin_dashboard.html', logs=logs, note=note[0])


@admin.route('/logout')
@admins_only
def logout():
    i = datetime.now()
    log = '[' + i.strftime('%Y/%m/%d %H:%M:%S') + '] ' + \
        g.player['username'] + ' logged out'
    g.lcursor.execute('INSERT INTO admin_logs (ocurrence) VALUES (?)', (log,))
    g.ldb.commit()
    del session['admin_login']
    return redirect(url_for('main.homepage'))


@admin.route('/dashboard/stats', methods=['GET'])
@admins_only
def statistics():
    return render_template('admin_statistics.html')


@admin.route('/users', defaults={'page': 0})
@admin.route('/users/page/<int:page>')
@admins_only
def users(page):
    perpage = 10
    offset = page * perpage
    g.cursor.execute('SELECT COUNT(*) FROM users;')
    quantity = g.cursor.fetchone()[0]
    sql = """
        SELECT id, username, account_created, mail, ip_last
          FROM users
      ORDER BY id
          DESC
         LIMIT %s
        OFFSET %s;"""
    g.cursor.execute(sql, [perpage, offset])
    return render_template(
        'admin_users.html', users=g.cursor.fetchall(),
        p=perpage, n=page, q=quantity
    )


@admin.route('/logs', defaults={'page': 0})
@admin.route('/logs/page/<int:page>')
@admins_only
def logs(page):
    perpage = 15
    offset = page * perpage
    g.lcursor.execute('SELECT COUNT(*) FROM admin_logs;')
    quantity = g.lcursor.fetchone()[0]
    sql = """
        SELECT ocurrence
          FROM admin_logs
      ORDER BY id
          DESC
         LIMIT ?
        OFFSET ?;"""
    g.lcursor.execute(sql, (perpage, offset))
    return render_template(
        'admin_logs.html', logs=g.lcursor.fetchall(),
        p=perpage, n=page, q=quantity
    )


@admin.route('/users/edit')
@admin.route('/users/edit/<username>')
def edit_user(username):
    return render_template('admin_edit_user.html')
