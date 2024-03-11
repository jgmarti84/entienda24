from sqlalchemy.orm import relationship
from sqlalchemy import Column, Numeric
from sqlalchemy.types import TypeDecorator, TEXT
import json
from datetime import datetime, timedelta
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
    enrolled_schedule = relationship("HorarioProfesorReservado", cascade='all, delete')

    def __repr__(self):
        return f"< Profesor: {self.tutor_id} Estudiante: {self.student_id} Materia: {self.subject_id}>"

    def class_length(self):
        return len(self.enrolled_schedule)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        db.session.add(self)
        db.session.commit()

    def date(self):
        return self.enrolled_schedule[0].date()

    def interval(self):
        start_time = self.enrolled_schedule[0].start_time()
        end_time = self.enrolled_schedule[-1].end_time()
        return f"{start_time} - {end_time}"

    def student_info(self):
        if self.status == 1:
            return_status = "Reprogramar Clase"
        elif self.status == 0:
            return_status = "Calificar Clase/Profesor"
        elif self.status == 3:
            return_status = "Seleccionar Horarios"
        else:
            return_status = "Error"
        return return_status

    def tutor_info(self):
        if self.status == 1:
            return_status = "Cancelar Clase"
        elif self.status == 0:
            return_status = "Sin Calificar"
        else:
            return_status = "Ver mas Info"
        return return_status

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def get_by_id(class_id):
        return ClaseReservada.query.get(class_id)

    @staticmethod
    def get_by_student_id(student_id):
        return ClaseReservada.query.filter_by(student_id=student_id).all()

    @staticmethod
    def get_by_tutor_id(tutor_id):
        return ClaseReservada.query.filter_by(tutor_id=tutor_id).all()

    @staticmethod
    def get_by_status(status):
        return ClaseReservada.query.filter(ClaseReservada.status.in_([status])).all()

    @staticmethod
    def update_classes_status(**filters):
        classes = ClaseReservada.query.filter_by(**filters).all()
        for cls in classes:
            if cls.enrolled_schedule[-1].datetime() < datetime.now() + timedelta(minutes=30):
                if cls.status == 1:
                    cls.update(**dict(status=0))
