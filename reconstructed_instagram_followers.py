import bs4 as bs
import requests
import json
from spiderlib import utils
import random
import pickle
import logging
from proxy_collector import ProxyCollector



class IgSpider:
    def __init__(self):
        logging.info('Starting Spider.')

    def get_followers_count(self, username):
        logging.info('Start getting followers count.')
        try: # own ip (without proxy)
            
            logging.info('Using own ip...')
            # self.request_followers(username)
            raise AttributeError # just for testing. must be deleted.
        except AttributeError as e:
            # Now use proxies
            logging.info('[X]Failed with own ip...')
            logging.info('Trying some used & worked proxy...')
            logging.debug("Failed log: {}".format(e))
            while True:
                proxies = proxyman.return_proxies(limit=10)
                while len(proxies) != 0:
                    proxy = random.choice(proxies)
                    logging.debug(" Trying proxy: {}".format(proxy))
                    try:
                        followers_count = self.request_followers(username, proxy=proxy)
                        logging.info('[VVV]GET FOLLOWERS COUNT!!!'+ str(followers_count))
                        proxyman.add_proxy(proxy, status_for_projects="alive")
                        return followers_count
                    except AttributeError as e:
                        logging.debug(e)
                        logging.info('[X] ERROR!! Must been redirect to Login Page.')
                        proxies.remove(proxy)
                    except requests.exceptions.ProxyError as e:
                        logging.info("[X] Failed. Changing proxy...")
                        proxies.remove(proxy)

    def request_followers(self, username, proxy=None):
        if proxy != None:
            logging.debug(" Proxy detected & used: {}".format(proxy))
            
            # First Test if proxy is working. 
            try:
                logging.debug
                proxyman.get_my_ip(proxy=proxy)
            except requests.exceptions.ProxyError as e:
                logging.debug("[X] ProxyError: {}".format(e))
                logging.info("[X] Proxy not working, Please change proxy.")
                proxyman.add_proxy(proxy, status="dead")
                raise requests.exceptions.ProxyError
            
            # Formatting
            proxy = proxyman.format_proxy_with_http(proxy)
            proxy_scheme = {
                "http": proxy,
                "https": proxy,
            }
            proxy = proxy_scheme

        url = "https://www.instagram.com/{}/".format(username)
        req = requests.get(url, proxies=proxy)
        soup = bs.BeautifulSoup(req.text, 'lxml')
    
        ld = self.get_ld_json(soup)
        logging.debug("Get ld+json: {}".format(ld))
        followers_count = ld['mainEntityofPage']['interactionStatistic']['userInteractionCount']
        logging.debug("[V] Followers count: {}".format(followers_count))
    
        return followers_count

    def get_ld_json(self, soup):
        result_json = json.loads(
            "".join(soup.find("script", {"type": "application/ld+json"}).contents))
        return result_json

def btt_logic():
    #  Read last output and update BTT
    try:
        with open('last_output.pkl','rb') as f:
            raw = pickle.load(f)            
            print(json.dumps(raw))
    except FileNotFoundError as e:
        pass

    # Try to get newest followers_count (it might take long)
    spider = IgSpider()
    proxyman = ProxyCollector(filename='proxies')
    username = 'sa_____h'
    followers_count = spider.get_followers_count(username)
    
    # Formated for btt 
    icon_path = '/Users/pc1/Documents/Python/btt/instagram_followers/instagram.png'
    raw = {"text": str(followers_count),
           "icon_path": icon_path,
           "font_size": 15}
    
    # Write to pickle for next display
    with open('last_output.pkl','wb') as f:
        pickle.dump(raw, f)
    


if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    btt_logic()
    # spider = IgSpider()
    # proxyman = ProxyCollector(filename='proxies')
    # username = 'sa_____h'
    # followers_count = spider.get_followers_count(username)
    



