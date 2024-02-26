from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, RadioField, SelectField
from wtforms.validators import DataRequired, Email, Length

from app.data.static_data import country_codes


class SignupForm(FlaskForm):

    user_type = RadioField('Estudiante/Profesor', validators=[DataRequired()], choices=[('s', 'Estudiante'), ('p', 'Profesor')], default="p")
    username = StringField('Usuario', validators=[DataRequired(), Length(max=64)])
    name = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    last_name = StringField("Apellido", validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_country_code = SelectField('Pais', choices=country_codes, default=54)
    phone_city_code = StringField('Codigo de Area')
    phone = StringField('Telefono', validators=[DataRequired()])

    submit = SubmitField('Registrar')

    # def validate_phone(self):
    #     try:
    #         p = phonenumbers.parse(self.phone.data)
    #         if not phonenumbers.is_valid_number(p):
    #             raise ValueError()
    #     except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
    #         raise ValidationError('El Número de teléfono no es válido')


class LoginForm(FlaskForm):

    username_email = StringField('Usuario/Email', validators=[DataRequired(), Length(max=128)])
    password = PasswordField('Password', validators=[DataRequired()])

    remember_me = BooleanField('Recuérdame')