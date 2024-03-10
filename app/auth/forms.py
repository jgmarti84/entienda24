from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, RadioField, SelectField, TextAreaField, IntegerField
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


class LoginForm(FlaskForm):

    username_email = StringField('Usuario/Email', validators=[DataRequired(), Length(max=128)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128)])

    remember_me = BooleanField('Recuérdame')


class ModifyPasswordForm(FlaskForm):

    old_password = PasswordField('Password Viejo', validators=[DataRequired()])
    new_password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Modificar Contraseña')


class EditUserProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    name = StringField('Usuario', validators=[DataRequired(), Length(max=64)])
    last_name = StringField("Apellido", validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_country_code = SelectField('Pais', choices=country_codes)
    phone_city_code = StringField('Codigo de Area')
    phone = StringField('Telefono')

    submit = SubmitField('Submit')


class EditTutorBankDataForm(FlaskForm):
    cbu = StringField('CBU', validators=[DataRequired(), Length(min=22, max=22)])
    alias = StringField('Alias', validators=[DataRequired(), Length(max=140)])

    submit = SubmitField('Submit')

