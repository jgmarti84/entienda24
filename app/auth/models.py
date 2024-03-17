import numpy as np
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import bcrypt
import pandas as pd
from app.utils.data import dict_without_key
from datetime import date, datetime, timedelta

from app import db
from app.tutor.models import HorarioProfesorDisponible, HorarioProfesorReservado
from app.student.models import ClaseReservada
import app.utils.schedule as schedule
from app.data.static_data import time_index_parser
from hashlib import md5
import pytz


# ba_tz = timezone('America/Argentina/Buenos_Aires')


class Usuario(db.Model, UserMixin):
    """
    Database table schema model to structure information on website tutors.
    """
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_type = db.Column(db.String(1), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    profile_description = db.Column(db.String(400), nullable=True)
    fantasy_name = db.Column(db.String(50), nullable=True)
    profile_picture_path = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')))
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')),
        onupdate=datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))
    )

    _is_tutor = None

    def __repr__(self):
        string_user_type = "Profesor" if self.is_tutor else "Estudiante"
        return f'<Usuario {string_user_type} {self.username} ({self.email})>'

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt()).decode('utf8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf8'), self.password.encode('utf8'))

    @property
    def is_tutor(self):
        if self._is_tutor is None:
            self._is_tutor = self.user_type == 'p'
        return self._is_tutor

    def avatar(self, size):
        avatar_source = self.profile_picture_path
        if not avatar_source:
            digest = md5(self.email.lower().encode('utf-8')).hexdigest()
            avatar_source = f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
        return avatar_source

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        db.session.add(self)
        db.session.commit()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def get_by_id(tutor_id):
        return Usuario.query.get(tutor_id)

    @staticmethod
    def get_by_email(email):
        return Usuario.query.filter_by(email=email).first()

    @staticmethod
    def get_by_username(username):
        return Usuario.query.filter_by(username=username).first()

    @staticmethod
    def get_by_phone(phone):
        return Usuario.query.filter_by(phone=phone).first()

    @staticmethod
    def get_all():
        return Usuario.query.all()


class Profesor(db.Model, UserMixin):
    """
    Database table schema model to structure information on website tutors.
    """
    __tablename__ = "profesores"

    id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    bank_cbu = db.Column(db.String(22), nullable=True)
    bank_alias = db.Column(db.String(64), nullable=True)

    user = relationship("Usuario")
    tutor_subject = relationship("MateriaProfesor")
    availability_schedule = relationship("HorarioProfesorDisponible")
    enrollment_schedule = relationship("HorarioProfesorReservado")
    class_enrolled = relationship("ClaseReservada", back_populates="tutor")

    is_tutor = True

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f'<Profesor {self.user.username} ({self.user.email})>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        db.session.add(self)
        db.session.commit()

    def get_availability_df(self):
        df = pd.DataFrame(columns=HorarioProfesorDisponible.__table__.columns.keys())
        if self.availability_schedule:
            df = pd.DataFrame(dict_without_key(s.__dict__, "_sa_instance_state") for s in self.availability_schedule)
        return df

    def get_enrollment_df(self):
        df = pd.DataFrame(columns=HorarioProfesorReservado.__table__.columns.keys())
        if self.enrollment_schedule:
            df = pd.DataFrame(dict_without_key(s.__dict__, "_sa_instance_state") for s in self.enrollment_schedule)
        return df

    def get_weeks_schedule(self, n_weeks=4):
        base_df = schedule.empty_week_schedules_df(n_weeks=n_weeks)
        availability_df = base_df.merge(self.get_availability_df().drop(["id", "tutor_id"], axis=1), how="left")
        enrollment_df = base_df.merge(self.get_enrollment_df().drop(["id", "tutor_id", "enrolled_class_id"], axis=1), how="left")
        availability_df = schedule.impute_past_availability_slots(availability_df, minutes_lag=-30)
        availability_df = availability_df.groupby(["year_index", "week_index"]).apply(
            lambda x: schedule.slot_schedule_week_to_view(x, schedule_type="availability")
        ).drop(["year_index", "week_index"], axis=1)
        availability_df = availability_df.fillna("").replace(
            {-1: "B", 1: "V", 2: "P", 3: "VyP"}).apply(lambda x: x.tolist(), axis=1)

        enrollment_df = enrollment_df.groupby(["year_index", "week_index"]).apply(
            lambda x: schedule.slot_schedule_week_to_view(x, schedule_type="enrollment")
        ).drop(["year_index", "week_index"], axis=1)
        enrollment_df = enrollment_df.fillna("0").apply(lambda x: x.tolist(), axis=1)

        df = pd.concat([availability_df, enrollment_df], axis=1).rename(
            columns={0: "availability_days", 1: "enrolled_days"}).reset_index()
        df["monday_week_date"] = df.apply(
            lambda x: date.fromisocalendar(year=x["year_index"], week=x["week_index"], day=1),
            axis=1)
        df["time_slot"] = df["time_index"].apply(lambda x: time_index_parser[x])
        return df

    def price_factor(self):
        count_hours = self.count_hours(status=0)
        if count_hours < 0:
            raise Exception("Tutor hours count is less than zero!")
        elif count_hours < 249:
            return_value = 1.5
        elif count_hours < 500:
            return_value = 1.4
        elif count_hours < 750:
            return_value = 1.3
        elif count_hours < 1000:
            return_value = 1.2
        else:
            return_value = 1.1
        return return_value

    def get_classes(self, status=None):
        tutor_logged_classes = ClaseReservada.get_by_tutor_id(self.id)
        if isinstance(status, type(None)):
            status = [0, 1, 2, 3]
        if not isinstance(status, list):
            status = [status]
        clases = [ce for ce in tutor_logged_classes if ce.status in status]
        return clases

    def count_hours(self, status=None):
        clases = self.get_classes(status=status)
        return sum(ce.class_length() / 2 for ce in clases)

    def count_enrollments(self, status=None):
        clases = self.get_classes(status=status)
        return len(clases)

    def mean_score(self):
        if self.count_scores() == 0:
            return np.nan
        scores = [ce.score for ce in self.class_enrolled if ce.score]
        return sum(scores) / len(scores)

    def count_scores(self):
        scores = [ce.score for ce in self.class_enrolled if ce.score]
        return len(scores)

    def availability_hours(self, n_weeks=8):
        schedule_df = self.get_availability_df()
        if not schedule_df.empty:
            schedule_df["datetime_slot"] = schedule_df.apply(
                lambda x: schedule.from_iso_to_datetime(x["year_index"], x["week_index"], x["day_index"], x["time_index"]),
                axis=1
            )
            schedule_df = schedule_df[(schedule_df["datetime_slot"] > datetime.now() + timedelta(minutes=15)) & (
                    schedule_df["week_index"] < datetime.now().isocalendar().week + n_weeks)]
        return float(len(schedule_df) / 2)

    def availability(self, n_weeks=8):
        x = self.availability_hours(n_weeks=n_weeks)
        if x < 5:
            return_value = "baja"
        elif x < 20:
            return_value = "media"
        else:
            return_value = "alta"
        return return_value

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def get_by_id(tutor_id):
        return Profesor.query.get(tutor_id)

    @staticmethod
    def get_all():
        return Profesor.query.all()


class Estudiante(db.Model, UserMixin):
    """
    Database table schema model to structure information on website tutors.
    """
    __tablename__ = "estudiantes"

    id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True, autoincrement=True)

    user = relationship("Usuario")
    class_enrolled = relationship("ClaseReservada", back_populates="student")

    is_tutor = False

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f'<Estudiante {self.user.username} ({self.user.email})>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def get_classes(self, status=None):
        student_logged_classes = ClaseReservada.get_by_student_id(self.id)
        student_logged_classes.extend(
            ClaseReservada.query.filter(ClaseReservada.other_students.contains([self.id])).all())
        if isinstance(status, type(None)):
            status = [0, 1, 2, 3]
        if not isinstance(status, list):
            status = [status]
        clases = [ce for ce in student_logged_classes if ce.status in status]
        return clases

    def count_hours(self, status=None):
        clases = self.get_classes(status=status)
        return sum(ce.class_length() / 2 for ce in clases)

    def has_class_tutor(self, tutor_id):
        clases = self.get_classes(status=[0, 1])
        tutor_clases = [ce for ce in clases if ce.tutor_id == tutor_id]
        return len(tutor_clases) != 0

    def count_enrollments(self, status=None):
        clases = self.get_classes(status=status)
        return len(clases)

    @staticmethod
    def get_by_id(student_id):
        return Estudiante.query.get(student_id)

    @staticmethod
    def get_by_username(username):
        return Usuario.query.filter_by(username=username).first()
