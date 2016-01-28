from flask import Flask
from flask.ext.mysql import MySQL 
from app.common import load

app = Flask(__name__)
app.config.from_pyfile('app/_.cfg')

mysql = MySQL()

mysql.init_app(app)
load(app, mysql.connect().cursor())

from app.subapps.main.blueprints  import main
from app.subapps.admin.blueprints import admin
from app.subapps.api.blueprints   import api

from flask import session
from flask import request
from flask import g
from flask import redirect
from flask import render_template

from app.i18n.locale import locale

@app.route('/locale/<l>')
def change_locale(l):
	if(l in app.config['LANGUAGES']):
		session['usrlocale'] = l
	return redirect(request.referrer)

@app.before_request
def check_for_locale():
	check = session.get('usrlocale')
	usrlocale = check if check else 'es_ES'
	g.l = locale[usrlocale]
	g.ln = usrlocale

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405

app.register_blueprint(
	admin, url_prefix='/admin'
)
app.register_blueprint(
	api, url_prefix='/api/v1'
)
app.register_blueprint(main)

#if __name__ == '__main__':
#    app.run(debug=True, port=8080, threaded=True)