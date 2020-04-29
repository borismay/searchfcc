import mechanize
from bs4 import BeautifulSoup
import requests
import socket

def read_url(url, timeout = 10):
    socket.setdefaulttimeout(timeout)
    return requests.get(url).text

def get_license_page(name):
    br = mechanize.Browser()
    URL = r'https://apps.fcc.gov/coresWeb/simpleSearch.do?btnSearch=true'
    print(URL)
    br.open(URL)
    br.select_form(name='advancedSearchForm')
    br['simpleSearchName'] = ['Business Name',]
    br['simpleSearchValue'] = name[:29] + '*'
    response2 = br.submit()
    data = response2.read()
    return data.decode('utf-8')

def get_frns(page):
    soup = BeautifulSoup(page, 'html.parser')
    frns = soup.find_all('a', href=lambda href: href and "?frn=" in href)
    if frns:
        return [frn.text.strip() for frn in frns]
    return []

def parse_frn(frn):
    frn_url = create_frn_link(frn)
    soup = BeautifulSoup(read_url(frn_url), 'html.parser')
    infos = soup.find_all('tr')
    d = {}
    for info in infos:
        key = info.find('th').text.strip()[:-1]
        value = info.find('td').text.strip()
        d[key] = value
    return d

def create_frn_link(frn):
    return r'https://apps.fcc.gov/coresWeb/searchDetail.do?frn={}'.format(frn)


if __name__ == '__main__':
    page = get_license_page('frontier')
    frns = get_frns(page)
    data = []
    for frn in frns:
        data.append(parse_frn(frn))