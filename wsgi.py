from gevent.wsgi import WSGIServer
from main import app

if __name__ == '__main__':
	http_server = WSGIServer(('', 80), app)
	http_server.serve_forever()