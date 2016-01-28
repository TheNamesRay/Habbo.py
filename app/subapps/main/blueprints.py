from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect

from app.common import app

main = Blueprint('main', __name__, template_folder='pages')

@main.route('/')
def index():
	return render_template('index.html')


	
