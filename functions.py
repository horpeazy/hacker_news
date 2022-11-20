import math
from datetime import datetime


def paginate_news(page, selection, count=20):
    start = (page - 1) * count
    end = start + count
    total_pages = math.ceil(len(selection) / count)

    if page < total_pages:
        next_page = page + 1
    else:
        next_page = None
    if page == 1:
        prev_page = None
    elif page >= 2:
        prev_page = page - 1

    news = [news.format() for news in selection]
    result = news[start:end]
    data = {
        'news': result,
        'prev_page': prev_page,
        'next_page': next_page,
        'length': len(result)
    }
    return data


def populate_instance(instance, data):
    instance.hacker_news_id = data.get("id")
    instance.type = data.get("type")
    instance.time_posted = datetime.fromtimestamp(int(data.get("time")))
    instance.author = data.get("by")
    instance.deleted = data.get("deleted")
    instance.dead = data.get("dead")
    instance.text = data.get("text")
    instance.url = data.get("url")
    instance.title = data.get("title")
    instance.parent = data.get("parent")
    instance.parts = data.get("parts")
    instance.descedants = data.get("descedants")
    instance.score = data.get("score")
    instance.kids = data.get("kids")
