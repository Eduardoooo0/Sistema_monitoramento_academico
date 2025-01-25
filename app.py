from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session,make_response
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
        cursor.execute("SELECT alu_matricula,alu_email FROM tb_alunos")
        mat_ema = cursor.fetchall()
        matriculas = [row['alu_matricula'] for row in mat_ema]
        emails = [row['alu_email'] for row in mat_ema]
        cursor.execute("SELECT * FROM tb_alunos WHERE alu_id=(%s)", (id,))
        aluno = cursor.fetchone()
        email_atual = aluno['alu_email']
        matricula_atual = aluno['alu_matricula']

        nome = request.form['nome']
        matricula = request.form['matricula']
        email = request.form['email']
        data_nascimento = request.form['data']
        curso = request.form.get('curso')

        # se o email/matricula já estiverem cadastrados
        if email in emails and matricula in matriculas:
            if email != email_atual and matricula != matricula_atual:
                flash('Email e matrícula já cadastrados')
                return redirect(url_for('editar_alunos', id=id))
            elif email != email_atual:
                flash('Email já cadastrado')
                return redirect(url_for('editar_alunos', id=id))
            elif matricula != matricula_atual:
                flash('Matrícula já cadastrada')
                return redirect(url_for('editar_alunos', id=id))
        elif email in emails and email != email_atual:
            flash('Email já cadastrado')
            return redirect(url_for('editar_alunos', id=id))
        elif matricula in matriculas and matricula != matricula_atual:
            flash('Matrícula já cadastrada')
            return redirect(url_for('editar_alunos', id=id))

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


@app.route('/editar_disciplinas/<int:id>', methods=['POST','GET'])
def editar_disciplinas(id):
    cursor = mysql.connection.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM tb_disciplinas JOIN tb_cursos ON dis_cur_id = cur_id JOIN tb_professores ON dis_pro_id = pro_id WHERE dis_id = (%s)', (id,))
        disciplina = cursor.fetchone()
        cursor.execute('SELECT * FROM tb_cursos')
        cursos = cursor.fetchall()
        cursor.execute('SELECT * FROM tb_professores')
        professores = cursor.fetchall()
        return render_template('editar_disciplinas.html', disciplina = disciplina, cursos=cursos, professores=professores)
    
    else:
        cursor.execute("SELECT dis_codigo, dis_nome FROM tb_disciplinas")
        disc = cursor.fetchall()
        cod = [row['dis_codigo'] for row in disc]
        nomes = [row['dis_nome'] for row in disc]
        cursor.execute("SELECT * FROM tb_disciplinas WHERE dis_id = (%s)", (id,))
        disciplina = cursor.fetchone()
        cod_atual = disciplina['dis_codigo']
        nome_atual = disciplina['dis_nome']

        codigo = request.form['codigo']
        nome = request.form['nome']
        curso = request.form.get('curso')
        professor = request.form.get('professor')
        carga_horaria = request.form['carga']

        # se o códico já estiver cadastrado
        if codigo != cod_atual and codigo in cod:
            flash('Código já cadastrado.')
            return redirect(url_for('editar_disciplinas', id=id))
        elif nome != nome_atual and nome in nomes:
            flash('Nome já cadastrado.')
            return redirect(url_for('editar_disciplinas', id=id))
    
        cursor.execute("UPDATE tb_disciplinas SET dis_codigo = (%s), dis_nome = (%s), dis_carga_horaria = (%s), dis_cur_id = (%s), dis_pro_id = (%s) WHERE dis_id = (%s)", 
                       (codigo,nome,carga_horaria,curso,professor,id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('disciplinas'))


@app.route('/excluir_disciplinas/<int:id>', methods=['POST','GET'])
def excluir_disciplinas(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM tb_disciplinas WHERE dis_id = (%s)", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('disciplinas'))


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


@app.route('/frequencia', methods=['POST','GET'])
def frequencia():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tb_disciplinas')
    disciplinas = cursor.fetchall()
    cursor.execute('SELECT * FROM tb_cursos')
    cursos = cursor.fetchall()
    if request.method == 'POST':
        forms = request.form.get('form_type')
        curso = request.form.get('curso')
        disciplina = request.form.get('disciplina')
        cursor.execute('SELECT * FROM tb_disciplinas JOIN tb_cursos ON dis_cur_id = cur_id JOIN tb_alunos ON alu_cur_id = cur_id WHERE dis_cur_id = %s AND dis_id = %s', (curso,disciplina))
        dados = cursor.fetchall()
        if forms == 'form1':
            response = make_response(render_template('frequencia.html', dados=dados, disciplinas=disciplinas,cursos=cursos))
            response.set_cookie('disciplina_id', disciplina)
            response.set_cookie('curso_id', curso)
            return response
        elif forms == 'form2':
            disc = request.cookies.get('disciplina_id')
            curso = request.cookies.get('curso_id')
            cursor.execute('SELECT alu_id AS quant FROM tb_disciplinas JOIN tb_cursos ON dis_cur_id = cur_id JOIN tb_alunos ON alu_cur_id = cur_id WHERE dis_id = %s AND dis_cur_id = %s', (disc,curso))
            quant = cursor.fetchall()
            data = request.form.get('data')
            for alu in quant:
                alu_id = alu['quant']
                presenca = request.form.get(f'presenca_{alu_id}')
                cursor.execute('INSERT INTO tb_frequencia(frq_data,frq_presenca,frq_alu_id,frq_dis_id,frq_cur_id) VALUES (%s,%s,%s,%s,%s)', (data,presenca,alu_id,disc,curso))
                mysql.connection.commit()
            cursor.close()
            return redirect(url_for('frequencia'))
    return render_template('frequencia.html',disciplinas=disciplinas,cursos=cursos )

