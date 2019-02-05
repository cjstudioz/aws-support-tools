import urllib
import os
import requests
import json
import time
from datetime import datetime
from functools import lru_cache
from jose import jwk, jwt
from jose.utils import base64url_decode

def hosted_ui(
    domain_prefix:str,
    region:str,
    client_id:str,
    redirect_uri:str,
    response_type='token', #or code
) -> str:
    """
    domain_prefix = 'testing-nuco'
    region = 'eu-west-1'
    client_id = '3h4pi1cc4dd84u4uutedgsquni'
    redirect_uri = "https://d2vjwuugbmujh1.cloudfront.net/landing"
    response_type = 'token'
    hosted_ui(domain_prefix, regio, client_id, redirect_uri)  

    """
    params = [(k,v) for k,v in locals().items() if k not in ['domain_prefix', 'region']]
    encoded_params = urllib.parse.urlencode(params)
    res = f'https://{domain_prefix}.auth.{region}.amazoncognito.com/login?{encoded_params}'
    return res

@lru_cache()
def get_cognito_public_keys(
    region: str=os.environ.get('COGNITO_REGION'),
    userpool_id: str=os.environ.get('USERPOOL_ID'),
) -> list:
    """
    # https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/

    ## Example Usage ##
    region = 'us-east-1'
    userpool_id = 'us-east-1_SovB8fiRm'
    keys = get_cognito_public_keys(region, userpool_id)
    """
    keys_url = f'https://cognito-idp.{region}.amazonaws.com/{userpool_id}/.well-known/jwks.json'
    response = requests.get(keys_url)
    jkeys = json.loads(response.content)
    public_keys = {key['kid']: key for key in jkeys['keys']}
    return public_keys


def verified_claims(
    token: str,
    app_client_id: str=os.environ.get('COGNITO_CLIENT_ID'),
    public_keys: dict=None
) -> bool:
    """

    verified token signature, expiry and app_id then returns claims
    """
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']

    public_keys = public_keys or get_cognito_public_keys()
    public_key = jwk.construct(public_keys[kid])

    message, encoded_signature = str(token).rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

    if not public_key.verify(message.encode("utf8"), decoded_signature):
        raise RuntimeError(f'Signature verification failed')

    claims = jwt.get_unverified_claims(token)
    if time.time() > claims['exp']:
        expiry = datetime.fromtimestamp(claims['exp'])
        raise RuntimeError(f"Token expired at {expiry}, it is now {datetime.now()}")

    if app_client_id and claims['client_id'] != app_client_id:
        raise RuntimeError(f"Token audience {claims['aud']} was not issued for this audience {app_client_id}")

    return claims


if __name__ == '__main__':
    domain_prefix = 'testing-nuco'
    region = 'eu-west-1'
    client_id = '3h4pi1cc4dd84u4uutedgsquni'
    redirect_uri = "https://d2vjwuugbmujh1.cloudfront.net/landing"
    response_type = 'token'
    url = hosted_ui(domain_prefix, region, client_id, redirect_uri)
    print(url)


    region = 'us-east-1'
    userpool_id = 'us-east-1_SovB8fiRm'
    app_client_id = '4makg4kbaf49bt2pdm2vlrhkcm'
    keys = get_cognito_public_keys(region, userpool_id)
    token = 'eyJraWQiOiJDbjFPU1RndHZaSzNFMmdVNXhYSWRBeTlWU1RcL3QxaDNhc2R4Y2cwYlR1cz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJjZjk2ZmZjNi1jYTkwLTQ2ZDgtOTVjNy04MWVkN2NjOGRkOTgiLCJldmVudF9pZCI6IjllYzQzMmRkLTI4ZjQtMTFlOS04ZGQxLTIxNmFmZTJlOWY1ZSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE1NDkzMzY2NzEsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5ldS13ZXN0LTEuYW1hem9uYXdzLmNvbVwvZXUtd2VzdC0xXzc2R3BqREdSMiIsImV4cCI6MTU0OTM0MDI3MSwiaWF0IjoxNTQ5MzM2NjcxLCJ2ZXJzaW9uIjoyLCJqdGkiOiJiMGQyOGE2Yy1hYzc2LTQ1Y2UtODkwMS01MzRiY2U5ODdiNjAiLCJjbGllbnRfaWQiOiIzaDRwaTFjYzRkZDg0dTR1dXRlZGdzcXVuaSIsInVzZXJuYW1lIjoiY2Y5NmZmYzYtY2E5MC00NmQ4LTk1YzctODFlZDdjYzhkZDk4In0.KhNAYOMq811eTu3REuX3zFE9w_Zb8Dahl3kmIu0O7wlccu3TdeI86H-Mto_V-TX7JAkANdvDPAjJJAg0TbfCLpU60aYI0EYetRlBM2nnpJ5qEJ3vLhibzp00B9gVJL27ouMxGJpI3rA6iQMRA7uWn-lyRtq3axCWMub-u9uyniTK9afjiX8pqt_8ladAJxcsp8UPG3Sn0o2lzoe8pAQxpvzcpVIHH8fY60Vc2ELAEPGlUYZHDcLBA8sYYRnSeb11aTkslpFReu0GPtFYQ51sdGJJSRJw46EQep-e1NYMZtYUw5qX8eCM8i77jFl51_21NAIXEijcmoRcFORVqSvDcg'
    claims = verified_claims(token, app_client_id, keys)
    print(claims)
