from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from urllib.parse import urlparse
from datetime import datetime, timezone
import json
from .utils import validate_email_syntax
import phonenumbers
import config
from app.tutor.models import HorarioProfesorDisponible, HorarioProfesorReservado, MateriaProfesor
from app.student.models import ClaseReservada
import app.utils.schedule as schedule
import app.utils.classes as classes

import os
from app import login_manager

from . import auth_bp
from .forms import SignupForm, LoginForm, ModifyPasswordForm, EditUserProfileForm, EditTutorBankDataForm
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
            # if not phonenumbers.is_possible_number(phonenumbers.parse(phone_nr)):
            #     error = f"El Número de teléfono {phone_nr} es inválido"
            #     return json.dumps({'status': 'Signup Error', 'error': error})

            # Comprobamos que no hay ya un usuario con ese telefono
            user = Usuario.get_by_phone(phone_nr)
            if user is not None:
                error = f"El Teléfono {phone_nr} ya está siendo utilizado por otra persona"
                return json.dumps({'status': 'Singup Error', 'error': error})

            user_data = {k: v for k, v in form.data.items() if k in Usuario.__table__.columns.keys()}
            user_data["phone"] = phone_nr
            user = Usuario(**user_data)
            user.set_password(password)
            user.created_at = datetime.now(timezone.utc)
            user.save()
            if user.is_tutor:
                tutor = Profesor(user.id)
                tutor.save()
            else:
                student = Estudiante(user.id)
                student.save()
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
                return jsonify({"status": "Validate Error", "error": "Error al validar estudiantes!"})
            students.append(current_user.user)
            return jsonify({"status": "Validate Successful", "students": [{k: v for k, v in s.__dict__.items() if k != "_sa_instance_state"} for s in students]}), 200
        except Exception as e:
            return jsonify({"status": "Validate Error", "error": str(e)})


@auth_bp.route('/validate_class_log/<int:tutor_id>', methods=["POST"])
def is_valid_tutor_log_schedule(tutor_id):
    if request.method == "POST":
        data = request.get_json()
        hours = float(data["hours"])
        class_type = data["class_type"]
        slots = data["slots"]
        if len(slots) != hours * 2:
            return json.dumps({"status": "Validate Error", "error": f"La cantidad de Horas no coincide con los horarios seleccionados."})
        for slot in slots:
            matching_slot = HorarioProfesorDisponible.get_tutor_slots_by_isodate(tutor_id, *slot[:4])
            if not len(matching_slot) == 1:
                return json.dumps({"status": "Validate Error", "error": f"Error en el horario del {slot[4]} a las {schedule.time_slot_from_time_index(slot[3])}"})
            if matching_slot[0].availability_type not in classes.map_class_type(class_type):
                return json.dumps({"status": "Validate Error", "error": f"El horario del {slot[4]} a las {schedule.time_slot_from_time_index(slot[3])} no corresponde con el tipo seleccionado."})
        try:
            return json.dumps({"status": "Validate Successful"})
        except Exception as e:
            return json.dumps({"status": "Validate Error", "error": str(e)})


@auth_bp.route("/class_log_save", methods=["POST"])
def class_log_save():
    if request.method == "POST":
        data = request.get_json()
        try:
            subject_id = int(data["subject_id"])
            tutor_id = int(data["tutor_id"])
            logger = data["students"].pop(-1)
            student_id = logger["id"]
            class_type = data["class_type"]
            class_ids = []
            for k, v in data["schedule_data"].items():
                class_to_log = ClaseReservada(tutor_id=tutor_id, subject_id=subject_id, student_id=student_id, status=2, class_type=class_type, other_students=[s["id"] for s in data["students"]])
                class_to_log.save()
                for schedule_slot in v:
                    kwargs = dict(enrolled_type=2, enrolled_class_id=class_to_log.id, **schedule_slot)
                    enrolled_slot = HorarioProfesorReservado(tutor_id=tutor_id, **kwargs)
                    enrolled_slot.save()
                class_ids.append(class_to_log.id)
            return jsonify({"status": "Logging Successful", "logged_classes": class_ids}), 200
        except Exception as e:
            return jsonify({'status': 'Logging Error', 'error': str(e)}), 500


@auth_bp.route('/class_log_remove', methods=["POST"])
def class_log_remove():
    if request.method == "POST":
        data = request.get_json()
        try:
            for logged_class_id in data:
                logged_class = ClaseReservada.get_by_id(logged_class_id)
                logged_class.remove()
            return jsonify({"status": "Remove Successful"}), 200
        except Exception as e:
            return jsonify({"status": "Remove Error", "error": str(e)}), 500


@auth_bp.route('/class_log_confirm', methods=["POST"])
def class_log_confirm():
    if request.method == "POST":
        class_ids = json.loads(request.form["loggedIds"])
        file = request.files.get('file')
        if not file:
            return jsonify({'status': 'Confirm Error', 'error': "Tiene que incluir el comprobante de transferencia"})
        try:
            for class_id in class_ids:
                slot_ids = [s.id for s in HorarioProfesorReservado.get_by_class_id(class_id)]

                for slot_id in slot_ids:
                    slot = HorarioProfesorReservado.get_by_id(slot_id)
                    slot.enrolled_type = 1
                    slot.save()

                cls = ClaseReservada.get_by_id(class_id)
                cls.status = 1
                cls.save()

            path = f"{config.UPLOADS_DIRECTORY}/payment_checks/{class_ids}"
            if not os.path.exists(path):
                os.makedirs(path)
            file.save(f"{path}/{file.filename}")  # Save the file to a folder (create the 'uploads' folder)
            return jsonify({'status': 'Confirm Successful'}), 200
        except Exception as e:
            return jsonify({'status': 'Confirm Error', 'error': str(e)}), 500


@auth_bp.route('/class_log_re_schedule/<int:class_id>', methods=["POST"])
def class_log_re_schedule(class_id):
    data = request.get_json()
    if request.method == "POST":
        cls = ClaseReservada.get_by_id(class_id)
        tutor_id = cls.tutor_id
        subject_id = cls.subject_id
        student_id = cls.student_id
        class_type = cls.class_type
        other_students = cls.other_students
        cls.remove()
        try:
            class_ids = []
            for k, v in data["schedule_data"].items():
                class_to_log = ClaseReservada(tutor_id=tutor_id, subject_id=subject_id, student_id=student_id, status=1, class_type=class_type, other_students=other_students)
                class_to_log.save()
                for schedule_slot in v:
                    kwargs = dict(enrolled_type=1, enrolled_class_id=class_to_log.id, **schedule_slot)
                    enrolled_slot = HorarioProfesorReservado(tutor_id=tutor_id, **kwargs)
                    enrolled_slot.save()
                class_ids.append(class_to_log.id)
            return jsonify({"status": "Re-schedule Successful"}), 200
        except Exception as e:
            return jsonify({'status': 'Re-schedule Error', 'error': str(e)}), 500


@auth_bp.route('/save_class_score/<int:class_id>', methods=["POST"])
@login_required
def save_class_score(class_id):
    if current_user.is_authenticated:
        if not current_user.is_tutor:
            if request.method == "POST":
                data = request.get_json()
                try:
                    cls = ClaseReservada.get_by_id(class_id)
                    cls.update(score=data["score"])
                    return jsonify({"status": "Save Successful"}), 200
                except Exception as e:
                    return jsonify({"status": "Save Error", "error": f"Error al guardar la calificacion: {e}"}), 500


@auth_bp.route('/update_user_data', methods=["POST"])
@login_required
def update_user_data():
    if current_user.is_authenticated:
        if request.method == "POST":

            error = None
            form = EditUserProfileForm(request.form)
            username = form.data["username"]
            email = form.data["email"]
            user_id = current_user.user.id

            # Comprobamos que no hay ya un usuario con ese nombre de usuario
            user = Usuario.get_by_username(username)
            if user is not None:
                if user.id != user_id:
                    error = f"El usuario {username} ya está siendo utilizado por otra persona"
                    return json.dumps({'status': 'Validate Error', 'error': error})

            # Comprobamos que no hay ya un usuario con ese email
            user = Usuario.get_by_email(email)
            if user is not None:
                if user.id != user_id:
                    error = f"El email {email} ya está siendo utilizado por otra persona"
                    return json.dumps({'status': 'Validate Error', 'error': error})

            phone_nr = f"+{form.phone_country_code.data}{form.phone_city_code.data}{form.phone.data}"
            # if not phonenumbers.is_possible_number(phonenumbers.parse(phone_nr)):
            #     error = f"El Número de teléfono {phone_nr} es inválido"
            #     return json.dumps({'status': 'Validate Error', 'error': error})

            # Comprobamos que no hay ya un usuario con ese telefono
            user = Usuario.get_by_phone(phone_nr)
            if user is not None:
                if user.id != user_id:
                    error = f"El Teléfono {phone_nr} ya está siendo utilizado por otra persona"
                    return json.dumps({'status': 'Validate Error', 'error': error})

            logout_user()
            user = Usuario.get_by_id(user_id)
            user.update(
                **dict(
                    username=username,
                    name=form.name.data,
                    last_name=form.last_name.data,
                    email=email,
                    phone=phone_nr
                )
            )
            login_user(user, remember=True)
            return json.dumps({'status': 'Validate Successful'})
    return redirect("public.create_account")


@auth_bp.route('/change_password', methods=["POST"])
@login_required
def change_password():
    if request.method == "POST":
        form = ModifyPasswordForm(request.form)
        if form.validate():
            old_password = form.old_password.data
            # check valid password
            if current_user.user.check_password(old_password):
                new_password = form.new_password.data
                user_id = current_user.user.id
                logout_user()
                user = Usuario.get_by_id(user_id)
                user.set_password(new_password)
                user.update()
                login_user(user, remember=True)
                return json.dumps({"status": "Modify Successful"})
            error = "La contraseña anterior no coincide"
            return json.dumps({'status': 'Modify Error', 'error': error})
        error = "Alguno de los campos requeridos está vacío"
        return json.dumps({'status': 'Modify Error', 'error': error})


@auth_bp.route('/upload_picture', methods=["POST"])
@login_required
def upload_picture():
    if request.method == "POST":
        file = request.files['file']
        try:
            user_id = current_user.user.id
            path = f"{config.UPLOADS_DIRECTORY}/profile_picture/{user_id}"
            if not os.path.exists(path):
                os.makedirs(path)
            file.save(f"{path}/profile_picture")  # Save the file to a folder (create the 'uploads' folder)
            return jsonify({'status': 'Upload Successful'}), 200
        except Exception as e:
            return jsonify({'status': 'Upload Error', 'error': str(e)}), 500


@auth_bp.route('/validate_bank_details', methods=["POST"])
@login_required
def validate_bank_details():
    if current_user.is_tutor:
        if request.method == "POST":
            form = EditTutorBankDataForm(request.form)
            if not form.validate():
                if len(form.cbu.data) != 22:
                    return json.dumps({"status": "Validate Error", "error": "La longitud del CBU/CVU debe ser exactamente de 22 digitos."})
                if not form.cbu.data.isdigit():
                    return json.dumps({"status": "Validate Error", "error": "El CBU solo puede tener numeros."})
                return json.dumps({"status": "Validate Error", "error": "Ambos campos deben ser completados (CBU/CVU y alias)"})

            kwargs = {"bank_cbu": form.cbu.data, "bank_alias": form.alias.data}
            current_user.update(**kwargs)
            return json.dumps({"status": "Validate Successful"})


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
