from sqlalchemy.orm import relationship
from app import db
import pandas as pd
from app.utils.schedule import from_iso_to_datetime
from datetime import timedelta


class MateriaProfesor(db.Model):

    __tablename__ = 'materias_profesor'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('profesores.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('materias.subject_id'), nullable=False)
    price_ref = db.Column(db.Numeric(10, 2))
    comment = db.Column(db.String(200), nullable=True)

    subject = relationship("Materia", uselist=False, back_populates="tutor_subject")
    tutor = relationship("Profesor", back_populates="tutor_subject")

    def __repr__(self):
        return f"<Materia: {self.subject_id}, Profesor: {self.tutor_id}, Precio Ref: {self.price_ref}>"

    def get_price_table_v(self, factor=1.0):
        return self.create_prices_table(float(self.price_ref) * factor).round(0).to_dict(orient="records")

    def get_price_table_p(self, factor=1.0):
        return self.create_prices_table(float(self.price_ref) * 1.25 * factor).round(0).to_dict(orient="records")

    @staticmethod
    def create_prices_table(price):
        df = pd.DataFrame({
            "factor": [1.0, 0.8, 0.7, 0.6],
            "nr_students": ["Individuales", "De 2 personas", "De 3 personas", "De más personas"]
        })
        df["hour_test"] = df["factor"] * price
        df["hour_x1"] = df["factor"] * 1.5 * price
        df["hour_x5"] = df["factor"] * 6.25 * price
        df["hour_x10"] = df["factor"] * 10 * price
        return df.sort_values("factor", ascending=False)

    @staticmethod
    def get_all():
        return MateriaProfesor.query.all()

    @staticmethod
    def get_by_tutor_id(tutor_id):
        return MateriaProfesor.query.filter(MateriaProfesor.tutor_id.in_([tutor_id])).all()

    @staticmethod
    def get_by_subject_id(subject_id):
        return MateriaProfesor.query.filter(MateriaProfesor.subject_id.in_([subject_id])).all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def remove_by_tutor(tutor_id):
        db.session.query(MateriaProfesor).filter(MateriaProfesor.tutor_id.in_([tutor_id])).delete()
        db.session.commit()


class HorarioProfesorDisponible(db.Model):

    __tablename__ = "horarios_disponibles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("profesores.id"), nullable=False)
    year_index = db.Column(db.Integer, nullable=False)
    week_index = db.Column(db.Integer, nullable=False)
    day_index = db.Column(db.Integer, nullable=False)
    time_index = db.Column(db.Integer, nullable=False)
    availability_type = db.Column(db.Integer, nullable=False)  # 1 es Virtual, 2 es Presencial y 3 es Ambos (VyP)

    def __repr__(self):
        return f"< Profesor: {self.tutor_id} {self.year_index} {self.week_index} {self.day_index} {self.time_index}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def upsert(self):
        slot = db.session.query(HorarioProfesorDisponible).filter(
            HorarioProfesorDisponible.tutor_id == self.tutor_id,
            HorarioProfesorDisponible.year_index == self.year_index,
            HorarioProfesorDisponible.week_index == self.week_index,
            HorarioProfesorDisponible.day_index == self.day_index,
            HorarioProfesorDisponible.time_index == self.time_index
        ).first()
        if slot:
            if self.availability_type == 0:
                db.session.delete(slot)
                db.session.commit()
            else:
                setattr(slot, "availability_type", self.availability_type)
                db.session.commit()
        else:
            self.save()

    def datetime(self):
        return from_iso_to_datetime(
            self.year_index,
            self.week_index,
            self.day_index,
            self.time_index
        )

    def date(self):
        return self.datetime().strftime("%d-%m-%Y")

    def start_time(self):
        return self.datetime().strftime("%H:%M")

    def end_time(self):
        return (self.datetime() + timedelta(minutes=30)).strftime("%H:%M")

    @staticmethod
    def get_tutor_slots_by_isodate(tutor_id, year_index=None, week_index=None, day_index=None, time_index=None):
        filters = [HorarioProfesorDisponible.tutor_id == tutor_id]
        if year_index:
            filters.append(HorarioProfesorDisponible.year_index == year_index)
        if week_index:
            filters.append(HorarioProfesorDisponible.week_index == week_index)
        if day_index:
            filters.append(HorarioProfesorDisponible.day_index == day_index)
        if time_index is not None:
            filters.append(HorarioProfesorDisponible.time_index == time_index)

        return db.session.query(HorarioProfesorDisponible).filter(*filters).all()

    @staticmethod
    def get_all():
        return HorarioProfesorDisponible.query.all()

    @staticmethod
    def get_by_tutor_id(tutor_id):
        return HorarioProfesorDisponible.query.filter(HorarioProfesorDisponible.tutor_id.in_([tutor_id])).all()


class HorarioProfesorReservado(db.Model):

    __tablename__ = "horarios_reservados"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("profesores.id"), nullable=False)
    year_index = db.Column(db.Integer, nullable=False)
    week_index = db.Column(db.Integer, nullable=False)
    day_index = db.Column(db.Integer, nullable=False)
    time_index = db.Column(db.Integer, nullable=False)
    enrolled_type = db.Column(db.Integer, nullable=False)  # 0 es libre, 1 es Reservado y 2 es temporalmente reservado
    enrolled_class_id = db.Column(db.Integer, db.ForeignKey("clases_reservadas.id"), nullable=False)

    def __repr__(self):
        return f"< Profesor: {self.tutor_id} {self.year_index} {self.week_index} {self.day_index} {self.time_index}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def datetime(self):
        return from_iso_to_datetime(
            self.year_index,
            self.week_index,
            self.day_index,
            self.time_index
        )

    def date(self):
        return self.datetime().strftime("%d-%m-%Y")

    def start_time(self):
        return self.datetime().strftime("%H:%M")

    def end_time(self):
        return (self.datetime() + timedelta(minutes=30)).strftime("%H:%M")

    @staticmethod
    def get_all():
        return HorarioProfesorReservado.query.all()

    @staticmethod
    def get_by_class_id(class_id):
        return HorarioProfesorReservado.query.filter(HorarioProfesorReservado.enrolled_class_id.in_([class_id])).all()

    @staticmethod
    def get_by_tutor_id(tutor_id):
        return HorarioProfesorReservado.query.filter(HorarioProfesorReservado.tutor_id.in_([tutor_id])).all()

    @staticmethod
    def get_by_id(slot_id):
        return HorarioProfesorReservado.query.get(slot_id)
