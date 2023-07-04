from server.app import app
from server.website import Website
from server.backend import Backend_Api
from json import load
import webbrowser
from gevent import pywsgi
import socket


if __name__ == '__main__':

    # Set up the website routes
    site = Website(app)
    for route in site.routes:
        app.add_url_rule(
            route,
            view_func=site.routes[route]['function'],
            methods=site.routes[route]['methods'],
        )

    # Set up the backend API routes
    backend_api = Backend_Api(app)
    for route in backend_api.routes:
        app.add_url_rule(
            route,
            view_func=backend_api.routes[route]['function'],
            methods=backend_api.routes[route]['methods'],
        )

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    site_config = {
        'host': '0.0.0.0',
        'port': 1338,
        'debug': False
    }

    # Run the Flask server by WSGI
    print(f"Running on http://127.0.0.1:{site_config['port']}")
    print(f"Running on http://{ip_address}:{site_config['port']}")
    webbrowser.open_new('http://127.0.0.1:1338/')

    server = pywsgi.WSGIServer(('0.0.0.0', site_config['port']), app)
    server.serve_forever()

    print(f"Closing {ip_address}:{site_config['port']}")