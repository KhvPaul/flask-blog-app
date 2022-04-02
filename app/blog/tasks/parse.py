import requests
from bs4 import BeautifulSoup

from datetime import datetime

from celery import shared_task
from flask_mail import Message
from requests import ReadTimeout
from urllib3.exceptions import ProtocolError, ReadTimeoutError

from app.models import Blog, Blogger

from flask import current_app, render_template, url_for

from db import db

from app import celery, mail

import re

import sys


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


def connect(link):
    try:
        return requests.get(link)
    except:
        print(red(f'Connection Error --> {link}'))
        return 0


# @celery.task(name='send_parse_message')
def send_parse_message(title, link):
    message = Message(subject='Parsed Article Added',
                      recipients=[app.config['MAIL_DEFAULT_SENDER']],
                      html=render_template('mail/notify_article_parsed.html',
                                           article=formatted_title(title),
                                           origin=link,
                                           datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                      sender=app.config['MAIL_DEFAULT_SENDER'], )
    print(green(' Sending message '))
    mail.send(message)
    print(cyan(' Message sent '))
    # return True


def create_if_not_exist(title, content, link, author):
    title_exists = Blog.query.filter(Blog.title == title).first()
    content_exists = Blog.query.filter(Blog.content == content).first()
    start = link.rfind('/') + 1
    end = link.rfind('.')
    route = author + ':' + link[start:end if end and end > start else None]
    route_exists = Blog.query.filter(Blog.route == route).first()
    if not title_exists and not content_exists and not route_exists:
        blogger = Blogger.query.filter(Blogger.username == author).first()
        blog = Blog(
            title=title,
            content=content,
            blogger_id=blogger.id,
            is_posted=True,
            publication_request=True,
            notified=True,
            route=route
        )
        # blog.create_update_route(blogger=blogger, title=title)
        try:
            db.session.add(blog)
            db.session.commit()
            message = green(' Blog ') + selected_color(formatted_title(title), color(4,32,40)) + green(' successfully added ')
            print(message)
            try:
                send_parse_message(title, link)
            except:
                pass
        except:
            message = red(' Blog ') + selected_color(formatted_title(title), color(4, 31, 40)) + red(' hasn\'t been added ')
            print(message)
    else:
        message = purple(f' {author}: Blog ') + selected_color(formatted_title(title), color(4, 35, 40)) + purple(' exists in db ')
        print(message)


@shared_task(name='news_parser_gov_ua')
def news_parser_gov_ua():
    # https: // www.president.gov.ua / ru
    r = connect('https://www.president.gov.ua/')
    if r == 0:
        return 0
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, features='html.parser').find('div', {'class': 'item_section'})
        articles = soup.findAll("div", class_="item_stat")
        for article in articles:
            title = article.find("div", class_="item_text").find('a').text
            link = article.find("div", class_="item_text").find('a')['href']
            rp = connect(link)
            if rp == 0:
                print(red(f'Connection Error --> {str(link)}'))
                continue
            if rp.status_code == 200:
                paragraphs_block = BeautifulSoup(rp.text, features='html.parser').find('div',
                                                                                       {'class': 'article_content'})
                paragraphs = paragraphs_block.findAll('p')
                content = ''
                for p in paragraphs[1:-1]:
                    content += ' ' + p.text
                content = re.sub(" +", " ", content)

                create_if_not_exist(title=title, content=content, link=link, author='president.gov.ua')

    return True


@shared_task(name='news_parser_gordon_ua')
def news_parser_gordon_ua():
    # https://gordonua.com/news.html
    r = connect('https://gordonua.com/news.html')
    if r == 0:
        print(red('Connection Error --> https://gordonua.com/news.html'))
        return 0
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, features='html.parser').find('div', {'class': 'lenta sw34_20'})
        articles = soup.findAll("div", class_="row")
        for article_link in articles:
            link = article_link.find('div', {'class': 'lenta_head'}).find('a')['href']
            link = 'https://gordonua.com' + link if link[0] == '/' else link
            rp = connect(link)
            if rp == 0:
                print(red(f'Connection Error --> {str(link)}'))
                continue
            if rp.status_code == 200:  # rp -> request page
                article = BeautifulSoup(rp.text, features='html.parser').find('div', {'class': 'block article'})
                title = article.find("h1", class_="a_head flipboard-title").text
                content = article.find("h2", class_="newposiziwin flipboard-subtitle")
                content = str(content.text + ' ') if content else ''
                paragraphs_block = article.find("div", class_="a_body newposiziwin")
                paragraphs = paragraphs_block.findAll('p', {'style': 'text-align: justify;'})
                for p in paragraphs:
                    content += p.text
                content = re.sub(" +", " ", content)
                create_if_not_exist(title=title, content=content, link=link, author='gordonua.com')
    return True
