from . import student_bp
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user, logout_user, login_user
from app.auth.models import Usuario, Profesor
from app.student.models import ClaseReservada
from app.auth.forms import EditUserProfileForm, ModifyPasswordForm
import phonenumbers
import json
import os


@student_bp.route('/student/home/')
@login_required
def home():
    if current_user.is_authenticated:
        if not current_user.is_tutor:
            # removemos las clases que quedron temporalmente reservadas por alguna razon que no tengo claro.
            classes = ClaseReservada.query.filter_by(status=2).filter_by(student_id=current_user.user.id).all()
            for cls in classes:
                cls.remove()

            # buscamos todas las clases
            student_logged_classes = ClaseReservada.get_by_student_id(current_user.user.id)

            form = EditUserProfileForm()
            user_phone = phonenumbers.parse(current_user.user.phone)
            pcode = user_phone.country_code
            form.phone_country_code.default = pcode
            form.process()
            pext = "" if not user_phone.extension else user_phone.extension
            pnat = "" if not user_phone.national_number else user_phone.national_number
            user_phone = [pcode, pext, pnat]

            pass_form = ModifyPasswordForm()
            return render_template(
                "student/home.html",
                form=form,
                pass_form=pass_form,
                phones=user_phone,
                classes=student_logged_classes
            )
        return redirect(url_for('tutor.home'))
    return redirect(url_for('public.login'))


@student_bp.route('/class-log/<int:tutor_id>')
@login_required
def class_log(tutor_id):
    default_params = {
        "number_weeks": int(request.args.get('nweeks', "4")),
    }
    if current_user.is_authenticated:
        if not current_user.is_tutor:
            tutor = Profesor.get_by_id(tutor_id)
            return render_template(
                "student/class_log.html",
                tutor=tutor,
                default_params=default_params,

            )
        return redirect("public.create_account")
    return redirect("public.create_account")
