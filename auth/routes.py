import json

from flask import Blueprint, make_response, redirect, render_template, request, session, url_for
from flask_dance.contrib.slack import slack

from .models import *
from .settings import SLACK_TEAM_ID, SLACK_TEAM_NAME
from .utils import to_user_id, get_user_agent, create_jwt


routes = Blueprint('routes', __name__, template_folder='templates')


load_dotenv()
KEY_REDIRECT_URL = 'redirect_url'


@routes.route('/')
def index():
    # TODO: redirect 안전하게: app id를 받아서 따로
    # 저장된 주소로만 redirect하는 방식이 좋을 것 같다.
    # 점점 Oauth를 구현하는 느낌
    from_url = request.args.get('from')
    if from_url:
        session[KEY_REDIRECT_URL] = from_url

    if not slack.authorized:
        return render_template('before_login.html', link=url_for('slack.login'), team_name=SLACK_TEAM_NAME)

    access_token = create_access_token(slack.token['access_token'])
    if access_token is None:
        return logout(render_template('before_login.html', link=url_for('slack.login')))

    try:
        response = make_response(redirect(session.pop(KEY_REDIRECT_URL) + '?access_token={}'.format(access_token)))
    except KeyError:
        response = make_response(render_template('after_login.html', link=url_for('routes.logout_view')))
    return response


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


def create_access_token(token, auto_save=True):
    slack_user = get_slack_user(token)
    if slack_user is None:
        return None
    if not auto_save:
        return slack_user is None

    user = get_or_create_user(slack_user)
    device = Device.create(user=user, name=get_user_agent(request))
    access_token = create_jwt({
        'user_id': user.id,
        'device_id': device.id
    })
    return access_token


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


def get_slack_user(slack_token):
    response = slack.get('/api/users.identity?token={}'.format(slack_token))
    identity = response.json()
    if identity['ok'] and identity['team']['id'] == SLACK_TEAM_ID:
        return identity['user'] # {'name': '', 'id': ''}
    else:
        return None


def get_or_create_user(slack_user):
    user_id = to_user_id(slack_user['id'])
    try:
        user = User.get(User.id == user_id)
    except User.DoesNotExist:
        user = User.create(id=user_id, name=slack_user['name'])
    return user
