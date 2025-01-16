from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, DateTime
from models import db

class Alunos(db.Model):
    __tablename__ = 'tb_alunos'
    alu_id:Mapped[int] = mapped_column(primary_key=True, nullable=False)
    alu_nome:Mapped[str] = mapped_column(db.String(100),nullable=False)
    alu_matricula:Mapped[int] = mapped_column(nullable=False)
    alu_email:Mapped[str] = mapped_column(db.String(100) ,unique=True, nullable=False)
    alu_curso:Mapped[str] = mapped_column(db.String(100), nullable=False)
    alu_data_nascimento:Mapped[DateTime] = mapped_column(Date, nullable=False)