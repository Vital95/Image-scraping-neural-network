from bs4 import BeautifulSoup
import urllib3
import re
import os
import random
import sys
import time
from random import randint
from http.cookiejar import LWPCookieJar
from urllib.request import Request, urlopen
from urllib.parse import quote_plus, urlparse, parse_qs
import requests

urllib3.disable_warnings()

is_bs4 = True

'''
url_home = "https://www.google.%(tld)s/"
url_search = "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&btnG=Google+Search&tbs=%(tbs)s&safe=%(safe)s&tbm=%(tpe)s"
url_next_page = "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&start=%(start)d&tbs=%(tbs)s&safe=%(safe)s&tbm=%(tpe)s"
url_search_num = "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&num=%(num)d&btnG=Google+Search&tbs=%(tbs)s&safe=%(safe)s&tbm=%(tpe)s"
url_next_page_num = "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&num=%(num)d&start=%(start)d&tbs=%(tbs)s&safe=%(safe)s&tbm=%(tpe)s"
'''
#test
url_home = "https://www.google.%(tld)s/"
url_search = "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&btnG=Google+Search&tbs=%(tbs)s&safe=%(safe)s&tbm=%(tpe)s&filter=0"
url_next_page = "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&start=%(start)d&tbs=%(tbs)s&safe=%(safe)s&tbm=%(tpe)s&filter=0"
url_search_num = "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&num=%(num)d&btnG=Google+Search&tbs=%(tbs)s&safe=%(safe)s&tbm=%(tpe)s&filter=0"
url_next_page_num = "https://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&num=%(num)d&start=%(start)d&tbs=%(tbs)s&safe=%(safe)s&tbm=%(tpe)s&filter=0"

# Cookie jar. Stored at the user's home folder.
home_folder = os.getenv('HOME')
if not home_folder:
    home_folder = os.getenv('USERHOME')
    if not home_folder:
        home_folder = '.'   # Use the current folder on error.
cookie_jar = LWPCookieJar(os.path.join(home_folder, '.google-cookie'))
try:
    cookie_jar.load()
except Exception:
    pass

USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)'

install_folder = os.path.abspath(os.path.split(__file__)[0])
user_agents_file = os.path.join(install_folder, 'user_agents.txt')
try:
    with open('user_agents.txt') as fp:
        user_agents_list = [_.strip() for _ in fp.readlines()]
except Exception:
    user_agents_list = [USER_AGENT]

#not in use yet
def getLinks(url):
    http = urllib3.PoolManager()
    html_page = http.request('GET', url)
    soup = BeautifulSoup(html_page.data,"html.parser")
    links = []
    for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
        links.append(link.get('href'))
    return links

#print(getLinks("http://www.google.com"))
#print( getLinks("https://www.google.com.ua/search?q=aime+blond&oq=aime+blond&aqs=chrome..69i57.4536j0j8&sourceid=chrome&ie=UTF-8#q=anime+blonde") )

def get_page(url, user_agent=None):
    """
    Request the given URL and return the response page, using the cookie jar.
    @type  url: str
    @param url: URL to retrieve.
    @type  user_agent: str
    @param user_agent: User agent for the HTTP requests. Use C{None} for the default.
    @rtype:  str
    @return: Web page retrieved for the given URL.
    @raise IOError: An exception is raised on error.
    @raise urllib2.URLError: An exception is raised on error.
    @raise urllib2.HTTPError: An exception is raised on error.
    """
    if user_agent is None:
        user_agent = USER_AGENT
    request = Request(url)
    request.add_header('User-Agent', user_agent)
    #request.set_proxy('222.124.30.138:8080', 'https')
    #test
    #proxies = {'https': 'https://222.124.30.138:8080'}
    #if(requests.get(url, proxies=proxies).status_code == 200):
        #request.set_proxy(proxies)
    
    #test
    print(request.headers)
    cookie_jar.add_cookie_header(request)
    response = urlopen(request)
    cookie_jar.extract_cookies(response, request)
    html = response.read()
    response.close()
    cookie_jar.save()
    return html

def get_random_user_agent():
    """
    Get a random user agent string.
    @rtype:  str
    @return: Random user agent string.
    """
    return random.choice(user_agents_list)

def filter_result(link):
    try:
        # Valid results are absolute URLs not pointing to a Google domain
        # like images.google.com or googleusercontent.com
        o = urlparse(link, 'http')
        if o.netloc and 'google' not in o.netloc:
            return link

        # Decode hidden URLs.
        if link.startswith('/url?'):
            link = parse_qs(o.query)['q'][0]

            # Valid results are absolute URLs not pointing to a Google domain
            # like images.google.com or googleusercontent.com
            o = urlparse(link, 'http')
            if o.netloc and 'google' not in o.netloc:
                return link

    # Otherwise, or on error, return None.
    except Exception:
        pass
    return None


def search(query, tld='com', lang='en', tbs='0', safe='off', num=10, start=0,
           stop=None, pause=10.0, only_standard=False, extra_params={}, tpe='', user_agent=None):

    # Set of hashes for the results found.
    # This is used to avoid repeated results.
    hashes = set()

    # Prepare the search string.
    query = quote_plus(query)

    # Check extra_params for overlapping
    for builtin_param in ('hl', 'q', 'btnG', 'tbs', 'safe', 'tbm'):
        if builtin_param in extra_params.keys():
            raise ValueError(
                'GET parameter "%s" is overlapping with \
                the built-in GET parameter',
                builtin_param
            )
    
    # Grab the cookie from the home page.
    get_page(url_home % vars(), user_agent = user_agent)

    # Prepare the URL of the first request.
    if start:
        if num == 10:
            url = url_next_page % vars()
        else:
            url = url_next_page_num % vars()
    else:
        if num == 10:
            url = url_search % vars()
        else:
            url = url_search_num % vars()

    # Loop until we reach the maximum result, if any (otherwise, loop forever).
    while not stop or start < stop:

        try:  # Is it python<3?
            iter_extra_params = extra_params.iteritems()
        except AttributeError:  # Or python>3?
            iter_extra_params = extra_params.items()
        # Append extra GET_parameters to URL
        for k, v in iter_extra_params:
            url += url + ('&%s=%s' % (k, v))

        # Sleep between requests.
        pause = randint(30,50)
        time.sleep(pause)

        # Request the Google Search results page.
        html = get_page(url, user_agent = user_agent)

        # Parse the response and process every anchored URL.
        if is_bs4:
            soup = BeautifulSoup(html, 'html.parser')
        else:
            soup = BeautifulSoup(html)
        anchors = soup.find(id='search').findAll('a')
        for a in anchors:

            # Leave only the "standard" results if requested.
            # Otherwise grab all possible links.
            if only_standard and (
                    not a.parent or a.parent.name.lower() != "h3"):
                continue

            # Get the URL from the anchor tag.
            try:
                link = a['href']
            except KeyError:
                continue

            # Filter invalid links and links pointing to Google itself.
            link = filter_result(link)
            if not link:
                continue

            # Discard repeated results.
            h = hash(link)
            if h in hashes:
                continue
            hashes.add(h)

            # Yield the result.
            yield link

        # End if there are no more results.
        if not soup.find(id='nav'):
            break

        # Prepare the URL for the next request.
        start += num
        if num == 10:
            url = url_next_page % vars()
        else:
            url = url_next_page_num % vars()

#start
linksList = list()
step = 10
#for i in range(0, 200, step):
for url in search("anime blonde",start = 0, stop = 300,user_agent = get_random_user_agent()):
    print(url)
    with open('links.txt', "a") as myfile:
        myfile.write(url)
        myfile.write("\n")
try:
    sys.stdout.flush()
except:
    pass
