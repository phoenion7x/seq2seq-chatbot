import random
import requests
import requests.auth
import json
from user_agent import generate_user_agent
import time
import re

checker_username = ""  # Your app username
checker_password = ""  # Your app password
client_id = ""  # Your app client ID
client_secret = ""  # Your app client secret

emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)


def process_sentence(text):
    text = emoji_pattern.sub(r'', text)
    text = re.sub(r"[\([{})\]]", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"r\/\S+", "", text)
    text = text.replace('\n', '')
    text = text.replace('”', '"')
    text = text.replace('“', '"')
    text = text.replace('’', "'")
    text = text.replace('…', "...")
    text = text.replace('–', "-")
    # text = re.sub(r"(http?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)", "", text)
    if text == "removed" or "upvote" in text or text == "deleted" and "giphy" not in text:
        text = ""
    return text


def replies_printer(replies_set, main_comment):
    for reply in replies_set['data']['children']:
        try:
            reply_text = process_sentence(reply['data']['body'])
            if len(reply_text) < 240:
                if reply_text:
                    with open('out.txt', 'a') as out_file:
                        out_file.write(main_comment + "| $sep$ |" + reply_text + "\n")
            replies2 = reply['data']['replies']
            if replies2 != "":
                replies_printer(replies2, reply_text)
        except:
            pass


def generate():
    user_agent = generate_user_agent()
    client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    post_data = {"grant_type": "password", "username": checker_username, "password": checker_password, "scope": "read"}
    headers = {"User-Agent": user_agent}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data,
                             headers=headers)
    data = json.loads(response.text)
    auth_token = 'bearer ' + data['access_token']
    headers = {"Authorization": auth_token, "User-Agent": user_agent}
    after = ""
    for i in range(10):
        response = requests.get('https://oauth.reddit.com/r/all/top?limit=100&t=month&after=' + after, headers=headers)
        data = json.loads(response.text)
        posts = data['data']['children']
        post_list = []
        for post in posts[1:]:
            post_list.append(post['data']['permalink'])
        time.sleep(3)
        for link in post_list:
            post_link = 'https://oauth.reddit.com{}'.format(link)
            response = requests.get(post_link, headers=headers)
            data = json.loads(response.text)
            comments = data[1]['data']['children']

            for comment in comments[1:]:
                try:
                    comment_text = process_sentence(comment['data']['body'])

                except:
                    continue
                if len(comment_text) < 240 and comment_text:

                    replies = comment['data']['replies']
                    if replies != "":
                        replies_printer(replies, comment_text)

        after = "t3_" + post_list[-1].split('/')[4]


if __name__ == '__main__':
    generate()
