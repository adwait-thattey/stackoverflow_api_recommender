import requests
from bs4 import BeautifulSoup
import os
import models


def get_page(url, writeto=None, title=None):
    res = requests.get(url)
    if res.status_code == 200:
        if writeto:
            if title:
                f = open(os.path.join(writeto, title.replace('/', '-')), mode="w")
            else:
                url_last_part = url.split('/')[-1]
                f = open(os.path.join(writeto, url_last_part), mode="w")
            f.write(res.text)
            f.close()

    return res


def get_page_soup(url, writeto=None, title=None):
    res = get_page(url, writeto=writeto, title=title)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup



