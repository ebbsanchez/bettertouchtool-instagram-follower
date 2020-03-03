import requests
import pandas as pd
import logging
import json
from datetime import datetime
import math

class ProxyCollector:
    def __init__(self, filename, dont_init=False):
        self.filename = 'datasets/{}.csv'.format(filename)
        self.columns = ["ip:port", 'status',
                        'status_for_projects', 'updated_time']
        self.proxies_df = pd.DataFrame(columns=self.columns)
        self.proxies_on_call = []

        if not dont_init:
            self.init_df()
        else:
            logging.warning(
                ' Not loading old data. Will get clean DataFrame and it might overwrite the old {}.csv. Make sure you are using clean file for testing.'.format(self.filename))

    def init_df(self):
        logging.debug("[init] Loading {}...".format(self.filename))
        try:
            with open(self.filename, 'rb') as f:
                self.proxies_df = pd.read_csv(self.filename)
            logging.info("[init] {} loaded.".format(self.filename))
        except FileNotFoundError as e:
            logging.info(
                "[init] {} not found. get clean DataFrame... the file not exists and directory need to be created.".format(self.filename))

    def get_my_ip(self, proxy=None):
        # """NOTE: Proxy need to be full path (http://xxx.xxx.xxx.xxx:xxxx) """
        if proxy == None:
            pass
        else:
            proxy = self.format_proxy_with_http(proxy)
            proxy = {
                'http': proxy,
                'https': proxy,
            }
        req = requests.get('https://api.ipify.org?format=json', proxies=proxy)
        req_json = json.loads(req.text)
        logging.debug("My {} is: {}".format('IP', req_json['ip']))
        return req_json['ip']

    def format_proxy_with_http(self, proxy):
        logging.debug("proxy= {}".format(proxy))
        if proxy.startswith('http://'):
            return proxy
        else:
            return "http://{}".format(proxy)

    def collect_raw_proxy(self, url):
        proxy_list = requests.get(url).text.split('\n')
        for proxy in proxy_list:
            try:
                ip = self.get_my_ip(proxy=proxy)
                logging.info(' Proxy worked. IP: {}'.format(ip))
                self.add_proxy(proxy, status='alive')
            except requests.exceptions.ProxyError as e:
                logging.info(' {} proxy not working...'.format(proxy))
            except requests.exceptions.InvalidProxyURL as e:
                logging.info(
                    "Not a valid proxy url. Assume is the end of file.")
                pass
        return

    def add_proxy(self, proxy, status="", status_for_projects="", save=True):

        old_proxies = self.proxies_df['ip:port'].to_list()
        now_time = datetime.strftime(datetime.now(), '%Y-%m-%d')

        if not (proxy in old_proxies):
            logging.info("[Add Proxy] New proxy Addedd: {}.".format(proxy))
            if status == "":
                status = 'unknown'
            if status_for_projects == "":
                status_for_projects = 'unknown'

            new_proxies = pd.DataFrame(
                [[proxy, status, status_for_projects, now_time]], columns=self.columns)
            self.proxies_df = self.proxies_df.append(
                new_proxies, ignore_index=True)
        else:
            logging.info("[Add Proxy] Knowned proxy. Updated.")
            if status == "":
                status_series = self.proxies_df.loc[self.proxies_df['ip:port'] == proxy, "status"]
                try:
                    status = status_series.item()
                except ValueError as e:
                    if len(status_series) > 1:
                        self.clean_duplicated_proxy(proxy)
                        logging.warning("[!!!]Find Duplicated proxy.. cleaning duplicated.. but somewhere must to get fixed.")
                        status_series = self.proxies_df.loc[self.proxies_df['ip:port'] == proxy, "status"]
                        status = status_series.item()
                    else:
                        raise ValueError

            if status_for_projects == "":
                status_for_projects_series = self.proxies_df.loc[self.proxies_df['ip:port'] == proxy, "status_for_projects"]
                try:
                    status_for_projects = status_for_projects_series.item()
                except ValueError as e:
                    if len(status_for_projects_series) > 1:
                        self.clean_duplicated_proxy(proxy)
                        logging.warning("[!!!]Find Duplicated proxy.. cleaning duplicated.. but somewhere must to get fixed.")
                        status_for_projects_series = self.proxies_df.loc[self.proxies_df['ip:port'] == proxy, "status_for_projects"]
                        status_for_projects = status_for_projects_series.item()
                    else:
                        raise ValueError

            self.proxies_df.loc[self.proxies_df['ip:port'] == proxy, [
                "status", "status_for_projects", "updated_time"]] = [status, status_for_projects, now_time]

        if save == True:
            with open(self.filename, 'w') as f:
                self.proxies_df.to_csv(f, index=False)
            logging.debug(" Add proxy and SAVED to {}.".format(self.filename))
        else:
            logging.debug(
                " Add proxy but NOT SAVING to {}.".format(self.filename))

    def print_proxy_in_file(self):
        try:
            with open(self.filename, 'rb') as f:
                self.proxies_df = pd.read_csv(f)
            for index, proxy in self.proxies_df.iterrows():
                print("[*] {} is {}".format(proxy['ip:port'], proxy['status']))

        except FileNotFoundError as e:
            logging.debug(e)
            print("[*] {} not found. must be a new file? There is nothing to print.")

    def return_alive_proxy_series_list(self, test=False):
        # TODO: Test proxies before return.
        alive_proxies = []
        for index, proxy in self.proxies_df.iterrows():
            if proxy['status'] == 'alive':
                alive_proxies.append(proxy)
        return alive_proxies

    def return_proxies(self, limit=1, status="", status_for_projects=""):
        # TODO: Add 'updated_time' filter
        # QUIESTION: What if there is no proxy in DB?
        # TODO: Notify user if there is no proxy. -> It return Nan
        if status != "":
            result_df = self.proxies_df.loc[self.proxies_df['status'] == status]
        else:
            result_df = self.proxies_df.loc[self.proxies_df['status'] == "alive"]

        if status_for_projects != "":
            result_df = result_df.loc[result_df["status_for_projects"]
                                      == status_for_projects]

        result_series = result_df.sample(n=limit)['ip:port']
        result_list = result_series.to_list()
        
        if math.isnan(result_list[0]):
            logging.critical("There is no proxy anymore..")
            raise Exception
        else:
            return result_list

    def clean_duplicated_proxy(self, proxy):  # For bug fixing
        to_delete_df = self.proxies_df.loc[self.proxies_df['ip:port'] == proxy]
        to_delete_df = to_delete_df.sample()
        self.proxies_df = self.proxies_df.drop(to_delete_df.index[0])
        return


def quickset():
    proxyman = ProxyCollector(filename='proxies')
    return proxyman


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    proxyman = ProxyCollector(filename='proxies')
    print('IP: {}'.format(proxyman.get_my_ip()))
    # proxyman.add_proxy("170.81.35.26:36681")
    # proxyman.print_proxy_in_file()
    # a = proxyman.return_alive_proxy_series_list()
    # proxyman.collect_raw_proxy(url="https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt")
