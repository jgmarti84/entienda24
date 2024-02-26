from . import student_bp
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.auth.models import Profesor


@student_bp.route('/student/home/')
@login_required
def home():
    if current_user.is_authenticated:
        if not current_user.is_tutor:
            return render_template("student/home.html")
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
            return render_template("student/class_log.html", tutor=tutor, default_params=default_params)
        return render_template("public/create_account.html")
    return render_template("public/create_account.html")
