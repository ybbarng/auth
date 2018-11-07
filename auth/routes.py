from flask import Blueprint, make_response, redirect, render_template, url_for
from flask_dance.contrib.slack import slack


routes = Blueprint('routes', __name__, template_folder='templates')


@routes.route('/')
def index():
    if not slack.authorized:
        return render_template('before_login.html', link=url_for('slack.login'))
    else:
        response = slack.get('/api/users.identity?token={}'.format(slack.token['access_token']))
        if not response.json()['ok'] and False:
            return logout('before_login.html', link=url_for('slack.login'))
        return render_template('after_login.html', link=url_for('routes.logout_view'))


@routes.route('/revoke')
def revoke():
    response = slack.post('/api/auth.revoke?token={}'.format(slack.token['access_token']))
    return 'api key를 revoke 했습니다.'


@routes.route('/logout')
def logout_view():
    return logout(render_template('logout_success.html', link=url_for('routes.index')))


def logout(rv):
    response = make_response(rv)
    response.set_cookie('session', expires=0)
    return response
