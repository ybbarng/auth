from csiphash import siphash24
from user_agents import parse

from .settings import SIPHASH_KEY


def to_user_id(slack_user_id):
    return siphash24(SIPHASH_KEY, slack_user_id.encode('utf-8')).hex()


def get_user_agent(request):
    return str(parse(str(request.user_agent)))
