from flask import Flask, request
from flask import render_template
from flask_restful import Resource
from flask_restful import Api
from endpoint.documento import DocumentoEndPoint
from endpoint.usuario import UsuarioEndPoint
from endpoint.cuenta import CuentaEndPoint
import logging, sys, os

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')
class Servidor(Flask):
    __root = '/'
    __uri = __root + ''
    app = Flask(__name__)
    
    def __new__(cls):
        api = Api(cls.app)
        api.add_resource(DocumentoEndPoint,"/file", '/file'+'/<int:id>')
        api.add_resource(CuentaEndPoint, "/account")
        api.add_resource(UsuarioEndPoint, "/user",)
        # api.add_resource(DocumentoTipoORDateBO, cls.uri2)
        cls.app.run(host='0.0.0.0', port=8081, debug=True)
        
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

    # @app.route("/access", methods=['GET'])
    # def access():
    #     return render_template('access.html')

    # @app.route("/subscribe", methods=['GET'])
    # def subscribe():
    #     return render_template('subscribe.html')

    # @app.route("/upload", methods=['GET'])
    # def upload():
    #     return render_template('upload.html')
    
    # @app.route("/view", methods=['GET'])
    # def modal():
    #     return render_template('modal.html')