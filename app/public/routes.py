from flask import render_template, url_for, redirect, request
from flask_login import current_user

from app.auth.forms import LoginForm, SignupForm
from app.auth.models import Profesor
from app.models import Materia, Facultad
from app.tutor.models import MateriaProfesor

from . import public_bp


# -------- Public Home ----------------------------------------------------------- #
@public_bp.route("/", methods=["GET", "POST"])
def home():
    if current_user.is_authenticated:
        if current_user.is_tutor:
            return redirect(url_for('tutor.home'))
        else:
            return redirect(url_for('student.home'))
    faculties = Facultad.get_all()
    login_form = LoginForm()
    return render_template("public/home.html", login_form=login_form, faculties=faculties)


# -------- Register Page ----------------------------------------------------------- #
@public_bp.route("/register/")
def register():
    if current_user.is_authenticated:
        if current_user.is_tutor:
            return redirect(url_for('tutor.home'))
        else:
            return redirect(url_for('student.home'))
    else:
        login_form = LoginForm()
        signup_form = SignupForm()
        return render_template("public/register.html", form=signup_form, login_form=login_form)


# -------- Login Page ----------------------------------------------------------- #
@public_bp.route('/login-page/')
def login():
    if current_user.is_authenticated:
        if current_user.is_tutor:
            return redirect(url_for('tutor.home'))
        else:
            return redirect(url_for('student.home'))
    else:
        login_form = LoginForm()
        return render_template("public/login.html", login_form=login_form)


# -------- About Us ----------------------------------------------------------- #
@public_bp.route("/quienes_somos")
def quienes_somos():
    return "Somos entienda y aprenda"


# -------- Tutor Public Page ----------------------------------------------------------- #
@public_bp.route('/tutor-view/<int:tutor_id>')
def tutor_view(tutor_id):
    default_filters = {
        "number_weeks": int(request.args.get('nweeks', "4")),
        "active_tab": request.args.get('tab', "horarios"),
    }
    tutor = Profesor.get_by_id(tutor_id)
    if tutor is None:
        redirect(url_for('public.home'))
    login_form = LoginForm()
    return render_template("public/tutor_view.html", tutor=tutor, login_form=login_form, default_filters=default_filters)


# -------- All Subjects Public Page ----------------------------------------------------------- #
@public_bp.route('/subjects')
def subjects():
    default_filters = {
        "subject": request.args.get('subject', ""),
        "faculty": int(request.args.get('faculty', "0"))
    }
    subjects = Materia.get_all()
    faculties = Facultad.get_all()
    login_form = LoginForm()
    return render_template(
        'public/subjects.html',
        subjects=subjects,
        faculties=faculties,
        login_form=login_form,
        default_filters=default_filters,
    )


# -------- All Tutors Public Page ----------------------------------------------------------- #
@public_bp.route('/tutors')
def tutors():
    def get_tutor_hours(x):
        return x.count_hours(status=0)

    tutors_list = Profesor.get_all()
    tutors_list = sorted(tutors_list, key=get_tutor_hours, reverse=True)
    login_form = LoginForm()
    return render_template(
        "public/tutors_list.html",
        tutors=tutors_list,
        login_form=login_form,
    )


# -------- Specific Subject Public Page ----------------------------------------------------------- #
@public_bp.route('/subject_view/<int:subject_id>')
def subject_info(subject_id):
    asc = request.args.get('asc', 'false')
    default_params = {
        "sortby": request.args.get('sortby', 'mean_score'),
        "asc": True if asc == "true" else False
    }
    tutor_subjects = MateriaProfesor.get_by_subject_id(subject_id)
    login_form = LoginForm()
    if len(tutor_subjects) == 0:
        subject = Materia.get_by_subject_id(subject_id)
        return render_template("public/empty_tutor_subject.html", subject=subject, login_form=login_form)
    return render_template(
        "public/subject_view.html",
        tutor_subjects=tutor_subjects,
        login_form=login_form,
        default_params=default_params
    )


# -------- Redirect page when trying to log class ----------------------------------------------------------- #
@public_bp.route('/student_account_creation')
def create_account():
    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template("public/create_account.html", form=signup_form, login_form=login_form)