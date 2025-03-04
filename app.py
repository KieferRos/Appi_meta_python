from flask import Flask,request,jsonify, render_template 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)

#CONFIGURACION DE LA BASE DE DATOS SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#MODELO DE LA TABLA LOG
class log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)


#CREAR UNA TABLA SINO EXISTE
with app.app_context():
    db.create_all()


#funcion para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x:x.fecha_y_hora,reverse=True)


@app.route('/')
def index():
    #obtener todos los registros de labase de datos
    registros = log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html',registros=registros_ordenados)

mensajes_log=[]

#Funcion para agregar mensajes y guardar en la base de datos
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    #Guardar el mensaje en la base de datos
    nuevo_registro = log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

#token de verificacion para la configuración
token_kiefer = "KIEFERCOD"

@app.route('/webhook',methods=['GET', 'POST'])
def webhook():
        if request.method == 'GET':
             challenge = verificar_token(request)
             return challenge
        elif request.method == 'POST':
            reponse = recibir_mensajes(request)
            return reponse

def verificar_token(req):
     token = req.args.get('hub.verify_token')
     challenge = req.args.get('hub.challenge')

     if challenge and token == token_kiefer:
          return challenge
     else:
          return jsonify({'error': 'Token Invalido'}),401
   

def recibir_mensaje(req):
     req = request.get_json()
     agregar_mensajes_log(req)
     
     return jsonify({'message':'EVENT_RECEIVED'})


if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
    
