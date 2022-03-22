from flask import Flask, request
from flask import render_template
from flask_restful import Resource
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from bo.documento import DocumentoBO, DocumentoTipoORDateBO
import logging, sys
import requests

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')

class Servidor(Flask):
    root = '/'
    uri = root + 'file'
    uri2 = root + 'files'
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = ""

    def __new__(cls):  
        api = Api(cls.app)
        api.add_resource(DocumentoBO, cls.uri, cls.uri+'/<int:id>')
        api.add_resource(DocumentoTipoORDateBO, cls.uri2)
        cls.app.run(host='0.0.0.0', port=8080, debug=True)
    
    def __init__(self):
        pass

    @staticmethod
    def getFormats():
        formats = [
            {'tipo': 1, 'nombre': 'jpeg' },
            {'tipo': 2, 'nombre': 'png' },
            {'tipo': 3, 'nombre': 'mp4' }]
        return formats

    @staticmethod
    def getFiles():
        files = DocumentoBO.getdocumentos()
        return files

    @staticmethod
    def getFile(id):
        file = DocumentoBO.getdocumento(id)
        return file

    @app.route("/", methods=['GET'])
    def view():
        header = {
            'Content-Type': 'application/json',
        }
        url = "http://127.0.0.1:8080/file"
        w = requests.get(url, headers=header)
        log.info(w.text)
        return render_template('view.html', formatos=Servidor.getFormats(), documentos=Servidor.getFiles())

    @app.route("/upload", methods=['GET'])
    def upload():
        return render_template('upload.html')
    
    @app.route("/view", methods=['GET'])
    def modal():
        id = request.args.get('id')
        documento=Servidor.getFile(id)
        log.warn(documento)
        return render_template('modal.html', documento=documento)