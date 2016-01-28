from flask import Blueprint
from app.common import db

api = Blueprint('api', __name__)

@api.route('/login/email', methods=['POST'])
def index():
	print('hey niggers')
	return 'hey niggers'

	
