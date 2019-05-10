import json
import getpass
import requests as r
import uuid


UPLOAD_TEMPLATE = 'curl -X POST -d {} -u {}:{} https://api.github.com'
GITHUB_ENDPOINT = 'https://api.github.com/gists'


def share(snippet, public=False):
    return _share_github(snippet, public)


def _share_github(snippet, public=False):
    name = snippet.name
    if name == '':
        name = str(uuid.uuid4())
    file_content = {}
    file_content['public'] = public
    file_content['files'] = {snippet.name: {'content': snippet.content}}
    user = input('Username: ')
    passw = getpass.getpass()
    response = r.post(GITHUB_ENDPOINT,
                      data=json.dumps(file_content),
                      auth=(user, passw))

    status_code = response.status_code
    if 200 <= status_code < 300:
        return json.loads(response.text)['html_url']
    else:
        msg = 'Unable to create snippet, returned code: {}, reason: {}'
        raise Exception(msg.format(response.status_code, response.text))

