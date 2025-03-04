from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


URL = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html'


def get_print_view_url(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    target_attr = 'w-space-nowrap ml-auto registry-entry__header-top__icon'
    print_view_url_part = soup.find('div', class_=target_attr).find_all('a')[1].get('href')
    url_part = f'{urlparse(url).scheme}://{urlparse(url).netloc}'
    return f'{url_part}{print_view_url_part}'


def main():
    params = {
        'fz44': 'on',
        'pageNumber': None
    }
    for page_num in range(1, 3):
        params['pageNumber'] = page_num
        try:
            response = requests.get(URL, params=params)
            response.raise_for_status()
            print_view_url = get_print_view_url(response.url)
        except requests.HTTPError as http_error:
            print(f'HTTPError: {http_error}')
        except requests.ConnectionError as connection_error:
            print(f'ConnectionError: {connection_error}')



if __name__ == "__main__":
    main()