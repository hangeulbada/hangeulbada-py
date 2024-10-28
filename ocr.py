import requests
import uuid
import time
import json
import os
from dotenv import load_dotenv
load_dotenv()


api_url = os.getenv('OCR_API_URL')
secret_key = os.getenv('OCR_SECRET_KEY')


# 이미지 경로
image_file = './static/103826131638027518579_66b9f0945dd57334d0755ca4.jpeg'

request_json = {
    'images': [
        {
            'format': 'jpeg',
            'name': 'demo'
        }
    ],
    'requestId': str(uuid.uuid4()),
    'version': 'V2',
    'timestamp': int(round(time.time() * 1000))
}

payload = {'message': json.dumps(request_json).encode('UTF-8')}
files = [
  ('file', open(image_file,'rb'))
]
headers = {
  'X-OCR-SECRET': secret_key
}

response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

# print(response.text.encode('utf-8'))
print(response.text)