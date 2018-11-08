from flask import Blueprint, make_response, redirect, render_template, request, session, url_for
from flask_dance.contrib.slack import slack


routes = Blueprint('routes', __name__, template_folder='templates')


KEY_REDIRECT_URL = 'redirect_url'


@routes.route('/')
def index():
    from_url = request.args.get('from')
    if from_url:
        session[KEY_REDIRECT_URL] = from_url

    if not slack.authorized:
        return render_template('before_login.html', link=url_for('slack.login'))

    response = slack.get('/api/users.identity?token={}'.format(slack.token['access_token']))
    if not response.json()['ok']:
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
