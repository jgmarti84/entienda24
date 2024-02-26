from sqlalchemy.orm import relationship
from unidecode import unidecode

from app import db


class CodigoPais(db.Model):

    __tablename__ = "codigos_pais"

    code_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    country_abbv = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return f"<{self.country_abbv}: {self.code}>"

    @staticmethod
    def get_all():
        return CodigoPais.query.all()


class Facultad(db.Model):
    __tablename__ = "facultades"

    faculty_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    faculty_name = db.Column(db.String(50), nullable=False)
    university_name = db.Column(db.String(50), nullable=True)

    subjects = relationship("Materia", order_by="Materia.subject_name")

    def __repr__(self):
        return_repr = f"<Facultad {self.faculty_name}"
        if self.university_name:
            return_repr += f" ({self.university_name})"
        return_repr += ">"
        return return_repr

    @staticmethod
    def get_all():
        return Facultad.query.all()

    @staticmethod
    def get_by_faculty_id(faculty_id):
        return Facultad.query.get(faculty_id)


class Materia(db.Model):
    __tablename__ = "materias"

    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_name = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('facultades.faculty_id', ondelete='CASCADE'), nullable=False)
    subject_program = db.Column(db.String(100), nullable=True)

    tutor_subject = relationship("MateriaProfesor", back_populates="subject")
    faculty = relationship("Facultad", back_populates="subjects")
    class_enrolled = relationship("ClaseReservada", back_populates="subject")

    def __repr__(self):
        return f"<Materia {self.subject_name}>"

    def unidecode_subject_name(self):
        return unidecode(self.subject_name).lower()

    @staticmethod
    def get_all():
        return Materia.query.all()

    @staticmethod
    def get_by_subject_id(subject_id):
        return Materia.query.get(subject_id)
