from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    passwd = db.Column(db.String(80))
    nome = db.Column(db.String(80))
    cognome = db.Column(db.String(80))
    classe = db.Column(db.String(2))
    notifiche=db.Column(db.Integer)
    tipo=db.Column(db.Integer) # False: non amministratore, True: amministratore

    def __init__(self, username, passwd, nome, cognome, classe, tipo):
        self.username = username # L'username equivale all'email
        self.passwd = passwd
        self.nome = nome
        self.cognome = cognome
        self.classe = classe
        self.notifiche=0
        self.tipo=tipo

    def __repr__(self):
        return "<User {}>".format(self.username, self.passwd, self.nome, self.cognome, self.classe)

class Corso(db.Model):
    cid=db.Column(db.Integer, primary_key=True, unique=True)
    nome=db.Column(db.String(80))
    materia=db.Column(db.String(80))
    luogo=db.Column(db.String(80))
    prezzo=db.Column(db.Float)
    idProprietario = db.Column(db.Integer)
    Proprietario = db.Column(db.String(80))

    def __init__(self, nome, materia, luogo, prezzo, idProprietario, Proprietario):
        self.nome=nome
        self.materia=materia
        self.luogo=luogo
        self.prezzo=prezzo
        self.idProprietario=idProprietario
        self.Proprietario=Proprietario
    def __repr__(self):
        return "<User {}>".format(self.nome, self.materia, self.luogo, self.prezzo, self.idProprietario)

class Impegno(db.Model):
    iid=db.Column(db.Integer, primary_key=True, unique=True)
    richId=db.Column(db.Integer)
    propId=db.Column(db.Integer)
    nomeRich=db.Column(db.String(80))
    nomeProp=db.Column(db.String(80))
    ora=db.Column(db.String(80))
    data=db.Column(db.String(80))
    status=db.Column(db.Integer)
    materia=db.Column(db.String(80))

    def __init__ (self, richId, propId, nomeRich, nomeProp, ora, data, materia):
        self.richId=richId
        self.propId=propId
        self.nomeRich=nomeRich
        self.nomeProp=nomeProp
        self.ora=ora
        self.data=data
        self.status=0
        self.materia=materia

db.create_all()

nuovouser = User('admin', 'admin', 'dio', 'brando', '5f', 1)
db.session.add(nuovouser)
db.session.commit()
