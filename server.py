from flask import Flask, session, url_for, redirect, request, render_template, abort
from flask_sqlalchemy import SQLAlchemy
import smtplib
import bcrypt
from datetime import datetime, date, time
app = Flask(__name__)
app.secret_key = "condivisione"

# SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    passwd = db.Column(db.LargeBinary)
    nome = db.Column(db.String(80))
    cognome = db.Column(db.String(80))
    classe = db.Column(db.String(2))
    notifiche=db.Column(db.Integer)
    tipo=db.Column(db.Integer)

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
    professore = db.Column(db.String(80))

    def __init__(self, nome, materia, luogo, prezzo, idProprietario, Proprietario, professore):
        self.nome=nome
        self.materia=materia
        self.luogo=luogo
        self.prezzo=prezzo
        self.idProprietario=idProprietario
        self.Proprietario=Proprietario
        self.professore=professore
    def __repr__(self):
        return "<User {}>".format(self.nome, self.materia, self.luogo, self.prezzo, self.idProprietario)

class Impegno(db.Model):
    iid=db.Column(db.Integer, primary_key=True, unique=True)
    richId=db.Column(db.Integer)
    propId=db.Column(db.Integer)
    nomeRich=db.Column(db.String(80))
    nomeProp=db.Column(db.String(80))
    data=db.Column(db.DateTime)
    status=db.Column(db.Integer)
    materia=db.Column(db.String(80))

    def __init__ (self, richId, propId, nomeRich, nomeProp, data, materia):
        self.richId=richId
        self.propId=propId
        self.nomeRich=nomeRich
        self.nomeProp=nomeProp
        self.data=data
        self.status=0
        self.materia=materia

db.create_all()


# Funzioni del sito
def login(username, password):
    user = User.query.filter_by(username=username).first()
    try:
        return bcrypt.checkpw(bytes(password, encoding="utf-8"), user.passwd)
    except AttributeError:
        # Se non esiste l'Utente
        return False
def establishNotifications(username): #funzione per permessi amministrativi
    user = User.query.all()
    for utenze in user:
        if username == utenze.username:
            return utenze.notifiche
def establishuid(username):
    user = User.query.all()
    for utenze in user:
        if username == utenze.username:
            return utenze.uid

def establishAuth(username):
    user=User.query.all()
    for utenze in user:
        if username == utenze.username:
            return utenze.tipo

def sendemail(emailUtente, kind, ora, data, nome, materia):
    username=""
    password=""
    sender=""
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(username, password)
    if str(kind) == "1": #Hai una nuova richiesta sul sito
        msg = "L\'utente "+ nome + " ha chiesto un appuntamento il "+ data +" alle ore "+ ora +" per "+ materia + ". Per accettare o declinare, accedi al sito Condivisione."
    elif str(kind) == "2":
        msg = "La tua richiesta di ripetizione fatta allo studente "+ nome + " non e\' stata accettata."
    elif str(kind) == "3":
        msg = "La tua richiesta di ripetizione fatta allo studente "+ nome + " e\' stata accettata."
    else:
        msg = "Qualcosa non ha funzionato. Collegati al sito per vedere cosa c\'e\' di nuovo"
    server.sendmail(sender, emailUtente, msg)

# Sito
@app.route('/')
def page_home():
    if 'username' not in session:
        return redirect(url_for('page_login'))
    else:
        session.pop('username')
        return redirect(url_for('page_login'))

@app.route('/login', methods=['GET', 'POST'])
def page_login():
    if request.method == 'GET':
        css = url_for("static", filename="style.css")
        return render_template("login.html.j2", css=css)
    else:
        if login(request.form['username'], request.form['password']):
            session['username'] = request.form['username']
            if establishAuth(session['username']) == 1:
                return redirect(url_for('page_amministrazione', user=session['username']))
            else:
                return redirect(url_for('page_dashboard', user=session['username']))
        else:
            abort(403)
@app.route('/register', methods=['GET', 'POST'])
def page_register():
    if request.method == 'GET':
        css = url_for("static", filename="style.css")
        return render_template("User/add.html.j2", css=css)
    else:
        p = bytes(request.form["passwd"], encoding="utf-8")
        cenere=bcrypt.hashpw(p, bcrypt.gensalt())
        nuovouser = User(request.form['username'], cenere, request.form['nome'], request.form['cognome'], request.form['classe'], 0)
        db.session.add(nuovouser)
        db.session.commit()
        return redirect(url_for('page_login'))

@app.route('/user_del/<int:uid>')
def page_user_del(uid):
    if 'username' not in session or establishAuth(session['username']) != 1:
        abort(403)
    if uid == 1:
        abort(403)
    user = User.query.get(uid)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('page_amministrazione'))

@app.route('/user_inspect/<int:uid>')
def page_user_inspect(uid):
    if 'username' not in session:
        abort(403)
    user = User.query.get(uid)
    css = url_for("static", filename="style.css")
    return render_template("User/inspect.html.j2", css=css, user=user)

@app.route('/dashboard', methods=['GET', 'POST'])
def page_dashboard():
    if 'username' not in session:
        return redirect(url_for('page_home'))
    elif request.method == 'GET':
        banner = url_for("static", filename="banner.png")
        css = url_for("static", filename="style.css")
        imp=Impegno.query.all()
        selezionati=[]
        for impegno in imp:
            if impegno.richId == establishuid(session['username']) or impegno.propId == establishuid(session['username']):
                selezionati.append(impegno)
        return render_template("dashboard.html.j2", css=css, user=session['username'], banner=banner, notifiche=establishNotifications(session['username']), id=establishuid(session['username']), impegni=selezionati)
    else:
        abort(400)

@app.route('/changepw/<int:uid>', methods=['GET', 'POST'])
def page_user_show(uid):
    if 'username' not in session or uid != establishuid(session['username']):
        abort(403)
    if request.method == "GET":
        users = User.query.get(uid)
        css = url_for("static", filename="style.css")
        return render_template("User/show.html.j2", css=css, users=users, user=session["username"])
    else:
        if 'username' not in session:
            abort(403)
        else:
            users = User.query.get(uid)
            p = bytes(request.form["passwd"], encoding="utf-8")
            cenere=bcrypt.hashpw(p, bcrypt.gensalt())
            users.passwd=cenere
            users.classe = request.form["classe"]
            db.session.commit()
            return redirect(url_for('page_dashboard'))

@app.route('/informazioni', methods=['GET', 'POST'])
def page_informazioni():
    banner = url_for("static", filename="banner.png")
    css = url_for("static", filename="style.css")
    return render_template("informazioni.html.j2", css=css, banner=banner)

@app.route('/nuovocorso', methods=['GET', 'POST'])
def page_corso_new():
    if 'username' not in session:
        abort(403)
    if request.method == "GET":
        css = url_for("static", filename="style.css")
        return render_template("Corsi/add.html.j2", css=css, user=session["username"])
    else:
        if 'username' not in session:
            abort(403)
        else:
            creatore=User.query.get(establishuid(session['username']))
            proprietario=creatore.nome+" "+creatore.cognome
            nuovocorso = Corso(request.form['nome'], request.form['materia'], request.form['luogo'], float(request.form['prezzo']), establishuid(session['username']), proprietario, request.form['professore'])
            db.session.add(nuovocorso)
            db.session.commit()
            return redirect(url_for('page_dashboard'))

@app.route('/searchlesson', methods=['GET', 'POST'])
def page_corso_list():
    if 'username' not in session:
        abort(403)
    if request.method == "GET":
        corsi = Corso.query.all()
        css = url_for("static", filename="style.css")
        return render_template("Corsi/list.html.j2", css=css, user=session["username"], corsi=corsi, uid=establishuid(session['username']))
    else:
        ricerca=request.form['ricerca']
        corsi = Corso.query.all()
        risultati=[]
        for corso in corsi:
            if corso.luogo == ricerca or corso.materia == ricerca or corso.professore == ricerca:
                risultati.append(corso)
        css = url_for("static", filename="style.css")
        return render_template("Corsi/list.html.j2", css=css, user=session["username"], corsi=risultati, uid=establishuid(session['username']))

@app.route('/corso_del/<int:cid>', methods=['GET', 'POST'])
def page_corso_del(cid):
    if 'username' not in session:
        abort(403)
    corso = Corso.query.get(cid)
    if corso.idProprietario != establishuid(session['username']) and establishAuth(session['username']) != 1:
        abort(403)
    db.session.delete(corso)
    db.session.commit()
    if establishAuth(session['username']) != 1:
        return redirect(url_for('page_corso_list'))
    else:
        return redirect(url_for('page_amministrazione'))

@app.route('/corso_iscrizione/<int:cid>', methods=['GET', 'POST'])
def page_corso_isc(cid):
    if 'username' not in session:
        abort(403)
    if request.method == "GET":
        corsi = Corso.query.all()
        css = url_for("static", filename="style.css")
        return render_template("Corsi/prenota.html.j2", css=css, user=session["username"], corsi=corsi, uid=establishuid(session['username']), cid=cid)
    else:
        corso = Corso.query.get(cid)
        richiedente = User.query.get(establishuid(session['username']))
        nomeRichiedente=richiedente.nome+" "+richiedente.cognome
        proprietario=User.query.get(corso.idProprietario)
        nomeProprietario=proprietario.nome+" "+proprietario.cognome
        data=request.form['data']
        dsep=data.split("/")
        d=date(int(dsep[2]), int(dsep[1]), int(dsep[0]))
        ora=request.form['ora']
        osep=ora.split(":")
        o=time(int(osep[0]), int(osep[1]))
        nuovoImpegno=Impegno(richiedente.uid, corso.idProprietario, nomeRichiedente, nomeProprietario, datetime.combine(d, o), corso.materia)
        proprietario.notifiche+=1
        sendemail(proprietario.username, "1", ora, data, nomeRichiedente, corso.materia)
        db.session.add(nuovoImpegno)
        db.session.commit()
        return redirect(url_for('page_corso_list'))

@app.route('/richieste')
def page_richieste():
    if 'username' not in session:
        abort(403)
    if request.method == "GET":
        banner = url_for("static", filename="banner.png")
        css = url_for("static", filename="style.css")
        imp=Impegno.query.all()
        selezionati=[]
        for impegno in imp:
            if impegno.propId == establishuid(session['username']):
                selezionati.append(impegno)
        proprietario=User.query.get(establishuid(session['username']))
        proprietario.notifiche=0
        db.session.commit()
        return render_template("richieste.html.j2", css=css, user=session['username'], banner=banner, notifiche=establishNotifications(session['username']), id=establishuid(session['username']), impegni=selezionati)

@app.route('/impegno_deny/<int:iid>')
def page_impegno_deny(iid):
    if 'username' not in session:
        abort(403)
    impegno = Impegno.query.get(iid)
    tizio=User.query.get(impegno.richId)
    sendemail(tizio.username, "2", impegno.data.time, impegno.data.date, impegno.nomeProp, " ")
    db.session.delete(impegno)
    db.session.commit()
    return redirect(url_for('page_richieste'))

@app.route('/impegno_accept/<int:iid>')
def page_impegno_accept(iid):
    if 'username' not in session:
        abort(403)
    impegno = Impegno.query.get(iid)
    tizio=User.query.get(impegno.richId)
    sendemail(tizio.username, "3", impegno.data.time, impegno.data.date, impegno.nomeProp, " ")
    impegno.status=1
    db.session.commit()
    return redirect(url_for('page_richieste'))

@app.route('/impegno_del/<int:iid>')
def page_impegno_del(iid):
    if 'username' not in session:
        abort(403)
    impegno = Impegno.query.get(iid)
    if impegno.propId != establishuid(session['username']) and impegno.richId != establishuid(session['username']):
        abort(403)
    db.session.delete(impegno)
    db.session.commit()
    return redirect(url_for('page_dashboard'))

@app.route('/amministrazione', methods=['GET'])
def page_amministrazione():
    if 'username' not in session or establishAuth(session['username']) != 1:
        abort(403)
    else:
        if request.method == "GET":
            banner = url_for("static", filename="banner.png")
            css = url_for("static", filename="style.css")
            users=User.query.all()
            corsi=Corso.query.all()
            return render_template("Amministrazione/administrative_dashboard.html.j2", css=css, user=session['username'], banner=banner, users=users, corsi=corsi)
