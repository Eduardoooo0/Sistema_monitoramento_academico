from flask import Flask, render_template, request, redirect, url_for, flash, session,make_response
from flask_mysqldb import MySQL
import os
app = Flask(__name__)

app.config['SECRET_KEY'] = 'senha'

# Configurações do MySQL
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('SENHA')
app.config['MYSQL_DB'] = 'db_academico'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')