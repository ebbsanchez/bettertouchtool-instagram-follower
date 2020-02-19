# "{"text":followers_count,
# "icon_data": "base64_icon_data",
# "icon_path":icon_path}"

import bs4 as bs
import requests
import json


def get_ld_json(username):
    parser = "html.parser"
    url = "https://www.instagram.com/{}/".format(username)
    req = requests.get(url)
    soup = bs.BeautifulSoup(req.text, parser)
    return json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents))


def main(username):

    ld = get_ld_json(username)

    icon_path = '/Users/pc1/Documents/Python/btt/instagram_followers/instagram.png'
    followers_count = ld['mainEntityofPage']['interactionStatistic']['userInteractionCount']

    raw = {"text": followers_count,
           "icon_path":icon_path,
           "font_size": 15}

    return json.dumps(raw)


username = 'sa_____h'
print(main(username))
