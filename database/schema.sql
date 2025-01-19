drop database if exists db_academico;
create database db_academico;
use db_academico;

create table tb_professores(
	pro_id int auto_increment not null primary key,
	pro_nome varchar(100) not null
);

create table tb_cursos(
	cur_id int auto_increment not null primary key,
    cur_nome varchar(100) not null
);

create table tb_alunos(
	alu_id int auto_increment not null primary key,
    alu_matricula varchar(20) not null unique,
    alu_nome varchar(100) not null,
    alu_email varchar(100) unique,
    alu_data_nascimento date,
    alu_cur_id int,
    foreign key (alu_cur_id) references tb_cursos(cur_id)
);

create table tb_disciplinas(
	dis_id int auto_increment not null primary key,
    dis_nome varchar(100) not null,
    dis_carga_horaria int not null,
    dis_pro_id int,
    dis_cur_id int,
    foreign key (dis_pro_id) references tb_professores(pro_id),
    foreign key (dis_cur_id) references tb_cursos(cur_id)
);

create table tb_notas(
	not_id int auto_increment not null primary key,
    not_nota float not null,
    not_bimestre enum('1','2','3','4') default '1',
    not_alu_id int,
    foreign key (not_alu_id) references tb_alunos(alu_id)
);

create table tb_atividades(
	atv_id int auto_increment not null primary key,
    atv_tipo enum('Projeto','Trabalho','Prova') default 'Trabalho',
    atv_descricao text,
    atv_peso float not null,
    atv_alu_id int,
    atv_not_id int,
    foreign key (atv_alu_id) references tb_alunos(alu_id),
    foreign key (atv_not_id) references tb_notas(not_id)
);

create table tb_frequencia(
	frq_id int auto_increment not null primary key,
    frq_falta int default 0,
    frq_alu_id int,
    foreign key (frq_alu_id) references tb_alunos(alu_id)

);

insert into tb_cursos(cur_nome) values 
('Infoweb'),
('Têxtil'),
('Eletrotécnica'),
('Vestuário'),
('Design de moda'),
('Física');
