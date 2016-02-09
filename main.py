"""Initialize everything all in one place.

Attributes
----------
app : Flask application
    The default Flask application.
mysql : MySQL connection
    The default MySQL connection.
"""
from flask import Flask
from flask.ext.mysql import MySQL
from flask.ext.compress import Compress
import sqlite3

#! Flask application initialization
app = Flask(__name__)

#! Load configuration from _.cfg
app.config.from_pyfile('_.cfg')

#! Compress responses with gzip
Compress(app)

#! Open database connection
mysql = MySQL(app)

from flask import session
from flask import request
from flask import g
from flask import url_for
from flask import redirect
from flask import render_template

from src.i18n.locale import locale
from datetime import datetime


@app.template_filter('strftime')
def _jinja2_filter_datetime(timestamp):
    """Datetime filter for Jinja2

    Parameters
    ----------
    timestamp : int
        The UNIX timestamp to transform into date.

    Returns
    -------
    date : str
        The formatted date.
    """
    return datetime.fromtimestamp(int(timestamp))


@app.route('/locale/<l>')
def change_locale(l):
    """Allow the user to change the language.

    Parameters
    ----------
    l : str
        Locale string (es_ES, en_US)

    Returns
    -------
    redirect : redirect
        Refresh the page.
    """
    if l in locale:
        session['usrlocale'] = l
    return redirect(request.referrer)


@app.before_request
def check_for_locale():
    """Set the locale vars globally.

    Returns
    -------
        None
    """
    check = session.get('usrlocale')
    usrlocale = check if check else 'es_ES'
    g.l = locale[usrlocale]
    g.ln = usrlocale


@app.before_request
def set_db():
    """Generate a cursor for the MySQL and SQLite3 database.

    Returns
    -------
        None
    """
    g.db = mysql.get_db()
    g.cursor = g.db.cursor()
    g.ldb = sqlite3.connect('src/db.sqlite')
    g.lcursor = g.ldb.cursor()


@app.before_request
def set_player_params():
    """Set the player's parameters globally (if logged in).

    Returns
    -------
        None
    """
    if 'player_login' in session:
        sql = """
            SELECT username, mail, auth_ticket, rank, look, motto
              FROM users
             WHERE id = %s; """

        g.cursor.execute(sql, [session['player_id']])
        result = g.cursor.fetchone()
        if result:
            g.player = {}
            g.player['username'] = result[0]
            g.player['mail'] = result[1]
            g.player['auth_ticket'] = result[2]
            g.player['rank'] = result[3]
            g.player['look'] = result[4]
            g.player['motto'] = result[5]
        else:
            if 'admin_login' in session:
                del session['admin_login']
            del session['player_login']
            del session['player_id']


@app.before_request
def check_maintenance():
    """Check if the website is under maintenance.

    Returns
    -------
    redirect : redirect
        Take user to the maintenance page.
    """
    g.lcursor.execute(
        "SELECT value FROM settings WHERE variable = 'maintenance'")

    result = g.lcursor.fetchone()

    if result[0] is '1' and \
                    request.path != url_for('main.maintenance') and \
                    'public' not in request.path and \
                    'admin_login' not in session and \
                    'admin' not in request.path:
        return redirect(url_for('main.maintenance'))


@app.errorhandler(404)
def page_not_found():
    """Set a custom 404 page.

    Parameters
    ----------
        None

    Returns
    -------
    render_template : str
        The 404 template.

    response_code : int
        The 404 response code.
    """
    return render_template('404.html'), 404


@app.errorhandler(405)
def method_not_allowed():
    """Set a custom 405 page.

    Parameters
    ----------
        None

    Returns
    -------
    render_template : str
        The 405 template.

    response_code : int
        The 405 response code.
    """
    return render_template('405.html'), 405


@app.teardown_request
def close_sqlite3():
    """Close SQLite3

    Parameters
    ----------
        None

    Returns
    -------
        None
    """
    g.ldb.close()

from src.modules.main.blueprints import main
from src.modules.admin.blueprints import admin
from src.modules.api.blueprints import api

#! Register main blueprint
app.register_blueprint(main)

#! Register admin blueprint
app.register_blueprint(admin, url_prefix='/admin')

#! Register api blueprint
app.register_blueprint(api, url_prefix='/api/v1')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080, threaded=True)
