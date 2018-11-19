from csiphash import siphash24
from datetime import datetime
import jwt
from user_agents import parse

from .settings import JWT_KEY, SIPHASH_KEY


def to_user_id(slack_user_id):
    return siphash24(SIPHASH_KEY, slack_user_id.encode('utf-8')).hex()


def get_user_agent(request):
    return str(parse(str(request.user_agent)))


def create_jwt(data):
    data['iat'] = datetime.utcnow()  # Issued At Claim
    return jwt.encode(data, JWT_KEY, algorithm='HS512').decode('utf-8')


def parse_jwt(jwt_data):
    return jwt.decode(jwt_data, JWT_KEY, algorithms=['HS512'])
