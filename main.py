from time import sleep
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from lxml import etree
from xmltodict import parse


URL = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html'


def find_key(d, key):
    try:
        if key in d: return d[key]
        for v in d.values():
            if (found := find_key(v, key)):
                return found
    except AttributeError:
        pass
    return None


def get_print_view_urls(url, headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    tenders = soup.find_all('div', class_='col p-0 d-flex')
    print_view_urls = []
    for tender in tenders:
        print_view_url_part = tender.find_all('a')[1].get('href')
        url_part = f'{urlparse(url).scheme}://{urlparse(url).netloc}'
        print_view_urls.append(f'{url_part}{print_view_url_part}')
    return print_view_urls


def get_pub_date_from_xml(url, headers):
    print_xml_view_url = url.replace('view', 'viewXml')
    parser = etree.XMLParser(recover=True)
    xml_content = etree.fromstring(requests.get(print_xml_view_url, headers=headers).content, parser=parser)
    tender_detail = parse(etree.tostring(xml_content))
    pub_date = find_key(tender_detail, 'publishDTInEIS')
    return pub_date        
    

def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://zakupki.gov.ru/'
    }
    params = {
        'fz44': 'on',
        'pageNumber': None
    }

    all_print_view_urls = []
    for page_num in range(1, 3):
        try:
            params['pageNumber'] = str(page_num)
            response = requests.get(URL, params=params, headers=headers)
            print_view_urls = get_print_view_urls(response.url, headers)
            all_print_view_urls.extend(print_view_urls)
        except requests.HTTPError as http_error:
            print(f'HTTPError: {http_error}')
        except requests.ConnectionError as connection_error:
            print(f'ConnectionError: {connection_error}')

    for index, print_view_url in enumerate(all_print_view_urls, start=1):
        try:
            sleep(1)
            pub_date = get_pub_date_from_xml(print_view_url, headers)
            print(f'{index}. {print_view_url} -- {pub_date}')
        except Exception as error:
            print(f'xmlError: {error}')
            continue


if __name__ == "__main__":
    main()