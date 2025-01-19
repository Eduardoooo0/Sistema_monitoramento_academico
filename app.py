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


@app.route('/cadastro_alunos', methods=['GET','POST'])
def cadastro_alunos():
    cursor = mysql.connection.cursor()
    if request.method ==   'POST':
        cursor.execute("SELECT alu_matricula,alu_email FROM tb_alunos")
        mat_ema = cursor.fetchall()
        matriculas = [row['alu_matricula'] for row in mat_ema]
        emails = [row['alu_email'] for row in mat_ema]
        nome = request.form['nome']
        matricula = request.form['matricula']
        email = request.form['email']
        data_nascimento = request.form['data']
        curso = request.form.get('curso')
        if email and matricula:
            if email in emails and matricula in matriculas:
                flash('Email e matrícula já cadastrados')
                return redirect(url_for('cadastro_alunos'))
            elif email in emails:
                flash('Email já cadastrado')
                return redirect(url_for('cadastro_alunos'))
            elif matricula in matriculas:
                flash('Matrícula já cadastrada')
                return redirect(url_for('cadastro_alunos'))
        cursor.execute("INSERT INTO tb_alunos(alu_nome,alu_matricula,alu_email,alu_data_nascimento, alu_cur_id) VALUES (%s,%s,%s,%s,%s)", (nome,matricula,email,data_nascimento,curso))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('index'))
    cursor.execute('SELECT * FROM tb_cursos')
    cursos = cursor.fetchall()
    return render_template('cadastro_alunos.html', cursos=cursos)