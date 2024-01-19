from flask import Flask, request
import jwt
import requests
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# GitHub App credentials
APP_ID = '765235'
PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAxOL70NJZUbueErZ93y+ftsQb1vefOpH4FcwqajtOabngzGjj
KLcvSNOOls87h6cO5CYVcsC7Coxjft+VnZ98aOQOMRkhgQiXUB9v1n1LPMhX6tUH
uVk/mIF9Ac/sysGJwB31gIZUv3wpjlASPTOadOCZ2A1Z5lwF7qQ5er1ByzXuDYzg
sPs2sWDDZcIHzJXA9j3tKeP8N7nX5xNOSA0tuD5xLY6sEPQ0+3zSmuABlDa3I5Ol
bZaWBtYShSEcyXSAxHEJq5gIZXxFR4WjQJ/8oKtOe4UZWHjNqI1rJZWODp+VsXWq
6e0y5BpNX3+tveteDLpZ8OPGJhTUXqSwXSqSywIDAQABAoIBADkyc9NbeIVNCwQG
rhSLgkuXNztBHqnmQ/sZH+1So1oFnO/lPLDUXtE6XH8lXvbuql3PToXSxcOvuyvd
ilqLPZo/Pnw2/8u7kjG9oEDgj13uGdRn5OGMsvP8EjPXksPoa7s7ONoIrFAgovXr
/xB2kFWJ9keUwVwxuat1XBlzJ8z/sGFDJ3FfMxdwaxsFeLPUil2PaGjp7uHnco6M
DWQOdxqne8ezDUsZyYE0lD3Z4KNw8/Kxt1UTdcFA0kstNzgTj7PpgBgktvoaxtZI
8Kg6rdli6aC59u2fup8DQWZnBwv9I8qVkjhEnCzrfRe9nOYXqEf28TInRbf015K9
OABVpWECgYEA4gtwr49U5XbfnKrI7dvZ0B5xr7LjZMyIJnSHFJ1v0j8r9J26CjpM
PdIQlWQvbM90oXvFztnwZ8W4fXZc/eC63XfExl9X00ssJJIdTJTIYUWCWBv/jyKO
IVKW8eNqgkhc8Hi/ot+4wZA3lR3P8Ro7ux9iHHspaUe4QBxkZrmsqJECgYEA3vpb
peBw48hCfDbznnlv7W0iER2HBzYvaiEmgafEG1Vg3xQuwunvzL1Qrpy0H9LeW0HV
Xh23YWg4831Tjuk5wVF4bZqhbzgc4rHHtmDSbdcYhIQ8JHFW7J//o2qils6G9FeN
L1Fq6CTC+S9E8IFBsjvd58soeXcg5fZ8OGgh05sCgYA6WUOkPbZnaRD9quQk6gxG
eaVU+jNScK1wZ8H6o00bE21wPkqomzXU+2WGeo73YnGzwXRlGcLBtrsRv7zvV9RE
mMb1geT0yMHDSug/PWSgH0YvIkMMmpnfpicKl26F5NIAzNqC24cgh+6hEkn77Y6f
ldFIks40u+umuO19ys3z0QKBgQDYKOKh6vPljiUN4APKVLVx+QM2jmZxUlEi1KJM
vQO678jqWdl/MWQ8GidWLynbVAQleavMAojdEDltqshPWb+Yrk9OCcKIXGB8T5Zp
MnGs9AGbrcnUFmALIoyjsmOOSQbBZwLCpW47QDAXe4CcmuHCVJEp/WPuZNNqu8nu
sNxiEwKBgFz0KKW+3pwoZalhk4TBBK7EG6wjNW2kAUV55DcWh0f8zpxu0WoiDiVt
KbYVNmkpwgF7ecWeB5Vz2RzV5hgo6KRb7UYxCoMlqo+cLtRJXHLjAMeySAlk2BEa
JEGCONIuAHE9HdY65+hzetFYd60RBUNy07IuruYP+ypCa1SxNxI1
-----END RSA PRIVATE KEY-----'''

# Generate JWT
def generate_jwt(app_id, private_key):
    time_now = datetime.utcnow()
    payload = {
        'iat': time_now,
        'exp': time_now + timedelta(minutes=10),
        'iss': app_id
    }
    encoded_jwt = jwt.encode(payload, private_key, algorithm='RS256')
    return encoded_jwt

# Get Installation Access Token
def get_installation_access_token(jwt, installation_id):
    headers = {
        'Authorization': f'Bearer {jwt}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
    response = requests.post(url, headers=headers)
    return response.json().get('token')
# Get the PR's Diff
def get_pr_diff(installation_token, repo_name, pr_number):
    headers = {
        'Authorization': f'token {installation_token}',
        'Accept': 'application/vnd.github.v3.diff'
    }
    url = f'https://api.github.com/repos/{repo_name}/pulls/{pr_number}'
    response = requests.get(url, headers=headers)
    return response.text

# Post a comment
def post_review_comment(installation_token, repo_name, pr_number, body, commit_id, path, position):
    headers = {
        'Authorization': f'token {installation_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = f'https://api.github.com/repos/{repo_name}/pulls/{pr_number}/comments'
    data = {
        'side': 'RIGHT',
        'body': body,
        'commit_id': commit_id,  # The SHA of the latest commit to the PR
        'path': path,            # The file path of the commented line
        'line': position     # The line index in the diff
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()


def download_patch(patch_url, installation_token):
    headers = {
        'Authorization': f'token {installation_token}',
        'Accept': 'application/vnd.github.patch'
    }
    response = requests.get(patch_url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from torch.utils.data import Dataset, DataLoader

tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModelForSequenceClassification.from_pretrained("microsoft/codebert-base", num_labels=2)

model.load_state_dict(torch.load('tester1.pth'))

def isgood(code_snippet):
    # Tokenize the code snippet
    inputs = tokenizer(code_snippet, return_tensors="pt", truncation=True, padding=True)

    # Run the model
    with torch.no_grad():
        outputs = model(**inputs)
        bad, good = outputs.logits[0]
    return good > bad

def parse_patch(patch):
    files = patch.split('diff --git a/')[1:]
    for file in files:
        head, *diff = re.split(r'@@ -\d+,\d+ \+(\d+),\d+ @@', file)
        filematch = re.search(r'[+]{3} b/(.*?\.js)\n', head)
        if not filematch:
            continue
        filename = filematch.group(1)
        for i in range(len(diff) // 2):
            pos, code = diff[2*i], diff[2*i + 1]
            code = re.sub(r'\n\\ No newline at end of file', '', code)
            code = re.sub(r'(^|\n)[+ ]', r'\1', re.sub(r'(^|\n)-.*\n', r'\1', code.strip()))
            if not isgood(code):
                yield int(pos), filename


@app.route('/', methods=['GET'])
def index():
    return 'Hello', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        payload = request.json
        if payload['action'] == 'opened' and 'pull_request' in payload:
            installation_id = payload['installation']['id']
            pr_number = payload['number']
            repo_name = payload['repository']['full_name']
            commit_id = payload['pull_request']['head']['sha']  # Extracting the commit ID

            jwt_token = generate_jwt(APP_ID, PRIVATE_KEY)
            installation_token = get_installation_access_token(jwt_token, installation_id)

            patch_content = download_patch(payload['pull_request']['url'], installation_token)
            print(f'patch_content = {patch_content}')
            if patch_content:
                for pos, filename in parse_patch(patch_content):
                    comment_body = "Quality attention required"
                    result = post_review_comment(installation_token, repo_name, pr_number, comment_body, commit_id, filename, pos)

        return "Webhook received", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')

