import json

from flask import Blueprint, make_response, redirect, render_template, request, session, url_for
from flask_dance.contrib.slack import slack

from .settings import SLACK_TEAM_ID, SLACK_TEAM_NAME


routes = Blueprint('routes', __name__, template_folder='templates')


load_dotenv()
KEY_REDIRECT_URL = 'redirect_url'


@routes.route('/')
def index():
    from_url = request.args.get('from')
    if from_url:
        session[KEY_REDIRECT_URL] = from_url

    if not slack.authorized:
        return render_template('before_login.html', link=url_for('slack.login'), team_name=SLACK_TEAM_NAME)

    if not validate(slack.token['access_token']):
        return logout(render_template('before_login.html', link=url_for('slack.login')))

    try:
        return redirect(session.pop(KEY_REDIRECT_URL))
    except KeyError:
        pass

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


def validate(token):
    return get_user(token) is not None


# 이유는 모르겠는데 invalid_auth이 발생함
def check_validate_with_auth_test(token):
    headers = {
        'Content-type': 'application/json; charset=utf-8',
    }
    response = slack.post('/api/auth.test', headers=headers, data=json.dumps({'token': token}))
    print(response.request.headers)
    print(response.request.body)
    print(response.json())
    return response.json()['ok']


def get_user(slack_token):
    response = slack.get('/api/users.identity?token={}'.format(slack_token))
    identity = response.json()
    if identity['ok'] and identity['team']['id'] == SLACK_TEAM_ID:
        return identity['user'] # {'name': '', 'id': ''}
    else:
        return None
