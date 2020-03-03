import bs4 as bs
import requests
import json
from spiderlib import utils
import random
import pickle
import logging
from proxy_collector import ProxyCollector
from datetime import datetime
import math



class IgSpider:
    def __init__(self, filename="proxies"):
        logging.info('Starting Spider.')
        self.proxyman = ProxyCollector(filename=filename)
        self.failedsafe = 0

    def get_followers_count(self, username):
        logging.info('Start getting followers count.')
        try: # own ip (without proxy)
            
            logging.info('Using own ip...')
            # followers_count = self.request_followers(username)
            # return followers_count
            raise AttributeError # just for testing. must be deleted.
        except AttributeError as e:
            # Now use proxies
            logging.info('[X]Failed with own ip...')
            logging.info('Trying some used & worked proxy...')
            logging.debug("Failed log: {}".format(e))
            while True:
                proxies = self.proxyman.return_proxies(limit=1)
                followers_count = self.requests_with_proxies(proxies)
                if followers_count != None:
                    return followers_count

    def requests_with_proxies(self, proxies):
        while len(proxies) != 0:
            proxy = random.choice(proxies)
            logging.debug("proxies={}".format(proxies))
            logging.debug(" Trying proxy: {}".format(proxy))
            
            try: # Try Proxies. If get followers count, return

                followers_count = self.request_followers(username, proxy=proxy)
                logging.info('[VVV]GET FOLLOWERS COUNT!!!'+ str(followers_count))
                self.proxyman.add_proxy(proxy, status_for_projects="alive")
                return followers_count
            
            # except AttributeError as e: # If Error, test next proxies
            #     proxies.remove(proxy)
                
            #     logging.debug(e)
            #     logging.info('[X] ERROR!! Must been redirect to Login Page.')
            #     if self.failed():
            #         return "0000" 
                
            except requests.exceptions.ProxyError as e: # If Error, test next proxies
                logging.info("[X] Failed. Changing proxy...")
                proxies.remove(proxy)

        return None # If didnt get followers, return None.

    def failed(self):
        self.failedsafe += 1
        if self.failedsafe >= 100:
            logging.critical("Something is broken. prevneting infinite loop.")
            return True
        else:
            return False

    def request_followers(self, username, proxy=None):
        if proxy != None and math.isnan(proxy) != True:
            logging.debug(" Proxy detected & used: {}".format(proxy))

            # First Test if proxy is working. 
            try:
                self.proxyman.get_my_ip(proxy=proxy)
            except requests.exceptions.ProxyError as e:
                logging.debug("[X] ProxyError: {}".format(e))
                logging.info("[X] Proxy not working, Please change proxy.")
                self.proxyman.add_proxy(proxy, status="dead")
                raise requests.exceptions.ProxyError
            
            # Formatting
            proxy = self.proxyman.format_proxy_with_http(proxy)
            proxy_scheme = {
                "http": proxy,
                "https": proxy,
            }
            proxy = proxy_scheme
        elif math.isnan(proxy):
            logging.critical("There is no proxy. prxoy = nan in pandas")
            raise Exception 

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

    


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info('logging is up.')
    #  Read last output and update BTT
    try:
        with open('last_output.pkl','rb') as f:
            raw = pickle.load(f)            
            print(json.dumps(raw))
    except FileNotFoundError as e:
        pass

    # Try to get newest followers_count (it might take long)
    spider = IgSpider()
    username = 'sa_____h'
    followers_count = spider.get_followers_count(username)

    updated_time = datetime.strftime(datetime.now(), "%H:%M")
    
    # Formated for btt 
    icon_path = '/Users/pc1/Documents/Python/btt/instagram_followers/instagram.png'
    raw = {"text": "{} ({})".format(str(followers_count),updated_time),
           "icon_path": icon_path,
           "font_size": 15}
    
    # Write to pickle for next display
    with open('last_output.pkl','wb') as f:
        pickle.dump(raw, f)


