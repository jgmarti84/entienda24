from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user
from urllib.parse import urlparse
import json
from .utils import validate_email_syntax
import phonenumbers

from app import login_manager
from . import auth_bp
from .forms import SignupForm, LoginForm
from .models import Usuario, Profesor, Estudiante


# -------- Signup ---------------------------------------------------------- #
@auth_bp.route('/signup/', methods=['POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    if request.method == "POST":
        form = SignupForm(request.form)
        error = None
        if form.validate():
            password = form.password.data
            username = form.username.data
            email = form.email.data

            # Comprobamos que no hay ya un usuario con ese nombre de usuario
            user = Usuario.get_by_username(username)
            if user is not None:
                error = f"El usuario {username} ya está siendo utilizado por otra persona"
                return json.dumps({'status': 'Signup Error', 'error': error})

            # Comprobamos que no hay ya un usuario con ese email
            user = Usuario.get_by_email(email)
            if user is not None:
                error = f"El email {email} ya está siendo utilizado por otra persona"
                return json.dumps({'status': 'Singup Error', 'error': error})

            phone_nr = f"+{form.phone_country_code.data}{form.phone_city_code.data}{form.phone.data}"
            if not phonenumbers.is_possible_number(phonenumbers.parse(phone_nr)):
                error = f"El Número de teléfono {phone_nr} es inválido"
                return json.dumps({'status': 'Signup Error', 'error': error})

            # Comprobamos que no hay ya un usuario con ese telefono
            user = Usuario.get_by_phone(phone_nr)
            if user is not None:
                error = f"El Teléfono {phone_nr} ya está siendo utilizado por otra persona"
                return json.dumps({'status': 'Singup Error', 'error': error})

            user_data = {k: v for k, v in form.data.items() if k in Usuario.__table__.columns.keys()}
            user_data["phone"] = phone_nr
            user = Usuario(**user_data)
            user.set_password(password)
            user.save()
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('public.home')
            return json.dumps({'status': 'Signup Successful', 'next_page': next_page})

        error = "Alguno de los campos requeridos está vacío"
        return json.dumps({'status': 'Signup Error', 'error': error})


# -------- Login ----------------------------------------------------------- #
@auth_bp.route('/login/', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))

    if request.method == "POST":
        form = LoginForm(request.form)
        if form.validate():
            username_email = form.username_email.data
            user = Usuario.get_by_username(username_email)
            field_type = "usuario"
            if validate_email_syntax(username_email):
                user = Usuario.get_by_email(username_email)
                field_type = "email"

            if user is not None:
                if user.check_password(form.password.data):
                    login_user(user, remember=form.remember_me.data)
                    next_page = request.args.get('next', None)
                    if not next_page or urlparse(next_page).netloc != '':
                        next_page = url_for('public.home')
                    return json.dumps({'status': 'Login Successful', 'next_page': next_page})
                return json.dumps({'status': 'Login Error', 'errors': ['La contraseña coincide']})
            return json.dumps({'status': 'Login Error', 'errors': [f'El {field_type} {form.username_email.data} no existe']})
        return json.dumps({'status': 'Login Error', 'errors': ['Algún campo requerido está vacío']})
    return redirect(url_for('public.home'))


@auth_bp.route('/validate_students/', methods=["POST"])
def is_valid_student_username():
    if request.method == "POST":
        student_usernames_list = request.get_json()
        try:
            students = [Estudiante.get_by_username(username) for username in student_usernames_list]
            valid = all(students)
            if not valid:
                return json.dumps({"status": "Validate Error", "error": "Error al validar estudiantes!"})
            return json.dumps({"status": "Validate Successful", "students": [{k: v for k, v in s.__dict__.items() if k!="_sa_instance_state"} for s in students]})
        except Exception as e:
            return json.dumps({"status": "Validate Error", "error": str(e)})


@auth_bp.route('/validate_class_log/<int:tutor_id>')
def is_valid_tutor_log_schedule(tutor_id):
    return None


# -------- Logout ----------------------------------------------------------- #
@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.home'))


@auth_bp.route('/create_account')
def create_account():
    return render_template('public/create_account.html')


@login_manager.user_loader
def load_user(user_id):
    user = Usuario.get_by_id(int(user_id))
    if user.is_tutor:
        return Profesor.get_by_id(user.id)
    else:
        return Estudiante.get_by_id(user.id)
