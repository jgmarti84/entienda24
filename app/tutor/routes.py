from . import tutor_bp
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
import json
from urllib.parse import urlparse
from app.models import Materia
from app.student.models import ClaseReservada
from app.tutor.models import MateriaProfesor, HorarioProfesorDisponible
from app.auth.models import Estudiante, Profesor
import app.utils.schedule as schedule
import numpy as np
from psycopg2.extensions import register_adapter, AsIs
from app.auth.forms import ModifyPasswordForm, EditUserProfileForm, EditTutorBankDataForm
import phonenumbers
register_adapter(np.int64, AsIs)


@tutor_bp.route('/tutor/home/')
@login_required
def home():
    default_params = {
        "number_weeks": int(request.args.get('nweeks', "4")),
        "active_tab": request.args.get('tab', "horarios")
    }
    if current_user.is_authenticated:
        if current_user.is_tutor:
            # Update classes so those that are older than today will have a status of finished
            ClaseReservada.update_classes_status(tutor_id=current_user.user.id)
            # get all the classes from the tutor
            tutor_logged_classes = ClaseReservada.get_by_tutor_id(current_user.user.id)
            other_student_dict = {}
            for cls in tutor_logged_classes:
                for student_id in cls.other_students:
                    student = other_student_dict.get(student_id)
                    if not student:
                        other_student_dict[student_id] = Estudiante.get_by_id(student_id)

            form = EditUserProfileForm()
            user_phone = phonenumbers.parse(current_user.user.phone)
            pcode = user_phone.country_code
            form.phone_country_code.default = pcode
            form.process()
            pext = "" if not user_phone.extension else user_phone.extension
            pnat = "" if not user_phone.national_number else user_phone.national_number
            user_phone = [pcode, pext, pnat]

            pass_form = ModifyPasswordForm()
            bank_form = EditTutorBankDataForm()
            return render_template(
                "tutor/home.html",
                default_params=default_params,
                form=form,
                pass_form=pass_form,
                phones=user_phone,
                bank_form=bank_form,
                classes=tutor_logged_classes,
                other_student_dict=other_student_dict
            )

    return redirect(url_for('public.login'))


@tutor_bp.route('/tutor/edit-schedule/')
@login_required
def edit_schedule():
    default_params = {
        "number_weeks": int(request.args.get('nweeks', "4")),
    }
    if current_user.is_authenticated:
        if current_user.is_tutor:
            return render_template("tutor/edit_schedule.html", default_params=default_params)
        return redirect(url_for('student.home'))
    return redirect(url_for('public.login'))


@tutor_bp.route('/tutor/edit-classes/')
@login_required
def edit_classes():
    if current_user.is_authenticated:
        if current_user.is_tutor:
            subjects = Materia.get_all()
            return render_template("tutor/edit_classes.html", subjects=subjects)
        return redirect(url_for('student.home'))
    return redirect(url_for('public.login'))


@tutor_bp.route('/save_tutor_sutbjects/', methods=["POST"])
@login_required
def save_tutor_subjects():
    if current_user.is_authenticated:
        if current_user.is_tutor:
            tutor = current_user
            if request.method == "POST":
                if not current_user.bank_cbu:
                    return json.dumps({"status": "Save Error",
                                       "error": "Antes de poder guardar materias para dar debe registrar un CBU y Alias"})
                if not current_user.bank_alias:
                    return json.dumps({"status": "Save Error",
                                       "error": "Antes de poder guardar materias para dar debe registrar un CBU y Alias"})
                data = request.get_json()
                # validate data
                for subject_data in data["tutor_subjects_array"]:
                    if subject_data[4] == "0" or subject_data[4] == 0:
                        return json.dumps({"status": "Save Error", "error": f"Por favor ponga un precio de referencia para la materia {subject_data[2]}."})
                try:
                    MateriaProfesor.remove_by_tutor(tutor.id)
                    for subject_data in data["tutor_subjects_array"]:
                        tutor_subject = MateriaProfesor(tutor_id=tutor.id, subject_id=int(subject_data[1]), price_ref=float(subject_data[4]), comment=subject_data[5])
                        tutor_subject.save()
                    next_page = request.args.get('next', None)
                    if not next_page or urlparse(next_page).netloc != '':
                        next_page = url_for('tutor.home') + '?tab=materias'
                    return json.dumps({"status": "Save Successful", "next_page": next_page})
                except Exception as e:
                    return json.dumps({"status": "Save Error", "error": "Ocurrió un error al guardar las materias!"})
        return redirect(url_for('student.home'))
    return redirect(url_for('public.login'))


@tutor_bp.route('/save_tutor_schedule/', methods=["POST"])
@login_required
def save_tutor_schedule():
    if current_user.is_authenticated:
        if current_user.is_tutor:
            tutor = current_user
            if request.method == "POST":
                if not current_user.bank_cbu:
                    return json.dumps({"status": "Save Error",
                                       "error": "Antes de poder guardar materias para dar debe registrar un CBU y Alias"})
                if not current_user.bank_alias:
                    return json.dumps({"status": "Save Error",
                                       "error": "Antes de poder guardar materias para dar debe registrar un CBU y Alias"})
                data = request.get_json()
                modified_schedule = schedule.transform_view_schedule_db_format(data["data"])
                db_schedule = tutor.get_availability_df()
                merged_df = modified_schedule.merge(
                    db_schedule,
                    on=["tutor_id", "year_index", "week_index", "day_index", "time_index"],
                    how="left"
                ).dropna(subset=["availability_type_x", "availability_type_y"], how="all")
                merged_df = merged_df[merged_df["availability_type_x"] != merged_df["availability_type_y"]].drop(
                    ["availability_type_y", "id"], axis=1).rename(
                    columns={"availability_type_x": "availability_type"}).fillna("")
                merged_df["availability_type"] = merged_df["availability_type"].replace("", 0).astype(int)
                if merged_df.empty:
                    return json.dumps({"status": "Save Error", "error": "No se seleccionaron horarios para modificar"})
                try:
                    for i, row in merged_df.iterrows():
                        schedule_slot = HorarioProfesorDisponible(**row)
                        schedule_slot.upsert()
                    next_page = request.args.get('next', None)
                    if not next_page or urlparse(next_page).netloc != '':
                        next_page = url_for('tutor.home') + '?tab=horarios'
                    return json.dumps({"status": "Save Successful", "next_page": next_page})
                except:
                    return json.dumps({"status": "Save Error", "error": "Ocurrió un error al guardar los horarios!"})
        return redirect(url_for('student.home'))
    return redirect(url_for('public.login'))


@tutor_bp.route('/cancel_logged_class/<int:class_id>', methods=["POST"])
@login_required
def cancel_logged_class(class_id):
    if current_user.is_authenticated:
        if current_user.is_tutor:
            if request.method == "POST":
                try:
                    cls = ClaseReservada.get_by_id(class_id)
                    cls.update(**dict(status=3))
                    return jsonify({"status": "Cancel Successful", "message": "La Clase se ha cancelado correctamente"}), 200
                except Exception as e:
                    return jsonify({"status": "Cancel Error", "error": str(e)}), 500
        return redirect(url_for('student.home'))
    return redirect(url_for('public.login'))


@tutor_bp.route('/get_tutor_schedule/<int:tutor_id>', defaults={"nweeks": 4}, methods=["GET"])
@tutor_bp.route('/get_tutor_schedule/<int:tutor_id>/<int:nweeks>', methods=["GET"])
@login_required
def get_tutor_schedule(tutor_id, nweeks):
    if request.method == "GET":
        tutor = Profesor.get_by_id(tutor_id)
        return jsonify({"tutor_schedule": tutor.get_weeks_schedule(nweeks).to_dict(orient="records")}), 200
