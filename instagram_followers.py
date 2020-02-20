import bs4 as bs
import requests
import json
from spiderlib import utils
import random
import pickle

headers = {
    "accept": "*/*",
    "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "origin": "https://www.instagram.com",
    "referer": "https://www.instagram.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "User-Agent": utils.getRandomUserAgent(use_default=True),
    "cookie": 'ig_did=0220A2E4-62FC-497B-94AB-260627697EE3; rur=FTW; mid=Xkz0ZwAEAAEv5aUUfrJuX50vML-f; csrftoken=dBnqpxkaqf1VuPcG06Ftu8TFPl66Svo3; shbid=13174; shbts=1582101634.3760698; ds_user_id=2615533363; sessionid=2615533363%3AyZOeMhEiZbF38u%3A7; urlgen="{\"125.227.225.215\": 3462}:1j4LTu:LJYt6cp8b3PTdKiqf6dLpaDFIS8"'
}

try:
    with open('proxies.pkl', 'rb') as f:
        disk_proxies = pickle.load(f)

except FileNotFoundError:
    disk_proxies = {
        'used_proxy': [],
        'working_proxy': [],
    }
    with open('proxies.pkl', 'wb') as f:
        pickle.dump(disk_proxies, f)

def get_ld_json(soup):

    result_json = json.loads(
        "".join(soup.find("script", {"type": "application/ld+json"}).contents))

    return result_json


def main(username):
    proxy_list = utils.getNewProxies(limit=5, last_check=120, https=True)
    if 'http://pubproxy.com/#premium' in proxy_list[0]:
        print("[!] Reach Max Request")
    
    global disk_proxies
    with open('proxies.pkl', 'rb') as f:
        disk_proxies = pickle.load(f)
    proxy_list = disk_proxies['working_proxy']

    used_proxy = []
    try_count = 1
    while True:
        try:
            debugflag = 0
            proxy = random.choice(proxy_list)
            debugflag = 1
            proxies_scheme = {'http': proxy, 'https': proxy}
            parser = "lxml"
            url = "https://www.instagram.com/{}/".format(username)
            # LOG # print("[Start {}] Target: {}".format(try_count, url))
            used_proxy.append(proxy)
            if proxy not in disk_proxies['used_proxy']:
                disk_proxies['used_proxy'].append(proxy)
                with open('proxies.pkl', 'wb') as f:
                    pickle.dump(disk_proxies, f)
            req = requests.get(url, proxies=proxies_scheme)
        except requests.exceptions.ProxyError as e:
            # LOG # print(e.__class__.__name__)
            # LOG # print("[{}]Proxy '{}' isn't work. try next.\n".format(try_count, proxy))
            if 'http://pubproxy.com/#premium' in proxy:
                print("[X] Reach Max Request, disk proxies not working neither.")
                exit()
            proxy_list.remove(proxy)
            try_count += 1
            continue
        except IndexError as e:
            if debugflag == 1:
                print('what?? pickle might went wrong.')
            print("[*] Run out of proxy.. need to fetch again. ({})".format(e))
            proxy_list = utils.getNewProxies(limit=5, last_check=60)
            proxy_list = [
                proxy for proxy in proxy_list if proxy not in used_proxy]
            if len(proxy_list) == 0:
                print("[X] Run out of proxy.")
                exit()
            continue
        except SSLError as e:
            print(e, end='\n\n')
            print("---> SSLError?? <----")

        try:
            soup = bs.BeautifulSoup(req.text, parser)
            try:
                ld = get_ld_json(soup)
            except AttributeError as e:
                # LOG # print('[XXX] ERROR!! Must been redirect to Login Page. Changing proxy...')
                continue
            followers_count = ld['mainEntityofPage']['interactionStatistic']['userInteractionCount']
            if proxy not in disk_proxies['working_proxy']:
                disk_proxies['working_proxy'].append(proxy)
                with open('proxies.pkl', 'wb') as f:
                    pickle.dump(disk_proxies, f)
            break
        except Exception as e:
            print(e)

    icon_path = '/Users/pc1/Documents/Python/btt/instagram_followers/instagram.png'
    raw = {"text": followers_count,
           "icon_path": icon_path,
           "font_size": 15}

    return json.dumps(raw)


def testIfAlive(username='sa_____h'):
    url = "https://www.instagram.com/{}/?__a=1".format(username)
    req = requests.get(url, headers=headers)
    soup = bs.BeautifulSoup(req.text)
    print(soup.title)
    return soup


if __name__ == '__main__':
    username = 'sa_____h'
    print(main(username))
