from flask import Blueprint, render_template
from app.common import db

admin = Blueprint('admin', __name__, template_folder='pages')

@admin.route('/')
def index():
	return render_template('index.html')
	
