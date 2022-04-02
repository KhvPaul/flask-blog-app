import json
from datetime import datetime
from sqlalchemy import insert
from sqlalchemy.exc import PendingRollbackError

from db import db
from .models import Blog, Blogger, Comment, Role, roles_bloggers_table
from .utils.security import user_datastore

color = lambda x, y, z: ";".join([str(x), str(y), str(z)])

red = lambda x: '\x1b[%sm%s\x1b[0m' % (color(6, 31, 40), x)
yellow = lambda x: '\x1b[%sm%s\x1b[0m' % (color(6, 33, 40), x)
green = lambda x: '\x1b[%sm%s\x1b[0m' % (color(6, 32, 40), x)
cyan = lambda x: '\x1b[%sm%s\x1b[0m' % (color(6, 36, 40), x)

to_date = lambda x: datetime.strptime(x[:x.rfind('.')], '%Y-%m-%d %H:%M:%S')


def fill_db():

    with open('fixtures/role.json', 'r') as file:
        data = json.load(file)
        print(cyan('Inserting \'Role\' tuples'))
        for i in data:
            if Role.query.filter(Role.id == i['id']).first():
                print(yellow(f'id:{i["id"]} exists.'), end=' ')
                continue
            user_datastore.create_role(**i)
            try:
                db.session.commit()
                print(green(f'id:{i["id"]} added.'), end=' ')
            except:
                print(red(f'id:{i["id"]} error.'), end=' ')
    print()

    with open('fixtures/blogger.json', 'r') as file:
        data = json.load(file)
        print(cyan('Inserting \'Blogger\' tuples'))
        for i in data:
            if Blogger.query.filter(Blogger.id == i['id']).first():
                print(yellow(f'id:{i["id"]} exists.'), end=' ')
                continue
            i['created_on'] = to_date(i['created_on'])
            i['updated_on'] = to_date(i['updated_on'])
            blogger = Blogger(**i)
            try:
                db.session.add(blogger)
                db.session.commit()
                print(green(f'id:{i["id"]} added.'), end=' ')
            except:
                print(red(f'id:{i["id"]} error.'), end=' ')
    print()

    with open('fixtures/roles_bloggers.json', 'r') as file:
        data = json.load(file)
        print(cyan('Inserting \'roles_bloggers_table\' tuples'))
        for i in data:
            rb = roles_bloggers_table.insert().values(**i)
            # try:
            role = Role.query.filter(Role.id == i['role_id']).first()
            blogger = Blogger.query.filter(Blogger.id == i['blogger_id']).first()
            if not blogger.has_role(role):
                try:
                    db.session.execute(rb)
                    db.session.commit()
                    print(green(f'Blogger({i["blogger_id"]}): role{["role_id"]} added.'), end=' ')
                except:
                    print(red(f'Blogger({i["blogger_id"]}): role{["role_id"]} error.'), end=' ')
            else:
                print(yellow(f'Blogger({i["blogger_id"]}): role{["role_id"]} exists.'), end=' ')
    print()

    with open('fixtures/blog.json', 'r') as file:
        data = json.load(file)
        print(cyan('Inserting \'Blog\' tuples'))
        for i in data:
            if Blog.query.filter(Blog.id == i['id']).first():
                print(yellow(f'id:{i["id"]} exists.'), end=' ')
                continue
            i['post_date'] = to_date(i['post_date'])
            blog = Blog(**i)
            try:
                db.session.add(blog)
                db.session.commit()
                print(green(f'id:{i["id"]} added.'), end=' ')
            except:
                print(red(f'id:{i["id"]} error.'), end=' ')
        print()

    with open('fixtures/comment.json', 'r') as file:
        data = json.load(file)
        print(cyan('Inserting \'Comment\' tuples'))
        for i in data:
            if Comment.query.filter(Comment.id == i['id']).first():
                print(yellow(f'id:{i["id"]} exists.'), end=' ')
                continue
            i['post_date'] = to_date(i['post_date'])
            comment = Comment(**i)
            try:
                db.session.add(comment)
                db.session.commit()
                print(green(f'id:{i["id"]} added.'), end=' ')
            except:
                print(red(f'id:{i["id"]} error.'), end=' ')
