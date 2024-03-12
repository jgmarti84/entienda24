from . import student_bp
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.auth.models import Profesor
from app.student.models import ClaseReservada
from app.auth.forms import EditUserProfileForm, ModifyPasswordForm
import phonenumbers


@student_bp.route('/student/home/')
@login_required
def home():
    if current_user.is_authenticated:
        default_params = {
            "active_tab": request.args.get('tab', "perfil")
        }
        if not current_user.is_tutor:
            # removemos las clases que quedron temporalmente reservadas por alguna razon que no tengo claro.
            classes = ClaseReservada.query.filter_by(status=2).filter_by(student_id=current_user.user.id).all()
            for cls in classes:
                cls.remove()

            # buscamos todas las clases
            student_logged_classes = ClaseReservada.get_by_student_id(current_user.user.id)
            student_logged_classes.extend(ClaseReservada.query.filter(ClaseReservada.other_students.contains([current_user.user.id])).all())
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
                default_params=default_params,
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


@student_bp.route('/get_class_data/<int:class_id>', methods=["GET"])
@login_required
def get_class_data(class_id):
    if request.method == "GET":
        cls = ClaseReservada.get_by_id(class_id)
        class_info = {
            "class": cls.as_dict(),
            "student": cls.student.user.as_dict(),
            "tutor": cls.tutor.user.as_dict(),
            "subject": cls.subject.as_dict(),
            "enrolled_schedule": [dict(**ce.as_dict(), **{"date": ce.date(), "start_time": ce.start_time(), "end_time": ce.end_time()}) for ce in cls.enrolled_schedule]
        }
        return jsonify({"status": "Get Successful", "class_info": class_info})
