from flask import Flask
from flask_restful import Api
from endpoint.comprobante import ComprobanteEndPoint
import logging, sys, os
from util.config import CONFIG

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')
class ServidorWeb(Flask):
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(ComprobanteEndPoint,"/file", '/file'+'/<string:nombre>')

    def __new__(cls):
        __host = CONFIG["server.web"]["host"]
        __port = CONFIG["server.web"]["port"]
        cls.app.run(host=__host, port=__port, debug=True)
        
    def __init__(self):
        pass

    @app.route("/", methods=['GET'])
    def index():
        __basepath = os.path.join(os.getcwd(), "server", "component")
        cloud = os.path.join(__basepath,  "index.html")
        with open(cloud, "r") as f:
            binarios = f.read()
        return binarios

    @app.route("/upload", methods=['GET'])
    def upload():
        __basepath = os.path.join(os.getcwd(), "server", "component")
        cloud = os.path.join(__basepath,  "upload.html")
        with open(cloud, "r") as f:
            binarios = f.read()
        return binarios

    @app.route("/view", methods=['GET'])
    def view():
        __basepath = os.path.join(os.getcwd(), "server", "component")
        cloud = os.path.join(__basepath,  "view.html")
        with open(cloud, "r") as f:
            binarios = f.read()
        return binarios

    @app.route("/menu", methods=['GET'])
    def menu():
        __basepath = os.path.join(os.getcwd(), "server", "component")
        cloud = os.path.join(__basepath,  "menu.html")
        with open(cloud, "r") as f:
            binarios = f.read()
        return binarios

    @app.route("/modal", methods=['GET'])
    def modal():
        __basepath = os.path.join(os.getcwd(), "server", "component")
        cloud = os.path.join(__basepath,  "modal.html")
        with open(cloud, "r") as f:
            binarios = f.read()
        return binarios