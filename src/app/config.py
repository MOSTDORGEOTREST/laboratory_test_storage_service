import os
from dotenv import load_dotenv
import http.client

if os.path.exists(os.path.normpath(".env")):
    load_dotenv(dotenv_path=os.path.normpath(".env"))

def get_self_public_ip():
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    return conn.getresponse().read().decode()

class Configs:
    host_ip: str = get_self_public_ip()
    database_url: str = os.environ.get('DATABASE_URL')
    superuser_name: str = os.environ.get('SUPERUSER_NAME')
    superuser_password: str = os.environ.get('SUPERUSER_PASSWORD')
    jwt_secret: str = os.environ.get('JWT_SECRET')
    jwt_algorithm: str = os.environ.get('JWT_ALGORITHM')
    jwt_expiration: int = os.environ.get('JWT_EXPIRATION')
    s3_pre_key: str = os.environ.get('S3_PRE_KEY')
    endpoint_url: str = os.environ.get('AWS_URI')
    aws_access_key_id: str = os.environ.get('AWS_ACCCESS_KEY')
    service_name: str = os.environ.get('AWS_SERVICE_NAME')
    aws_secret_access_key: str = os.environ.get('AWS_SECRET_KEY')
    region_name: str = os.environ.get('AWS_REGION')
    bucket: str = os.environ.get('AWS_BUCKET')

configs = Configs()
