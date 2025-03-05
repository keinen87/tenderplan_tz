# Tender search

Поиск печатных форм тендеров с датой публикации. 


# Как запустить

## Окружение

Python 3.10.10. Для установки зависимостей использовать pip(pip3):

```bash
pip install -r requirements.txt
```

Брокер redis можно запустить докером:

```bash
sudo docker run -d -p 6379:6379 --name redis redis
```

## Запуск

Далее в отдельной вкладке терминала запустите воркер:

```bash
celery -A tasks worker --loglevel=info
```

В текущей папке запустите таски:

```bash
python main.py
```