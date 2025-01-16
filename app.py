from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from models import db
from models.tabelas import Alunos
import os
from dotenv import load_dotenv

load_dotenv()

app  = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')