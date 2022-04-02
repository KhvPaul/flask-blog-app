# from flask_security import MailUtil
#
# from .tasks import send_flask_mail
#
# class MyMailUtil(MailUtil):
#     pass
#
#     def send_mail(self, template, subject, recipient, sender, body, html, user, **kwargs):
#         send_flask_mail.delay(
#             subject=subject,
#             sender=sender,
#             recipients=[recipient],
#             body=body,
#             html=html,
#         )