from . import tutor_bp
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
import json
from urllib.parse import urlparse
from app.models import Materia
from app.tutor.models import MateriaProfesor, HorarioProfesorDisponible
import app.utils.schedule as schedule
import numpy as np
from psycopg2.extensions import register_adapter, AsIs
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
            current_user.get_weeks_schedule(4)
            return render_template("tutor/home.html", default_params=default_params)
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