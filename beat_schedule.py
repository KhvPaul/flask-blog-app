from celery.schedules import crontab

imports = ('app.blog.tasks.parse',)

BEAT_SCHEDULE = {
    'parse_gov_ua': {
        'task': 'news_parser_gov_ua',
        'schedule': crontab(minute='0'),
        # 'schedule': crontab(),
    },
    'parse_gordon_ua': {
        'task': 'news_parser_gordon_ua',
        'schedule': crontab(minute='30'),
        # 'schedule': crontab(),
    },
    'notify_blog_blogger': {
        'task': 'flaskBlog.blog.notify_blogger',
        'schedule': crontab(minute='*/5'),
    },
    'notify_comment_blogger': {
        'task': 'flaskBlog.blog.comment_message',
        'schedule': crontab(minute='*/5'),
    },
}