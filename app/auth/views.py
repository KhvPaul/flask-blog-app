import base64
import io
import os

from flask_security.utils import hash_password
from werkzeug.utils import secure_filename

from . import auth_blueprint
from flask import request, flash, render_template, redirect, url_for, make_response, abort, send_file, current_app

from .forms import SignUpForm, SingInForm, BloggerForm, ChangePasswordCheckForm, ChangePasswordForm

from flask_security import current_user, login_required, logout_user, login_user, password_reset
from db import db
from app.models import Blogger, Blog, Role
from app import csrf
from ..utils.security import user_datastore


@auth_blueprint.route('/registration', methods=['post', 'get'])
@csrf.exempt
def registration():
    data = dict()
    form = SignUpForm()
    if request.method == "POST" and form.validate_on_submit():
        data['form_is_valid'] = True
        user_datastore.create_user(
            username=form.username.data,
            email=form.email.data,
            password=hash_password(form.password.data))
        try:
            db.session.commit()
            blogger = Blogger.query.filter(Blogger.username == form.username.data).first()
            login_user(blogger)
            data['html_navbar'] = render_template('navbar.html', current_user=current_user, home=True)
            flash('Successfully created new User', 'success')
            data['html_messages_block'] = render_template('flash_messages.html')
            return data
        except:
            data['form_is_valid'] = False
            data['html_form'] = render_template('auth/forms/registration_form.html', form=form)
            flash('Error on User registration', 'danger')
            data['html_messages_block'] = render_template('flash_messages.html')
            return data
    elif request.method == "POST":
        data['html_form'] = render_template('auth/forms/registration_form.html', form=form, validated=True)
        return data
    else:
        data['html_form'] = render_template('auth/forms/registration_form.html', form=form)
        return data

@auth_blueprint.route('/login', methods=['post', 'get'])
@csrf.exempt
def login():
    data = dict()
    form = SingInForm()
    if request.method == "POST" and form.validate_on_submit():
        data['form_is_valid'] = True
        blogger = Blogger.query.filter(Blogger.email == form.email.data).first()
        try:
            login_user(blogger, remember=form.remember.data)
            login_user(blogger)
            data['html_navbar'] = render_template('navbar.html', current_user=current_user, home=True)
            data['html_button_create_blog'] = render_template('blog/button_create_blog.html', current_user=current_user)
            flash('Successfully logged in', 'success')
            data['html_messages_block'] = render_template('flash_messages.html')
            return data
        except:
            data['form_is_valid'] = False
            data['html_form'] = render_template('auth/forms/login_form.html', form=form)
            flash('Error on User authentication', 'danger')
            data['html_messages_block'] = render_template('flash_messages.html')
            return data
    else:
        data['html_form'] = render_template('auth/forms/login_form.html', form=form)
        return data


@auth_blueprint.route('/logout')
@csrf.exempt
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", 'warning')
    return redirect(url_for('blog_bp.blog_list'), 302)


@auth_blueprint.route('/change_password_check', methods=['post', 'get'])
@csrf.exempt
@login_required
def change_password_check():
    data = dict()
    form = ChangePasswordCheckForm()
    if request.method == "POST" and form.validate_on_submit():
        form = ChangePasswordForm()
        data['html_form'] = render_template('auth/forms/change_password_form.html', form=form)
        return data
    else:
        data['html_form'] = render_template('auth/forms/change_password_check_form.html', form=form)
        return data


@auth_blueprint.route('/change_password', methods=['post', 'get'])
@csrf.exempt
@login_required
def change_password():
    data = dict()
    blogger = Blogger.query.get_or_404(current_user.id)
    form = ChangePasswordForm()

    if request.method == "POST" and form.validate():
        data['form_is_valid'] = True
        blogger.password = hash_password(form.password.data)
        try:
            db.session.commit()
            flash('Successfully updated password data', 'success')
            data['html_messages_block'] = render_template('flash_messages.html')
            return data
        except:
            data['form_is_valid'] = False
            flash('Error on password update', 'danger')
            data['html_messages_block'] = render_template('flash_messages.html')
            return data
    else:
        data['html_form'] = render_template('auth/forms/change_password_form.html', form=form)
        return data


@auth_blueprint.route('/blogger/')
@login_required
def authenticated_user_profile():
    page = request.args.get('page', 1, type=int)
    blogs = Blog.query.filter(
        Blog.blogger == current_user
    ).order_by(Blog.post_date.desc()).paginate(page=page, per_page=4)
    return render_template(
        'auth/current_user.html',
        blogger=current_user,
        blogs=blogs,
        url_injection='auth.authenticated_user_profile',
        user_page=True,
    )


@auth_blueprint.route('/blogger/<string:username>')
def blogger_profile(username):
    blogger = Blogger.query.filter(Blogger.username == username).first()
    if not blogger:
        abort(404)
    if 'is_staff' in blogger.roles:
        if blogger != current_user:
            abort(403)
        else:
            return redirect(url_for('auth.authenticated_user_profile'), 302)
    if current_user == blogger:
         return redirect(url_for('auth.authenticated_user_profile'), 302)
    else:
        page = request.args.get('page', 1, type=int)
        if 'parser' in blogger.roles:
            blogs = Blog.query.filter(Blog.blogger == blogger, Blog.is_posted == True).order_by(
                Blog.post_date.desc()).all()  # .paginate(page=page, per_page=10)
        else:
            blogs = Blog.query.filter(Blog.blogger == blogger, Blog.is_posted == True).order_by(
                Blog.post_date.desc()).all()  # .paginate(page=page, per_page=4)
        return render_template(
            'auth/profile.html',
            blogger=blogger,
            blogs=blogs,
            url_injection='auth.blogger_profile',
            user_page=True
            )


@auth_blueprint.route('/blogger/update', methods=['get', 'post'])
@csrf.exempt
@login_required
def update_blogger():
    data = dict()
    blogger = Blogger.query.get_or_404(current_user.id)
    form = BloggerForm(obj=blogger)

    if request.method == "POST" and form.validate():
        data['form_is_valid'] = True
        blogger.first_name = form.first_name.data
        blogger.last_name = form.last_name.data
        blogger.email = form.email.data
        blogger.phone = form.phone.data
        blogger.address = form.address.data
        blogger.bio = form.bio.data

        page = request.args.get('page', 1, type=int)
        blogs = Blog.query.filter(
            Blog.blogger == current_user
        ).order_by(Blog.post_date.desc()).paginate(page=page, per_page=4)

        try:
            db.session.commit()
            data['html_profile_content'] = render_template('auth/blocks/user_profile_content.html',
                                                           blogger=current_user, blogs=blogs,
                                                           url_injection='auth.authenticated_user_profile')
            flash('Successfully updated user data', 'success')
            data['html_messages_block'] = render_template('flash_messages.html')
            return data
        except:
            data['form_is_valid'] = False
            data['html_form'] = render_template('auth/forms/blogger_detail_form.html', form=form)
            flash('Error on User Creation', 'danger')
            data['html_messages_block'] = render_template('flash_messages.html')
            return data
    else:
        data['html_form'] = render_template('auth/forms/blogger_detail_form.html', form=form, blogger=blogger)
        return data


@auth_blueprint.route('/blogger/update_picture', methods=['get', 'post'])
@csrf.exempt
@login_required
def update_picture():
    data = dict()
    # blogger = Blogger.query.get_or_404(current_user.id)
    blogger = Blogger.query.filter(Blogger.id==current_user.id).first()
    if request.method == "POST":
        data['form_is_valid'] = True
        extension_allowed = False
        file = request.files['inputFile']
        if file.filename == '':
            flash('No selected file', 'warning')
            return redirect(url_for('auth.authenticated_user_profile'), 302)
        for extension in current_app.config.get('IMAGE_ALLOWED_EXTENSIONS'):
            if extension in file.mimetype:
                extension_allowed = True
        if not extension_allowed and not request.files['inputFile'].mimetype.startswith('image/'):
            flash('File extension not allowed', 'danger')
            return redirect(url_for('auth.authenticated_user_profile'), 302)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file:    # if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config.get('UPLOAD_FOLDER') + '/images/', filename))
            # previous_path = url_for('static', filename=blogger.file_path)
            blogger.file_path = 'uploads/images/' + filename
            # if os.path.exists(previous_path) and 'default' not in previous_path:
            #     print(previous_path)
            #     os.remove(previous_path)
            try:
                db.session.commit()
                flash('Picture Uploaded', 'success')
            except:
                flash('Picture ERROR', 'danger')
            return redirect(url_for('auth.authenticated_user_profile'), 302)
    else:
        data['html_form'] = render_template('auth/forms/picture_block_form.html', blogger=blogger, request=request)
        return data