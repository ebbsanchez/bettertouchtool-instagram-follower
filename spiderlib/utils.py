import requests
import bs4 as bs
import importlib
import random


def r(module):
    return importlib.reload(module)


def getNewProxies(limit=1, last_check=1000, google=False, https=False):
    """
    #######################################################################
    #     PARAMETER             VALUES                DESCRIPTION         #
    #######################################################################
    # FORMAT          | json, txt             | Output format
    # LEVEL           | anonymous, elite      | Anonymity level
    # TYPE            | http, socks4, socks5  | Proxy protocol
    # LAST_CHECK      | 1-1000                | Last check time (in minutes)
    # LIMIT           | 1-20                  | Proxy results count
    # COUNTRY         | US,CA,...             | Country of the proxy
    # NOT_COUNTRY     | MX,CA,...             | Avoid proxy country
    # PORT            | `Number`              | Specify port number
    # GOOGLE          | `Boolean`             | Google passed proxies
    # HTTPS           | `Boolean`             | Supports HTTPS request
    # GET             | `Boolean`             | Supports GET request
    # POST            | `Boolean`             | Supports POST request
    # USER_AGENT      | `Boolean`             | Supports COOKIES request
    # COOKIES         | `Boolean`             | Supports USER_AGENT request
    # REFERER         | `Boolean`             | Supports REFERER request
    #

    # Retrieve two(2) http proxies from the US that support https.        #
    #######################################################################
    curl ""
    > 195.136.43.176:63909
    > 107.170.221.216:8080

    """
    args = {
        'FORMAT': 'txt',
        # 'LEVEL': 'anonymous',
        # 'TYPE': 'http',
        'LAST_CHECK': last_check,
        'LIMIT': limit,
        # 'COUNTRY': 'US',
        # 'NOT_COUNTRY': '',
        # 'PORT': 1234,
        'GOOGLE': google,
        'HTTPS': https,
        # 'GET': True,
        # 'POST': True,
        # 'USER_AGENT': True,
        # 'COOKIES': True,
        # 'REFERER': True,
    }
    formated_args = "&".join(
        ['{}={}'.format(key.lower(), str(args[key]).lower()) for key in args])

    url = "http://pubproxy.com/api/proxy?{args}".format(args=formated_args)
    proxy_list = requests.get(url).text.split('\n')
    proxy_list = ["".join(['http://', proxy])for proxy in proxy_list]

    return proxy_list

def function():
    pass

def getGoogleUserAgents():
    url = "https://developers.whatismybrowser.com/useragents/explore/software_name/googlebot/"
    resp = requests.get(url)
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    user_agents = soup.find_all("td", class_="useragent")
    user_agents = [agent.text for agent in user_agents]

    return user_agents


def getRandomUserAgent(use_default=False):
    if use_default:
        useragent = "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.120 Mobile Safari/537.36 (compatible; Googlebot/2.1; http://www.google.com/bot.html)"
        return useragent
    else:
        try:
            return random.choice(getGoogleUserAgents())
        except IndexError:
            print("[X] Can't get UserAgent.. use default.")
            useragent = "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.120 Mobile Safari/537.36 (compatible; Googlebot/2.1; http://www.google.com/bot.html)"
            return useragent
