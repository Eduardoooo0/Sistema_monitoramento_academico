from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session,make_response
from flask_mysqldb import MySQL
import os
from flask_login import LoginManager, current_user, login_required,login_user, logout_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from pymysql import DatabaseError

app = Flask(__name__)

app.config['SECRET_KEY'] = 'senha'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.login'

# Configurações do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'marcella123'
app.config['MYSQL_DB'] = 'db_academico'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_SSL_DISABLE'] = True

mysql = MySQL(app)

class User(UserMixin):
    def __init__(self, id, username,type):
        self.id = id
        self.username = username
        self.type = type

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT usu_id,usu_nome,usu_tipo FROM tb_usuarios WHERE usu_id = (%s)',(user_id))
    user = cursor.fetchone()
    return User(user['usu_id'],user['usu_nome'],user['usu_tipo'])



@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/professores')
def professores():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tb_professores JOIN tb_usuarios ON pro_usu_id = usu_id')
    dados = cursor.fetchall()
    return render_template('professores.html', dados=dados) 

@app.route('/alunos')
def alunos():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tb_alunos JOIN tb_cursos ON alu_cur_id = cur_id JOIN tb_usuarios ON alu_usu_id = usu_id')
    alunos = cursor.fetchall()
    cursor.execute('SELECT * FROM tb_cursos')
    cursos = cursor.fetchall()

    return render_template('alunos.html',alunos=alunos, cursos = cursos)

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
def cadastro_usuarios():
    cursor = mysql.connection.cursor()
    if request.method ==   'POST':
        cursor.execute("SELECT alu_matricula,usu_email FROM tb_alunos JOIN tb_usuarios ON alu_usu_id = usu_id")
        mat_ema = cursor.fetchall()
        matriculas = [row['alu_matricula'] for row in mat_ema]
        emails = [row['usu_email'] for row in mat_ema]
        tipo = request.form.get('tipo')
        nome = request.form['nome']
        email = request.form['email']
        data_nascimento = request.form['data']
        curso = request.form.get('curso')
        senha = generate_password_hash(os.getenv('SENHA'))
        if tipo == 'Aluno':
            matricula = request.form['matricula']
            if email and matricula:
                if email in emails and matricula in matriculas:
                    flash('Email e matrícula já cadastrados')
                    return redirect(url_for('cadastro_usuarios'))
                elif email in emails:
                    flash('Email já cadastrado')
                    return redirect(url_for('cadastro_usuarios'))
                elif matricula in matriculas:
                    flash('Matrícula já cadastrada')
                    return redirect(url_for('cadastro_usuarios'))
            cursor.execute("INSERT INTO tb_usuarios(usu_nome,usu_email,usu_data_nascimento,usu_tipo,usu_senha) VALUES (%s,%s,%s,%s,%s)", (nome,email,data_nascimento,tipo,senha))
            mysql.connection.commit()
            cursor.execute('SELECT usu_id FROM tb_usuarios WHERE usu_email = %s',(email,))
            id = cursor.fetchone()
            cursor.execute('SELECT alu_id FROM tb_alunos JOIN tb_usuarios ON alu_usu_id = usu_id WHERE alu_usu_id = %s',(str(id['usu_id'])))
            dados = cursor.fetchone()
            cursor.execute('UPDATE tb_alunos SET alu_matricula = %s,alu_cur_id = %s WHERE alu_id = %s', (matricula,curso,str(dados['alu_id'])))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('alunos'))
        elif tipo == 'Professor':
            if email in emails:
                flash('Email já cadastrado')
                return redirect(url_for('cadastro_usuarios'))
            cursor.execute("INSERT INTO tb_usuarios(usu_nome,usu_email,usu_data_nascimento,usu_tipo,usu_senha) VALUES (%s,%s,%s,%s,%s)", (nome,email,data_nascimento,tipo,senha))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('professores'))
        cursor.close()
    cursor.execute('SELECT * FROM tb_cursos')
    cursos = cursor.fetchall()
    return render_template('cadastro_alunos.html', cursos=cursos)


@app.route('/editar_senha',methods=['POST','GET'])
def editar_senha():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        cursor.execute('SELECT * FROM tb_usuarios WHERE usu_email = %s',(email,))
        dados = cursor.fetchone()
        if dados:
            cursor.execute('UPDATE tb_usuarios SET usu_senha = %s WHERE usu_email = %s',(generate_password_hash(senha),email))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('login'))
        else:
            flash('email incorreto')
            return render_template('editar_senha.html')
    return render_template('editar_senha.html')
@app.route('/login', methods = ['POST','GET'])
def login():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        cursor.execute('SELECT * FROM tb_usuarios WHERE usu_email=(%s)',(email,))
        user = cursor.fetchone()
        check_senha = check_password_hash(user['usu_senha'],senha)
        if email and check_senha:
            user = User(user['usu_id'],user['usu_nome'],user['usu_tipo'])
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Email ou senha inválido(s).')
            return render_template('login.html')
    cursor.execute('SELECT * FROM tb_usuarios WHERE usu_id=1')
    admin = cursor.fetchone()
    if admin is None:
        cursor.execute('INSERT INTO tb_usuarios(usu_nome,usu_email,usu_senha, usu_tipo) VALUES (%s,%s,%s,%s)',(os.getenv('NOME'),os.getenv('EMAIL'),generate_password_hash(os.getenv('SENHA')),os.getenv('TIPO')))
        mysql.connection.commit()
        cursor.close()
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!!!')
    return redirect(url_for('login'))

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


@app.route('/filtrar_alunos', methods=['POST','GET'])
def filtrar_alunos():
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT alu_id FROM tb_alunos")
    ids = cursor.fetchall()
    ids = [row['alu_id'] for row in ids]
    ids_alu = ','.join(map(str, ids))

    col_nome = request.form.get('nome')
    col_matricula = request.form.get('matricula')
    col_email = request.form.get('email')
    col_data_nascimento = request.form.get('data')
    col_curso = request.form.get('curso')

    text = f"SELECT alu_id, alu_nome, alu_matricula, alu_email, alu_data_nascimento, alu_cur_id, cur_nome FROM tb_alunos JOIN tb_cursos on alu_cur_id = cur_id WHERE alu_id in ({ids_alu})"

    if col_nome:
        text += f" and alu_nome = '{col_nome}'"
    if col_matricula :
        text += f" and alu_matricula = '{col_matricula}'"
    if col_email :
        text += f" and alu_email = '{col_email}'"
    if col_data_nascimento :
        text += f" and alu_data_nascimento = '{col_data_nascimento}'"
    if col_curso:
        text += f" and alu_cur_id = '{col_curso}'"
    
    cursor.execute(text)
    alunos = cursor.fetchall()
    cursor.execute('SELECT * FROM tb_cursos')
    cursos = cursor.fetchall()
    return render_template('alunos.html', alunos=alunos, cursos=cursos)


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
    cursor.execute('SELECT * FROM tb_professores JOIN tb_usuarios on pro_usu_id = usu_id')
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
    
        cursor.execute("UPDATE tb_disciplinas SET dis_codigo = (%s), dis_nome = (%s), dis_carga_horaria = (%s), dis_cur_id = (%s), dis_pro_id = (%s) WHERE dis_id = (%s)", (codigo,nome,carga_horaria,curso,professor,id))
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


@app.route('/filtrar_disciplinas', methods=['POST','GET'])
def filtrar_disciplinas():
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT dis_id FROM tb_disciplinas")
    ids = cursor.fetchall()
    ids = [row['dis_id'] for row in ids]
    ids_dis = ','.join(map(str, ids))

    col_codigo = request.form.get('codigo')
    col_nome = request.form.get('nome')
    col_curso = request.form.get('curso')
    col_professor = request.form.get('professor')
    col_carga_horaria = request.form.get('carga')

    text = f"SELECT dis_id, dis_nome, dis_codigo, dis_cur_id, dis_pro_id, dis_carga_horaria, cur_nome, pro_nome FROM tb_disciplinas JOIN tb_cursos on dis_cur_id = cur_id JOIN tb_professores ON dis_pro_id = pro_id WHERE dis_id in ({ids_dis})"

    if col_nome:
        text += f" and dis_nome = '{col_nome}'"
    if col_codigo :
        text += f" and dis_codigo = '{col_codigo}'"
    if col_curso :
        text += f" and dis_cur_id = '{col_curso}'"
    if col_professor :
        text += f" and dis_pro_id = '{col_professor}'"
    if col_carga_horaria:
        text += f" and dis_carga_horaria = '{col_carga_horaria}'"
    
    cursor.execute(text)
    disciplinas = cursor.fetchall()
    cursor.execute('SELECT * FROM tb_cursos')
    cursos = cursor.fetchall()
    cursor.execute('SELECT * FROM tb_professores')
    professores = cursor.fetchall()
    return render_template('disciplinas.html', disciplinas=disciplinas, cursos=cursos, professores=professores)



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



@app.route('/editar_atividades/<int:id>', methods=['POST','GET'])
def editar_atividades(id):
    cursor = mysql.connection.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM tb_atividades JOIN tb_disciplinas ON atv_dis_id = dis_id WHERE atv_id = (%s)', (id,))
        atv = cursor.fetchone()
        cursor.execute('SELECT * FROM tb_disciplinas')
        disciplinas = cursor.fetchall()
        return render_template('editar_atividades.html', atv=atv, disciplinas=disciplinas)

    else:
        titulo = request.form['titulo']
        tipo = request.form.get('tipo')
        descricao = request.form['descricao']
        bimestre = request.form.get('bimestre')
        peso = request.form['peso']
        data_entrega = request.form['data']
        disciplina = request.form.get('disciplina')

        cursor.execute("UPDATE tb_atividades SET atv_titulo = (%s), atv_tipo = (%s), atv_descricao = (%s), atv_bimestre = (%s), atv_peso = (%s), atv_data = (%s), atv_dis_id = (%s) WHERE atv_id = (%s)", 
                       (titulo,tipo,descricao,bimestre,peso,data_entrega,disciplina,id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('atividades'))
    
@app.route('/excluir_atividades/<int:id>', methods=['POST','GET'])
def excluir_atividades(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM tb_atividades WHERE atv_id = (%s)", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('atividades'))


@app.route('/filtrar_atividades', methods=['POST','GET'])
def filtrar_atividades():
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT atv_id FROM tb_atividades")
    ids = cursor.fetchall()
    ids = [row['atv_id'] for row in ids]
    ids_atv = ','.join(map(str, ids))

    col_titulo = request.form.get('titulo')
    col_tipo = request.form.get('tipo')
    col_descricao = request.form.get('descricao')
    col_bimestre = request.form.get('bimestre')
    col_peso = request.form.get('peso')
    col_data_entrega = request.form.get('data')
    col_disciplina = request.form.get('disciplina')

    text = f"SELECT atv_id, atv_titulo, atv_tipo, atv_descricao, atv_bimestre, atv_peso, atv_data, atv_dis_id, dis_nome, cur_nome, pro_nome FROM tb_atividades JOIN tb_disciplinas on atv_dis_id = dis_id JOIN tb_cursos ON cur_id = dis_cur_id JOIN tb_professores ON dis_pro_id = pro_id WHERE atv_id in ({ids_atv})"

    if col_titulo:
        text += f" and atv_titulo = '{col_titulo}'"
    if col_tipo :
        text += f" and atv_tipo = '{col_tipo}'"
    if col_descricao :
        text += f" and atv_descricao = '{col_descricao}'"
    if col_bimestre :
        text += f" and atv_bimestre = '{col_bimestre}'"
    if col_peso:
        text += f" and atv_peso = '{col_peso}'"
    if col_data_entrega:
        text += f" and atv_data = '{col_data_entrega}'"
    if col_disciplina:
        text += f" and atv_dis_id = '{col_disciplina}'"
    
    cursor.execute(text)
    atividades = cursor.fetchall()
    cursor.execute('SELECT * FROM tb_disciplinas')
    disciplinas = cursor.fetchall()
    return render_template('atividades.html', atividades=atividades, disciplinas=disciplinas)

    

@app.route('/cadastro_entregas', methods=['POST','GET'])
def cadastro_entregas():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        atividade = request.form.get('atividade')
        aluno = request.form.get('aluno')
        data = request.form['data']
        nota = request.form['nota']

        cursor.callproc('registrar_nota', (aluno, data, nota, atividade))
        mysql.connection.commit()

        cursor.execute('SELECT dis_id FROM tb_disciplinas JOIN tb_atividades ON atv_dis_id = dis_id WHERE atv_id = %s', (atividade,))
        # Obtendo o resultado
        disciplina = cursor.fetchone()

        # Verifica se a nota já existe
        cursor.execute('SELECT * FROM tb_notas WHERE not_alu_id = %s', (aluno))
        resultado = cursor.fetchone()
        if resultado:
            # Atualiza a nota existente
            cursor.execute('UPDATE tb_notas SET not_media = fn_calcular_media(%s, %s) WHERE not_alu_id = %s', (aluno, str(disciplina['dis_id']), aluno))
            mysql.connection.commit()
            cursor.execute('SELECT * FROM tb_notas WHERE not_alu_id = %s', (aluno))
        else:
            try:
                # Tentando inserir na tabela
                cursor.execute("""
                    INSERT INTO tb_notas (not_alu_id, not_atv_id, not_dis_id, not_media)
                    VALUES (%s, %s, %s, fn_calcular_media(%s, %s))
                """, (aluno, atividade,  str(disciplina['dis_id']), aluno, str(disciplina['dis_id'])))
                
                # Comitando as mudanças
                mysql.connection.commit()

            except DatabaseError as e:
                # Verificando se o erro é relacionado à frequência
                if "Frequência insuficiente para calcular a média." in str(e):
                    print("Erro: A frequência do aluno é insuficiente. Não é possível inserir a nota.")
                    cursor.execute("""
                        INSERT INTO tb_notas (not_alu_id, not_atv_id, not_dis_id, not_media)
                        VALUES (%s, %s, %s, 'frequencia insuficiente')
                    """, (aluno, atividade, disciplina))
                    mysql.connection.commit()
                else:
                    print("Erro inesperado:", e)

            finally:
                # Fechando o cursor
                cursor.close()



            # Insere nova nota
            #cursor.execute('INSERT INTO tb_notas(not_alu_id, not_atv_id,not_dis_id, not_media) VALUES (%s, %s, %s,%s)', (aluno, atividade, disciplina['dis_id'] ,media['media']))
            #mysql.connection.commit()
        #cursor.close()
        return redirect(url_for('atividades'))
    cursor.execute('SELECT * FROM tb_atividades')
    dados = cursor.fetchall()
    cursor.execute('SELECT * FROM tb_alunos JOIN tb_usuarios on alu_usu_id = usu_id')
    alunos = cursor.fetchall()
    return render_template('cadastro_entregas.html', dados=dados,alunos=alunos)

@app.route('/frequencia', methods=['POST','GET'])
def frequencia():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tb_disciplinas')
    disciplinas = cursor.fetchall()
    cursor.execute('SELECT * FROM tb_cursos')
    cursos = cursor.fetchall()
    cursor.execute('SELECT * FROM tb_alunos JOIN tb_usuarios on alu_usu_id = usu_id')
    alunos = cursor.fetchall()
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
        
    return render_template('frequencia.html',disciplinas=disciplinas,cursos=cursos, dados=alunos )


@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html')


@app.route('/exibir_media')
def exibir_media():
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * 
        FROM tb_notas 
        JOIN tb_atividades ON not_atv_id = atv_id 
        JOIN tb_alunos ON not_alu_id = alu_id 
        JOIN tb_disciplinas ON not_dis_id = dis_id 
        JOIN tb_usuarios ON alu_usu_id = usu_id
    ''')
    #cursor.execute('SELECT * FROM tb_notas JOIN tb_atividades ON not_atv_id = atv_id JOIN tb_alunos ON not_alu_id = alu_id JOIN tb_disciplinas ON not_dis_id = dis_id JOIN tb_usuario on alu_usu_id = usu_id)')
    media = cursor.fetchall()
    return render_template('exibir_media.html', media=media)

@app.route('/exibir_entregas', methods=['POST','GET'])
def exibir_entregas():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        filtro = request.form.get('tipo')
        if filtro == 'Aluno':
            cursor.execute('SELECT alu_nome, COUNT(*) AS total_entregas FROM tb_atividades_entrega JOIN tb_alunos ON alu_id = ate_alu_id GROUP BY alu_nome')
            atividades = cursor.fetchall()
            cursor.execute('SELECT atv_titulo AS title FROM tb_atividades')
            nomes = cursor.fetchall()
            return render_template('exibir_entregas.html',filtro=filtro,atividades=atividades, nomes=nomes)
        elif filtro == 'Disciplina':
            cursor.execute('SELECT dis_nome, COUNT(*) AS total_entregas FROM tb_atividades_entrega JOIN tb_atividades ON ate_atv_id = atv_id JOIN tb_disciplinas ON dis_id = atv_dis_id GROUP BY dis_nome')
            disciplinas = cursor.fetchall()
            cursor.execute('SELECT atv_titulo AS title FROM tb_atividades')
            nomes = cursor.fetchall()
            return render_template('exibir_entregas.html',filtro=filtro,atividades=disciplinas,nomes=nomes)
        elif filtro == 'prazo':
            cursor.execute('SELECT atv_titulo FROM tb_atividades JOIN tb_atividades_entrega ON atv_id = ate_atv_id WHERE ate_data > atv_data')
            datas = cursor.fetchall()
            cursor.execute('SELECT atv_titulo AS title FROM tb_atividades')
            nomes = cursor.fetchall()
            return render_template('exibir_entregas.html',filtro=filtro,atividades=datas,nomes=nomes)
    return render_template('exibir_entregas.html',filtro='',alunos='')


@app.route('/register', methods=['POST','GET'])
def register():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        nome = request.form['nome']
        tipo = request.form.get('tipo')
        cursor.execute('SELECT * FROM tb_usuarios WHERE usu_email = %s',(email,))
        user = cursor.fetchone()
        if user:
            flash('Email já cadastrado.')
            return redirect(url_for('register'))
        cursor.execute('INSERT INTO tb_usuarios(usu_nome,usu_email,usu_senha,usu_tipo) VALUES (%s,%s,%s,%s)',(nome,email,generate_password_hash(senha),tipo))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('login'))
    return render_template('register.html')





@app.route('/logs')
def logs():

    cursor = mysql.connection.cursor()

    cursor.execute('SELECT * FROM tb_log_notas JOIN tb_disciplinas ON not_dis_id = dis_id JOIN tb_alunos on not_alu_id = alu_id JOIN tb_usuarios on alu_usu_id = usu_id')
    logs = cursor.fetchall()
    print(logs)
    return render_template('logs.html', logs=logs)


