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
        insert into tb_professores(pro_usu_id)
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



delimiter //
create function fn_calcular_media(id_alu int, id_dis int) 
returns float 
deterministic
begin
    declare media float default 0;  -- inicializa a variável
    select sum(ate_nota * atv_peso) / sum(atv_peso) into media from tb_atividades 
    join tb_atividades_entrega on atv_id = ate_atv_id where ate_alu_id = id_alu and atv_dis_id = id_dis;
    return media;
end //
delimiter ;


delimiter //
create procedure registrar_nota(id_alu int, atv_data date, nota float, id_atv int)
begin
    insert into tb_atividades_entrega(ate_data, ate_nota, ate_atv_id, ate_alu_id) values (atv_data, nota, id_atv, id_alu);
end //
delimiter ;

delimiter //
create trigger verificar_frequencia
before insert on tb_notas
for each row
begin
    declare total_aulas int;
    declare presencas int;
    declare porcentagem float;
    declare id_dis int;
    declare message_text TEXT;
    
    -- ajuste o nome da coluna para referenciar corretamente a atividade
    set id_dis = (select atv_dis_id from tb_atividades join tb_atividades_entrega on ate_atv_id = atv_id where atv_id = new.not_atv_id limit 1);
    
    -- contar o total de aulas
    select count(*) into total_aulas from tb_frequencia where frq_dis_id = id_dis and frq_alu_id = new.not_alu_id;

    -- contar presenças
    select count(*) into presencas from tb_frequencia where frq_dis_id = id_dis and frq_alu_id = new.not_alu_id and frq_presenca = 'presente';
    
    -- calcular a porcentagem de presença
    if total_aulas > 0 then
        set porcentagem = (presencas / total_aulas) * 100;
    else
        set porcentagem = 0;  -- se não houver aulas, a porcentagem é 0%
    end if;
    
    -- impede a inserção se a frequência for inferior a 75%
    if porcentagem < 60 then
		
        set message_text = 'frequência insuficiente para calcular a média.';
    end if;
end //
delimiter ;

CREATE TABLE tb_log_notas (
    log_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    log_operacao TEXT NOT NULL,
    not_id INT,
    not_media INT,
    not_atv_id INT,
    not_alu_id INT,
    not_dis_id INT,
    
    -- Definindo as chaves estrangeiras corretamente
    FOREIGN KEY (not_alu_id) REFERENCES tb_alunos(alu_id),
    FOREIGN KEY (not_dis_id) REFERENCES tb_disciplinas(dis_id),
    FOREIGN KEY (not_atv_id) REFERENCES tb_atividades(atv_id)  -- Presumindo que a tabela de atividades se chama tb_atividades
);



DROP TRIGGER IF EXISTS log_notas;
DROP TRIGGER IF EXISTS log_notas_update;
DROP TRIGGER IF EXISTS log_notas_delete;

DELIMITER //

CREATE TRIGGER log_notas
AFTER INSERT ON tb_notas
FOR EACH ROW
BEGIN
    INSERT INTO tb_log_notas (log_operacao, not_id, not_media, not_atv_id, not_alu_id, not_dis_id)
    VALUES ('INSERT', NEW.not_id, NEW.not_media, NEW.not_atv_id, NEW.not_alu_id, NEW.not_dis_id);
END//

CREATE TRIGGER log_notas_update
AFTER UPDATE ON tb_notas
FOR EACH ROW
BEGIN
    INSERT INTO tb_log_notas (log_operacao, not_id, not_media, not_atv_id, not_alu_id, not_dis_id)
    VALUES ('UPDATE', NEW.not_id, NEW.not_media, NEW.not_atv_id, NEW.not_alu_id, NEW.not_dis_id);
END//

CREATE TRIGGER log_notas_delete
AFTER DELETE ON tb_notas
FOR EACH ROW
BEGIN
    INSERT INTO tb_log_notas (log_operacao, not_id, not_media, not_atv_id, not_alu_id, not_dis_id)
    VALUES ('DELETE', OLD.not_id, OLD.not_media, OLD.not_atv_id, OLD.not_alu_id, OLD.not_dis_id);
END//

DELIMITER ;