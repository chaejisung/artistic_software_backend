import requests
from requests import Response

google_login_url = 'http://127.0.0.1:8000/auth/google/login'

res = requests.get(google_login_url)

def print_res(res:Response):
    print("응답", res)
    print("응답 헤더", res.headers)
    print("응답 본문", res.json())
    print("요청 url", res.url)
    print("응답 쿠키", res.cookies)
    
print_res(res)