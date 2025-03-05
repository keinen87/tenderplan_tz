from tasks import GetPrintViewUrlsTask

LAST_PAGE_NUM = 2


def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://zakupki.gov.ru/'
    }
    for page_num in range(1, LAST_PAGE_NUM+1):
        GetPrintViewUrlsTask().apply_async(args=(page_num, headers))


if __name__ == "__main__":
    main()
