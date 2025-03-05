from celery import Celery, Task
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from lxml import etree
from xmltodict import parse
import logging


URL = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html'
BROKER_URL = 'redis://localhost:6379/0'

logger = logging.getLogger(__name__)
app = Celery('tasks', broker=BROKER_URL)
app.conf.result_backend = BROKER_URL


def find_key(dict_, key):
    try:
        if key in dict_: 
            return dict_[key]
        for v in dict_.values():
            if isinstance(v, dict) and (found := find_key(v, key)):
                return found
    except AttributeError:
        pass
    return None


class GetPrintViewUrlsTask(Task):
    name = 'tasks.get_print_view_urls'

    def run(self, page_num, headers):
        try:
            params = {
                'fz44': 'on',
                'pageNumber': str(page_num)
            }
            response = requests.get(
                URL,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            tenders = soup.find_all('div', class_='col p-0 d-flex')
            print_view_urls = []
            for tender in tenders:
                links = tender.find_all('a')
                href = links[1].get('href')
                url_base = f"{urlparse(response.url).scheme}://{urlparse(response.url).netloc}"
                print_view_urls.append(f"{url_base}{href}")
            
            for url in print_view_urls:
                GetPubDateFromXmlTask().apply_async(args=(url, headers))
            
            return {"page": page_num, "urls": print_view_urls}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            self.retry(exc=e, countdown=60, max_retries=3)
        except Exception as e:
            logger.error(f"Error processing page {page_num}: {e}")
            raise


class GetPubDateFromXmlTask(Task):
    name = 'tasks.get_pub_date_from_xml'

    def run(self, print_view_url, headers):
        try:
            xml_url = print_view_url.replace('view', 'viewXml')
            response = requests.get(
                xml_url,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            parser = etree.XMLParser(recover=True)
            xml_content = etree.fromstring(response.content, parser=parser)
            tender_detail = parse(etree.tostring(xml_content))
            pub_date = find_key(tender_detail, 'publishDTInEIS')
            
            logger.info(f"Processed: {print_view_url} -- {pub_date}")
            return {'url': print_view_url, 'pub_date': pub_date}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {xml_url}: {e}")
            self.retry(exc=e, countdown=60, max_retries=3)
        except Exception as e:
            logger.error(f"Error processing XML for {print_view_url}: {e}")
            raise

app.register_task(GetPrintViewUrlsTask())
app.register_task(GetPubDateFromXmlTask())

if __name__ == '__main__':
    app.start()
