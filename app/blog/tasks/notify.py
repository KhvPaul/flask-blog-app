import os
from datetime import datetime
from flask_mail import Message

from app.models import Blog, Comment
from db import db

from app import celery, mail

from flask import current_app, render_template

app = current_app

color = lambda x, y, z: ";".join([str(x), str(y), str(z)])

red = lambda x: '\x1b[%sm%s\x1b[0m' % (color(6, 31, 40), x)
green = lambda x: '\x1b[%sm%s\x1b[0m' % (color(6, 32, 40), x)
yellow = lambda x: '\x1b[%sm%s\x1b[0m' % (color(6, 33, 40), x)
blue = lambda x: '\x1b[%sm%s\x1b[0m' % (color(6, 34, 40), x)
purple = lambda x: '\x1b[%sm%s\x1b[0m' % (color(6, 35, 40), x)
cyan = lambda x: '\x1b[%sm%s\x1b[0m' % (color(6, 36, 40), x)

selected_color = lambda x, y: '\x1b[%sm%s\x1b[0m' % (y, x)

formatted_title = lambda x: f"\"{' '.join(x.split()[0:5])}...\""


def get_path():
    path = ''
    path += f'http://{os.getenv("HOST")}'
    path += (":" + os.getenv("PORT") + '/') if os.getenv("PORT") else '/'


def send_message(message_data):
    message = Message(subject=message_data['subject'],
                      recipients=message_data['recipients'],
                      html=message_data['html'],
                      sender=app.config['MAIL_DEFAULT_SENDER'], )
    print(green(' Sending message '))
    mail.send(message)
    print(cyan(' Message sent '))


@celery.task(name='flaskBlog.blog.notify_admin')
def notify_admin(message_data):
    send_message(message_data)
    return 'Success'


@celery.task(name='flaskBlog.blog.notify_blogger')
def notify_blogger():
    blogs = Blog.query.filter(Blog.notified == False)
    for blog in blogs:
        if blog.is_posted:
            message_data = {
                'subject': "FIY",
                'sender': app.config['MAIL_DEFAULT_SENDER'],
                'recipients': [blog.blogger.email],
                'html': render_template(
                    'mail/notify_blogger_blog.html',
                    blog=formatted_title(blog.title),
                    origin=f'{get_path()}blog/{blog.route}',
                    datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ),
            }
            send_message(message_data)
            blog.notified = True
            try:

                db.session.commit()
                message = selected_color(' ' + blog.blogger.username, color(4,32,40)) + green(' is notified ') + selected_color(formatted_title(blog.title) + ' ', color(4,32,40))
                print(message)
            except:
                message = red(' Error on blog notification (user:') + selected_color(blog.blogger.username, color(4,31,40)) + green(' (blog:') + selected_color(formatted_title(blog.title) + ' ', color(4,31,40))
                print(message)
    return 'Success'


@celery.task(name='flaskBlog.blog.comment_message')
def comment_message():
    comments = Comment.query.filter(Comment.notified == False)
    for comment in comments:
        if comment.blog is None:
            try:
                db.session.delete(comment)
                db.session.commit()
                print(green(f' Comment(id:{comment.id}) was successfully deleted '))
            except:
                print(red(f' Error on comment(id:{comment.id}) deletion '))
        roles = comment.blog.blogger.roles
        if comment.is_posted and not 'parser' in roles and not 'test_user':
            message_data = {
                'subject': "FIY",
                'sender': app.config['MAIL_DEFAULT_SENDER'],
                'recipients': [comment.blog.blogger.email],
                'html': render_template(
                    'mail/notify_blogger_comment.html',
                    blog=formatted_title(comment.blog.title),
                    origin=f'{get_path()}blog/{comment.blog.route}',
                    datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    comment=comment.content
                ),
            }
            send_message(message_data)
            comment.notified = True
            try:
                db.session.commit()
                message = green(' Comment(id:') + selected_color(comment.id, comment(4,32,40)) + green('): ') + selected_color(comment.blog.blogger.username, color(4,32,40)) + green(' is notified ')
                print(message)
            except:
                message = red(' Error on comment(id:') + selected_color(comment.id, color(4,31,40)) + red(') notification (user: ') + selected_color(comment.blog.blogger.username, color(4,31,40)) + red(')(blog: ') + selected_color(formatted_title(comment.blog.title), color(4,31,40)) + red(') ')
                print(message)
    return 'Success'
