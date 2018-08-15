from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
import sys, os
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, TextAreaField, validators, StringField, PasswordField
from passlib.hash import sha256_crypt

app = Flask(__name__)

#config mysql
app.config['MYSQL_HOST'] = "127.0.0.1"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "myflaskapp"
app.config['MYSQL_CURSORCLASS'] = "DictCursor"
#initialize MYSQL
mysql=MySQL(app)

Articles = Articles()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id = id)

class RegisterForm(Form):
	name = StringField('Name',[validators.Length(min=1,max=50)])
	username = StringField('Username',[validators.Length(min=4,max=25)])
	email = StringField('Email',[validators.Length(min=6,max=50)])
	password = PasswordField('Passowrd',[
		validators.DataRequired(),
		validators.EqualTo('confirm',message='Passwords do not match'),
	])
	confirm = PasswordField('Confirm Password')

@app.route('/register',methods=['GET','POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name= form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		
		cur = mysql.connection.cursor()
		cur.execute("insert into users (name,email,username,password) values( %s,%s,%s,%s)",(name,email,username,password))
		mysql.connection.commit()
		cur.close()
		
		flash("you are now registered and can login",'success')
	
		redirect(url_for('index'))
	return render_template('register.html', form=form)


#user login
@app.route('/login',methods=['GET','POST'])
def login():
	if request.method=="POST":
		username = request.form['username']
		password_candidate = request.form['password']

		cur = mysql.connection.cursor()
		result = cur.execute("select * from users where username = %s",[username])
		if result >0:
			data=cur.fetchone()
			password = data['password']

			if sha256_crypt.verify(password_candidate, password):
				app.logger.info('password matched')
			else:
				app.logger.info('password not matched')
		else:
			app.logger.info('No User')
	return render_template('login.html')

if __name__ == '__main__':
	app.secret_key="secret123"
	app.run(debug=True)
