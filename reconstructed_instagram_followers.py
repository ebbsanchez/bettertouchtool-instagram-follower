import bs4 as bs
import requests
import json
from spiderlib import utils
import random
import pickle
import logging

logging.basicConfig(level=logging.DEBUG)
# DEBUG / INFO / WARNING / ERROR / CRITICAL


class Spider:
    def __init__(self):
        logging.info('Starting Spider.')

    def get_followers_count(self, username):
        logging.info('Start getting followers count.')
        try:
            logging.info('Using own ip...')
            request_followers(username)
        except failedException as e:
            logging.info('Failed with own ip...')
            logging.info('Trying some used & worked proxy...')
            proxies = get_local_proxies()
            while len(proxies) != 0:
                proxy = random.choose(proxies)
                try:
                    get_followers_count(proxy=proxy)
                    break
                except failedException as e:
                    proxies.remove(proxy)
            else:
                logging.info('Still not getting data...')
                logging.info("Fetching some proxies from: pubproxies.com. ")
                proxy_gen = get_pubproxies(limit=5)
                for proxy in proxy_gen:
                    try:
                        get_followers_count(proxy=proxy)
                        break
                    except failedException as e:
                        proxies.remove(proxy)

    def request_followers(self, username, proxy=None):
        url = "https://www.instagram.com/{}/".format(username)
        req = requests.get(url)
        soup = bs.BeautifulSoup(req.text, parser)
        try:
            ld = get_ld_json(soup)
            followers_count = ld['mainEntityofPage']['interactionStatistic']['userInteractionCount']
        except AttributeError as e:
            logging.info('ERROR!! Must been redirect to Login Page.')

    def get_ld_json(soup):
        result_json = json.loads(
            "".join(soup.find("script", {"type": "application/ld+json"}).contents))

        return result_json

    def get_my_ip(self, proxy=None):
        """NOTE: Proxy need to be full path (http://xxx.xxx.xxx.xxx:xxxx) """
        if proxy == None:
            pass
        else:
            proxy = {
                'http': proxy,
                'https': proxy,
            }
        req = requests.get('https://api.ipify.org?format=json',proxies=proxy)
        req_json = json.loads(req.text)
        logging.debug("My {} is: {}".format('IP', req_json['ip']))
        return req_json['ip']


if __name__ == '__main__':
    spider = Spider()
    proxyman = ProxyCollector()
    username = 'sa____h'
    # followers_count = spider.get_followers_count(username)
    # followers_count = spider.request_followers(username)
    proxy_list = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt').text.split('\n')
    for index in range(10):
        proxy = random.choice(proxy_list)
        proxy = 'http://' + proxy
        try:
            spider.get_my_ip(proxy=proxy)
        except requests.exceptions.ProxyError as e :
            print('[{}] proxy not working...'.format(index))
    # print(followers_count)
