from sqlalchemy.orm import relationship
from sqlalchemy import Column, Numeric
from sqlalchemy.types import TypeDecorator, TEXT
import json

from app import db


class JSONList(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class ClaseReservada(db.Model):
    """
    Database table schema model to structure information on website assigned or enrolled classes.
    """
    __tablename__ = "clases_reservadas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('profesores.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('materias.subject_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=False)
    status = db.Column(db.Integer, nullable=False) # 2: temporalmente reservada en espera del comprobante, 1: reservada y pagada, en espera de haber sido dada, 0: clase dada 3: cancelada/reprogramada
    class_type = db.Column(db.String(5), nullable=False)
    other_students = db.Column(JSONList, nullable=True)
    score = Column(Numeric(10, 2), nullable=True)

    student = relationship("Estudiante", back_populates="class_enrolled")
    tutor = relationship("Profesor", back_populates="class_enrolled")
    subject = relationship("Materia", back_populates="class_enrolled")
    enrolled_schedule = relationship("HorarioProfesorReservado")


    def __repr__(self):
        return f"< Profesor: {self.tutor_id} Estudiante: {self.student_id} Materia: {self.subject_id}>"

    def class_length(self):
        return float(len(self.enrolled_schedule)) / 2.