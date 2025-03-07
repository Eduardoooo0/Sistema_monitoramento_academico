drop database if exists db_academico;
create database db_academico;
use db_academico;



create table tb_usuarios(
	usu_id int auto_increment not null primary key,
    usu_nome varchar(100) not null,
    usu_email varchar(100) not null unique,
    usu_data_nascimento date,
    usu_tipo enum('Aluno','Professor','Admin'),
    usu_senha text not null
);


create table tb_professores(
	pro_id int auto_increment not null primary key,
    pro_usu_id int,
    foreign key (pro_usu_id) references tb_usuarios(usu_id)
);

delimiter //

create trigger add_foreign after insert
on tb_usuarios
for each row
begin
	if new.usu_tipo = 'Aluno' then
        insert into tb_alunos(alu_usu_id)
        values (new.usu_id);
    end if;
    
    if new.usu_tipo = 'Professor' then
        insert into tb_Professores(pro_usu_id)
        values (new.usu_id);
    end if;
end//

delimiter ;

/*insert into tb_professores(pro_nome) values 
('Romerito'),
('Hugo'),
('Cleysyvan'),
('Julianna'),
('Pablo'),
('Vinicius'),
('Jossefrania'),
('Mazé'),
('Janduir'),
('Cícero'),
('Iuri');*/

create table tb_cursos(
	cur_id int auto_increment not null primary key,
    cur_nome varchar(100) not null
);


 insert into tb_cursos(cur_nome) values 
 ('Infoweb'),
 ('Têxtil'),
 ('Eletrotécnica'),
 ('Vestuário'),
 ('Design de moda'),
 ('Física');
 
create table tb_alunos(
	alu_id int auto_increment not null primary key,
    alu_matricula varchar(20) unique,
    alu_cur_id int,
    alu_usu_id int,
    foreign key (alu_cur_id) references tb_cursos(cur_id),
    foreign key (alu_usu_id) references tb_usuarios(usu_id)
);

create table tb_disciplinas(
	dis_id int auto_increment not null primary key,
    dis_codigo varchar(100) not null unique,
    dis_nome varchar(100) not null,
    dis_carga_horaria int not null,
    dis_pro_id int,
    dis_cur_id int,
    foreign key (dis_pro_id) references tb_professores(pro_id),
    foreign key (dis_cur_id) references tb_cursos(cur_id)
);


create table tb_atividades(
	atv_id int auto_increment not null primary key,
    atv_titulo varchar(100) not null,
    atv_tipo enum('Projeto','Trabalho','Prova') default 'Trabalho',
    atv_descricao text,
    atv_bimestre enum('1','2','3','4') default '1',
    atv_peso float not null,
    atv_data date not null,
    atv_dis_id int,
    foreign key (atv_dis_id) references tb_disciplinas(dis_id)
);


create table tb_atividades_entrega(
	ate_id int auto_increment not null primary key,
    ate_data date not null,
    ate_nota float not null,
    ate_atv_id int,
    ate_alu_id int,
    foreign key (ate_atv_id) references tb_atividades(atv_id),
	foreign key (ate_alu_id) references tb_alunos(alu_id)
);

create table tb_notas(
	not_id int auto_increment not null primary key,
    not_media int not null,
    not_atv_id int,
    not_alu_id int,
    not_dis_id int,
    foreign key (not_atv_id) references tb_atividades(atv_id),
    foreign key (not_alu_id) references tb_alunos(alu_id),
    foreign key (not_dis_id) references tb_disciplinas(dis_id)
);



create table tb_frequencia(
	frq_id int auto_increment not null primary key,
    frq_data date not null,
    frq_presenca enum('Presente','Falta') default 'Presente',
    frq_alu_id int,
    frq_dis_id int,
    frq_cur_id int,
    foreign key (frq_alu_id) references tb_alunos(alu_id),
    foreign key (frq_dis_id) references tb_disciplinas(dis_id),
    foreign key (frq_cur_id) references tb_cursos(cur_id)
);

