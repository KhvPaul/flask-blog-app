from . import blog_blueprint
from flask import render_template, request, flash, abort, redirect, url_for, current_app
from flask_security import current_user, login_required

from db import db
from .forms import BlogForm, CommentForm, ContactUsForm
from .tasks.notify import notify_admin
from datetime import datetime
from app import csrf, cache
from app.models import Blog, Comment

###################
from celery.utils.log import get_logger

logger = get_logger(__name__)
###################

app = current_app


@blog_blueprint.route('/')
# @cache.cached(timeout=10)
def blog_list():
    carved_blogs = []
    blogs = Blog.query.filter(Blog.is_posted == True).order_by(Blog.post_date.desc())
    if blogs.count() > 6:
        for i in range(3):
            carved_blogs.append(blogs[i])
        page = request.args.get('page', 1, type=int)
        blogs = Blog.query.filter(
            Blog.id != carved_blogs[0].id,
            Blog.id != carved_blogs[1].id,
            Blog.id != carved_blogs[2].id,
            Blog.is_posted == True
        ).order_by(Blog.post_date.desc()).paginate(page=page, per_page=4)
    return render_template('blog/blog_list.html', blogs=blogs, carved_blogs=carved_blogs, home=True)


@blog_blueprint.route('/<string:blog_route>')
def show_blog(blog_route):  # put application's code here
    blog = Blog.query.filter(Blog.route == blog_route).first()
    if not blog:
        abort(404)
    if not blog.is_posted and blog.blogger != current_user:
        abort(403)
    return render_template('blog/blog_detail.html', blog=blog, home=True)


@blog_blueprint.route('/create', methods=['get', 'post'])
@csrf.exempt
@login_required
def create_blog():
    data = dict()
    form = BlogForm()
    if request.method == "POST":
        data['form_is_valid'] = True
        blog = Blog(
            title=form.title.data,
            content=form.content.data,
            publication_request=form.publication_request.data,
            blogger_id=current_user.id)
        blog.create_update_route(blogger=current_user, title=form.title.data)
        try:
            db.session.add(blog)
            db.session.commit()
            if blog.publication_request:
                pass
                # IF CELErY ACTIVE
                # message_data = {'subject': 'FIY',
                #                 'recipients': [app.config['MAIL_DEFAULT_SENDER']],
                #                 'html': render_template('mail/notify_admin.html',
                #                                         blog=blog,
                #                                         action='added',
                #                                         datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                #                                         )
                #                 }
                #
                # notify_admin.apply_async(args=[message_data])
            flash('Successfully created new Blog', 'success')
            if request.args.get('next'):
                return redirect(url_for('blog_bp.show_blog', blog_route=blog.route, home=True), 302)
            page = request.args.get('page', 1, type=int)
            blogs = Blog.query.filter(Blog.blogger == current_user).order_by(
                Blog.post_date.desc()).paginate(page=page, per_page=4)
            data['html_blogger_blog_list'] = render_template('blogger_blog_list.html',
                                                             blogger=current_user, blogs=blogs,
                                                             url_injection='auth.authenticated_user_profile')

            data['html_messages_block'] = render_template('flash_messages.html')
            return data
        except:
            data['form_is_valid'] = False
            flash('Error on Blog creation', 'error')
            data['html_messages_block'] = render_template('flash_messages.html')
            return data
    else:
        if request.args.get('next'):
            data['html_form'] = render_template('blog/blog_form.html', form=form, next=True, request=request)
        else:
            page = request.args.get('page', 1, type=int)
            data['html_form'] = render_template('blog/blog_form.html', form=form, page=page, request=request)
        return data


@blog_blueprint.route('/<string:blog_route>/update', methods=['get', 'post'])
@csrf.exempt
@login_required
def update_blog(blog_route):
    blog = Blog.query.filter(Blog.route == blog_route).first()
    previous_title = blog.title
    if not blog:
        abort(404)
    if blog.blogger != current_user:
        abort(403)
    data = dict()
    form = BlogForm(obj=blog)
    if request.method == "POST":
        data['form_is_valid'] = True
        print(app.config['MAIL_DEFAULT_SENDER'])
        blog.title = form.title.data
        blog.content = form.content.data
        blog.publication_request = form.publication_request.data
        if previous_title != form.title.data:
            blog.create_update_route(blogger=current_user, title=form.title.data)
        blog.is_posted = False
        blog.notified = False
        try:
            db.session.commit()
            flash(f'Successfully updated blog {blog}', 'success')
            page = request.args.get('page', request.args.get('page'), type=int)
            blogs = Blog.query.filter(Blog.blogger == current_user).order_by(
                Blog.post_date.desc()).paginate(page=page, per_page=4)

            data['html_blog_detail'] = render_template('blog/blog_detail_content.html', blog=blog)
            data['html_blogger_blog_list'] = render_template('blogger_blog_list.html',
                                                             blogger=current_user, blogs=blogs,
                                                             url_injection='auth.authenticated_user_profile')
            data['html_messages_block'] = render_template('flash_messages.html')

            # IF CELErY ACTIVE
            # if blog.publication_request:
            #     message_data = {'subject': 'FIY',
            #                     'sender': app.config['MAIL_DEFAULT_SENDER'],
            #                     'recipients': [app.config['MAIL_DEFAULT_SENDER']],
            #                     'html': render_template('mail/notify_admin.html',
            #                                             blog=blog,
            #                                             action='updated',
            #                                             datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #                                             )
            #                     }
            #
            #     notify_admin.apply_async(args=[message_data])
            return data
        except:
            data['form_is_valid'] = False
            flash('Error on Blog update', 'danger')
            data['html_messages_block'] = render_template('flash_messages.html')
            return data
    else:
        data['html_form'] = render_template('blog/blog_update_form.html', blog=blog, form=form, request=request,
                                            page=request.args.get('page'))
        return data


@blog_blueprint.route('/<string:blog_route>/delete', methods=['get', 'post'])
@csrf.exempt
@login_required
def delete_blog(blog_route):  # put application's code here
    data = dict()
    blog = Blog.query.filter(Blog.route == blog_route).first()
    print(blog)
    if not blog:
        abort(404)
    if blog.blogger != current_user:
        abort(403)
        print('HERE3')
    if request.method == 'POST':
        data['form_is_valid'] = True
        print('HERE1')
        try:
            print('try')
            db.session.delete(blog)
            db.session.commit()
            flash('Successfully deleted blog', 'info')
            print('here2')
            if request.args.get('page'):
                data['html_messages_block'] = render_template('flash_messages.html')
                page = request.args.get('page', 1, type=int)
                print('here4')
                if page > ((Blog.query.filter(Blog.blogger == current_user).count() // 5) + 1):
                    page -= 1
                blogs = Blog.query.filter(Blog.blogger == current_user).order_by(
                    Blog.post_date.desc()).paginate(page=page, per_page=5)
                print('here3')
                data['html_blogger_blog_list'] = render_template('blogger_blog_list.html',
                                                                 blogger=current_user, blogs=blogs,
                                                                 url_injection='auth.authenticated_user_profile')
                print('HERE3')
                return data
            return redirect(url_for('blog_bp.blog_list'), 302)
        except:
            flash('Error on blog deletion', 'error')
            data['html_messages_block'] = render_template('flash_messages.html')
            return data
    else:
        page = request.args.get('page') if request.args.get('page') else None
        data['html_form'] = render_template('blog/blog_delete.html', page=page, blog=blog)
        return data


@blog_blueprint.route('/<string:blog_route>/create_comment', methods=['get', 'post'])
@csrf.exempt
def create_comment(blog_route):  # put application's code here
    data = dict()
    blog = Blog.query.filter(Blog.route == blog_route).first()
    if not blog:
        abort(404)
    form = CommentForm()
    if request.method == 'POST':
        data['form_is_valid'] = True
        comment = Comment(
            author=form.author.data,
            content=form.content.data,
            blog_id=blog.id
        )
        try:
            db.session.add(comment)
            db.session.commit()
            flash('Successfully created comment', 'success')
            data['html_messages_block'] = render_template('flash_messages.html')
        except:
            flash('Error on comment creation', 'error')
            data['html_messages_block'] = render_template('flash_messages.html')

        # IF CELErY ACTIVE
        # message_data = {'subject': 'FIY',
        #                 'sender': app.config['MAIL_DEFAULT_SENDER'],
        #                 'recipients': [app.config['MAIL_DEFAULT_SENDER']],
        #                 'html': render_template('mail/notify_admin.html',
        #                                         comment=comment,
        #                                         action='added',
        #                                         datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                                         )
        #                 }
        # notify_admin.apply_async(args=[message_data])
        return data
    else:
        data['html_form'] = render_template('blog/comment_form.html', form=form, blog=blog)
        return data


@blog_blueprint.route('/contact_us', methods=['get', 'post'])
@csrf.exempt
def contact_us():
    data = dict()
    if not current_user.is_anonymous:
        form = ContactUsForm(email=current_user.email)
    else:
        form = ContactUsForm()
    if request.method == 'POST':
        data['form_is_valid'] = True

        # IF CELErY ACTIVE
        # message_data = {'subject': 'FIY',
        #                 'sender': app.config['MAIL_DEFAULT_SENDER'],
        #                 'recipients': [app.config['MAIL_DEFAULT_SENDER']],
        #                 'html': render_template('mail/contact_us.html',
        #                                         email=form.email.data,
        #                                         content=form.content.data,
        #                                         datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                                         )
        #                 }
        #
        # notify_admin.apply_async(args=[message_data])

        flash('Message send', 'success')
        data['html_messages_block'] = render_template('flash_messages.html')
        return data
    else:
        data['html_form'] = render_template('blog/contact_us_form.html', form=form)
        return data
