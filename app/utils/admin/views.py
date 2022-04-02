from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user

from flask import redirect, url_for, flash, abort


class AdminHomeView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_active and current_user.is_authenticated:
            if 'admin' in current_user.roles:
                return True
            else:
                abort(403)
        else:
            return False

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('security.login')+'?next=/admin/')


class BloggerModelAdmin(ModelView):
    column_list = ('username', 'email', 'created_on', 'updated_on')
    # create_modal = True

    # def on_model_change(self, form, model, is_created=False):
    #     model.picture = bytes(model.picture, 'utf-8')
    #     pass

    def is_accessible(self):
        if current_user.is_active and current_user.is_authenticated:
            if 'admin' in current_user.roles:
                return True
            else:
                abort(403)
        else:
            return False

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('security.login')+'?next=/admin/blogger')


class BlogModelAdmin(ModelView):
    column_list = ('blogger', 'title', 'post_date', 'is_posted', 'publication_request')
    can_view_details = True

    def is_accessible(self):
        if current_user.is_active and current_user.is_authenticated:
            if 'admin' in current_user.roles:
                return True
            else:
                abort(403)
        else:
            return False

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('security.login')+'?next=/admin/blog')


class CommentModelAdmin(ModelView):
    column_list = ('blogger', 'title', 'post_date', 'is_posted', 'publication_request')

    def is_accessible(self):
        if current_user.is_active and current_user.is_authenticated:
            if 'admin' in current_user.roles:
                return True
            else:
                abort(403)
        else:
            return False

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('security.login')+'?next=/admin/comment')
