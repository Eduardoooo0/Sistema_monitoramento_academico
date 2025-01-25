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

@app.route('/alunos')
def alunos():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tb_alunos JOIN tb_cursos ON alu_cur_id = cur_id')
    alunos = cursor.fetchall()
    
    return render_template('alunos.html',alunos=alunos)

@app.route('/disciplinas')
def disciplinas():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tb_disciplinas JOIN tb_cursos ON dis_cur_id = cur_id JOIN tb_professores ON dis_pro_id = pro_id')
    disciplinas = cursor.fetchall()
    
    return render_template('disciplinas.html',disciplinas=disciplinas)

@app.route('/atividades')
def atividades():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tb_atividades JOIN tb_disciplinas ON atv_dis_id = dis_id JOIN tb_cursos ON cur_id = dis_cur_id JOIN tb_professores ON dis_pro_id = pro_id')
    atividades = cursor.fetchall()
    
    return render_template('atividades.html',atividades=atividades)

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
        return redirect(url_for('alunos'))
    cursor.execute('SELECT * FROM tb_cursos')
    cursos = cursor.fetchall()
    return render_template('cadastro_alunos.html', cursos=cursos)


@app.route('/editar_alunos/<int:id>', methods=['POST','GET'])
def editar_alunos(id):
    cursor = mysql.connection.cursor()
    if request.method == 'GET':
        alu_id = id
        cursor.execute('SELECT * FROM tb_alunos JOIN tb_cursos ON alu_cur_id = cur_id WHERE alu_id = (%s)', (alu_id,))
        aluno = cursor.fetchone()
        cursor.execute('SELECT * FROM tb_cursos')
        cursos = cursor.fetchall()
        return render_template('editar_alunos.html', aluno = aluno, cursos=cursos)
    
    else:
        nome = request.form['nome']
        matricula = request.form['matricula']
        email = request.form['email']
        data_nascimento = request.form['data']
        curso = request.form.get('curso')

        cursor.execute('UPDATE tb_alunos SET alu_nome = (%s), alu_matricula = (%s), alu_email = (%s), alu_data_nascimento = (%s), alu_cur_id = (%s) WHERE alu_id = (%s)',
                       (nome, matricula, email, data_nascimento, curso, id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('alunos'))


@app.route('/excluir_alunos/<int:id>', methods=['POST','GET'])
def excluir_alunos(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM tb_alunos WHERE alu_id = (%s)", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('alunos'))



@app.route('/cadastro_disciplinas', methods=['POST','GET'])
def cadastro_disciplinas():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        cursor.execute("SELECT dis_codigo FROM tb_disciplinas")
        cod = cursor.fetchall()
        cod = [row['dis_codigo'] for row in cod]
        codigo = request.form['codigo']
        nome = request.form['nome']
        curso = request.form.get('curso')
        professor = request.form.get('professor')
        carga_horaria = request.form['carga']
        if codigo in cod:
            flash('Código já cadastrado.')
            return redirect(url_for('cadastro_disciplinas'))
        cursor.execute("INSERT INTO tb_disciplinas(dis_codigo,dis_nome,dis_carga_horaria,dis_cur_id, dis_pro_id) VALUES (%s,%s,%s,%s,%s)", (codigo,nome,carga_horaria,curso,professor))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('disciplinas'))
    cursor.execute('SELECT * FROM tb_professores')
    professores = cursor.fetchall()
    cursor.execute('SELECT * FROM tb_cursos')
    cursos = cursor.fetchall()
    return render_template('cadastro_disciplinas.html', cursos=cursos, professores=professores)

@app.route('/cadastro_atividades', methods=['POST','GET'])
def cadastro_atividades():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        titulo = request.form['titulo']
        tipo = request.form.get('tipo')
        descricao = request.form['descricao']
        bimestre = request.form.get('bimestre')
        peso = request.form['peso']
        data_entrega = request.form['data']
        disciplina = request.form.get('disciplina')
        cursor.execute("INSERT INTO tb_atividades(atv_titulo,atv_tipo,atv_descricao,atv_bimestre,atv_peso,atv_data,atv_dis_id) VALUES (%s,%s,%s,%s,%s,%s,%s)", (titulo,tipo,descricao,bimestre,peso,data_entrega,disciplina))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('atividades'))
    cursor.execute('SELECT * FROM tb_disciplinas')
    disciplinas = cursor.fetchall()
    return render_template('cadastro_atv.html', disciplinas=disciplinas)

@app.route('/cadastro_entregas', methods=['POST','GET'])
def cadastro_entregas():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        atividade = request.form.get('atividade')
        aluno = request.form.get('aluno')
        data = request.form['data']
        nota = request.form['nota']
        cursor.execute('INSERT INTO tb_atividades_entrega(ate_data,ate_nota,ate_atv_id,ate_alu_id) VALUES (%s,%s,%s,%s)',(data,nota,atividade,aluno))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('atividades'))
    cursor.execute('SELECT * FROM tb_atividades JOIN tb_disciplinas ON atv_dis_id = dis_id JOIN tb_cursos ON dis_cur_id = cur_id JOIN tb_alunos ON cur_id = alu_cur_id')
    dados = cursor.fetchall()
    cursor.execute('SELECT * FROM tb_alunos')
    alunos = cursor.fetchall()
    return render_template('cadastro_entregas.html', dados=dados,alunos=alunos)
