from flask import Flask
from flask import render_template
from flask_restful import Resource
from flask_restful import Api
from dto.documento import DocumentoDto

class Servidor(Flask):
    root = '/'
    uri = root + 'file'
    app = Flask(__name__)

    def __new__(cls):  
        api = Api(cls.app)
        api.add_resource(DocumentoDto, cls.uri, cls.uri+'/<int:id>')
        cls.app.run(host='0.0.0.0', port=80)
    
    def __init__(self):
        pass
    
    @app.route("/", methods=['GET'])
    def view():
        return render_template('view.html')

    @app.route("/upload", methods=['GET'])
    def upload():
        return render_template('upload.html')