import os
from flask import Flask, redirect, request, render_template, make_response, g, url_for,session
from flask_mail import Mail, Message
from datetime import datetime
import sqlite3

DATABASE = 'Exec.db'

app = Flask(__name__)

app.config.update( #MAIL SETTINGS
	DEBUG=True,
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = '',
	MAIL_PASSWORD = ''
	)

mail = Mail(app)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

#--------------------------------Rendering--------------------------------------

@app.route("/")
def home():
   return render_template('index.html', msg = '')

@app.route("/ThankYou", methods = ['POST'])
def SendMail():
    if request.method=='POST':
        name = request.form.get('name', default="Error")
        email = request.form.get('email', default="Error")
        mobile = request.form.get('mobile', default="Error")
        subject = request.form.get('subject', default="Error")
        message = request.form.get('message', default="Error")
        now = datetime.now()
        print(name)
        print(email)
        print(mobile)
        print(subject)
        print(message)

        subjectmsg = name + " - " + subject

        bodymsg = "Name: " + name + "\n\n" "Email: " + email + "\n\n" + "Mobile: " + mobile + "\n\n" + "Message: "+ message

        try:
            msg = Message(subjectmsg,
                sender="elliott.davies10@gmail.com",
                recipients=["elliott_davies@live.co.uk", "DaviesE70@Cardiff.ac.uk"])
            msg.body = bodymsg
            mail.send(msg)
            resp = make_response(render_template('index.html', msg='Thank you for getting in touch!'))

            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO CustomerQueries ('Name', 'Email', 'mobile', 'Subject', 'Message', 'QueryDate')\
                     VALUES (?,?,?,?,?,?)",(name, email, mobile, subject, message, now) )
            conn.commit()
            msg = "Record successfully added"
            conn.close()


            return resp
        except Exception as e:
            return(str(e))


#--------------------------------Adviser Sessions---------------------------------------

app.secret_key = os.urandom(24)

@app.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('adviser', None)
        email = request.form.get('email', default="Error")
        password = request.form.get('password', default="Error")
        resp = ""
        if VerifyAdviserEmail(email):
            if VerifyAdviserPassword(email, password):
				session['adviser'] = request.form['email'] #rename user in session[] to whatever you want to make a new
				resp = redirect(url_for('protected'))
            else:
                resp = make_response(render_template('login.html', msg='Incorrect  password'))
        else:
            resp = make_response(render_template('login.html', msg='Incorrect  email'))

        return resp
    return render_template('login.html')

@app.route('/protected')
def protected():
    if g.adviser:
        data = AllQueries()
        return render_template('protected.html', data = data)

    return redirect(url_for('login'))

@app.route('/DeleteQuery', methods = ['POST'])
def DeleteQueryRoute():
    if request.method=='POST':
        email = request.form.get('email', default="Error")
        print("EMAIL: " +email)
        DeleteQuery(email)
        data = AllQueries()
        return redirect(url_for('protected'))

@app.before_request
def before_request():
    g.adviser = None
    if 'adviser' in session:
        g.adviser = session['adviser']

@app.route('/getsession')
def getsession():
    if 'adviser' in session:
        return session['adviser']

    return 'Not logged in!'

@app.route('/dropsession')
def dropsession():
    session.pop('adviser', None)
    return redirect(url_for('login'))


def VerifyAdviserEmail(email):
  conn = sqlite3.connect(DATABASE)
  cur = conn.cursor()
  cur.execute("SELECT email FROM AdviserDetails WHERE email=?;", [email])
  data = cur.fetchall()
  conn.close()
  if email in str(data):
      return email

def VerifyAdviserPassword(email, password):
  conn = sqlite3.connect(DATABASE)
  cur = conn.cursor()
  cur.execute("SELECT password FROM AdviserDetails WHERE email=?;", [email])
  data = cur.fetchall()
  conn.close()
  if password in str(data):
	  print("Password: "+password)
	  print("Str(Data): "+str(data))
	  return password

def AllQueries():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM CustomerQueries;")
    data = cur.fetchall()
    conn.close()
    return data

def DeleteQuery(email):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
	#test = "DELETE FROM CustomerQueries WHERE Email=" + email ";"
    cur.execute("DELETE FROM CustomerQueries WHERE Email=?;", [email]) #;PRBABLY NOT MEANT TO BE CURSOR.
    conn.close()
    print("DELETED: " +email)





#--------------------------------Admin Sessions---------------------------------------



@app.route('/AdminLogin', methods=['GET', 'POST'])
def AdminLogin():
    if request.method == 'POST':
        session.pop('admin', None)
        AdminEmail = request.form.get('AdminEmail', default="Error")
        AdminPassword = request.form.get('AdminPassword', default="Error")
        resp = ""
        if VerifyAdminEmail(AdminEmail):
            if VerifyAdminPassword(AdminEmail, AdminPassword):
				session['admin'] = request.form['AdminEmail'] #rename user in session[] to whatever you want to make a new
				resp = redirect(url_for('AdminProtected'))
				#resp = make_response(render_template('protected.html', msg=''))
            else:
                resp = make_response(render_template('AdminLogin.html', msg='Incorrect password'))
        else:
            resp = make_response(render_template('AdminLogin.html', msg='Incorrect  email'))

        return resp
    return render_template('AdminLogin.html')



@app.route('/AdminProtected', methods=['GET', 'POST'])
def AdminProtected():
    if g.admin:
        if request.method=='POST':
            FirstName = request.form.get('FirstName', default="Error")
            SecondName = request.form.get('SecondName', default="Error")
            Email = request.form.get('Email', default="Error")
            Password = request.form.get('Password', default="Error")
            now = datetime.now()
            print(FirstName)
            print(SecondName)
            print(Email)
            print(Password)

            try:
                conn = sqlite3.connect(DATABASE)
                cur = conn.cursor()
                cur.execute("INSERT INTO AdviserDetails ('FirstName', 'SecondName', 'Email', 'Password','DateAdded')\
				         VALUES (?,?,?,?,?)",(FirstName, SecondName, Email, Password, now ) )
                conn.commit()
                msg = "Record successfully added"

                cur.execute("SELECT * FROM AdviserDetails;")
                data = cur.fetchall()
                conn.close()
                return redirect(url_for('AdminProtected', data = data))
                # return render_template('AdminProtected.html', data = data)
            except Exception as e:
                return(str(e))
        if request.method=='GET':
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("SELECT * FROM AdviserDetails;")
            data = cur.fetchall()
            conn.close()
            return render_template('AdminProtected.html', data = data)
    return redirect(url_for('AdminLogin'))




@app.before_request
def Admin_before_request():
    g.admin = None
    if 'admin' in session:
        g.admin = session['admin']

@app.route('/AdminGetSession')
def AdminGetSession():
    if 'admin' in session:
        return session['admin']

    return 'Not logged in!'

@app.route('/AdminDropSession')
def AdminDropSession():
    session.pop('admin', None)
    return redirect(url_for('AdminLogin'))


def VerifyAdminEmail(AdminEmail):
  conn = sqlite3.connect(DATABASE)
  cur = conn.cursor()
  cur.execute("SELECT email FROM AdminDetails WHERE email=?;", [AdminEmail])
  data = cur.fetchall()
  conn.close()
  if AdminEmail in str(data):
      return AdminEmail

def VerifyAdminPassword(AdminEmail, AdminPassword):
  conn = sqlite3.connect(DATABASE)
  cur = conn.cursor()
  cur.execute("SELECT password FROM AdminDetails WHERE email=?;", [AdminEmail])
  data = cur.fetchall()
  conn.close()
  if AdminPassword in str(data):
      return AdminPassword





#--------------------------------Database---------------------------------------

def createAdminTable():
	conn = sqlite3.connect(DATABASE)
	conn.execute('CREATE TABLE IF NOT EXISTS `AdminDetails` (\
					`ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,\
					`FirstName`	TEXT NOT NULL,\
					`SecondName`	TEXT NOT NULL,\
					`Email`	TEXT NOT NULL,\
					`Password`	TEXT NOT NULL);')

	conn.close()

def createAdviserTable():
	conn = sqlite3.connect(DATABASE)
	conn.execute('CREATE TABLE IF NOT EXISTS `AdviserDetails` (\
					`ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,\
					`FirstName`	TEXT NOT NULL,\
					`SecondName`	TEXT NOT NULL,\
					`Email`	TEXT NOT NULL,\
					`Password`	TEXT NOT NULL,\
					`DateAdded`	TEXT NOT NULL);')

	conn.close()

def createCustomerTable():
	conn = sqlite3.connect(DATABASE)
	conn.execute('CREATE TABLE IF NOT EXISTS `CustomerQueries` (\
					`ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,\
					`Name`	TEXT NOT NULL,\
					`Email`	TEXT NOT NULL,\
					`Mobile`	INTEGER,\
					`Subject`	TEXT NOT NULL,\
					`Message`	TEXT NOT NULL,\
					`QueryDate`	TEXT NOT NULL);')
	conn.close()


createCustomerTable()
createAdminTable()
createAdviserTable()



#-----------------------------------End-----------------------------------------

if __name__ == "__main__":
   app.run()
