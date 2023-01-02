import requests
from parsel import Selector
import multiprocessing
import threading
import pymongo

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.acwing
collection = db.acwing
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 QIHU 360EE"}


def get_page(page):
    url = f'https://www.acwing.com/activity/{page}/course/'
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    return response.text


def save_mongo(item):
    collection.insert_one(item)
    print('MongoDB保存成功')


def save_image(item):
    url = item['图片']
    response = requests.get(url, headers=headers)
    content = response.content
    try:
        with open(f'image/{item["标题"]}.png', 'wb') as file:
            file.write(content)
        print('图片保存成功')
    except:
        pass


def parse_one_item(p):
    title = p.css('span[class="activity_title"]::text').extract_first()
    text = p.css('span[class="activity_abstract"]::text').extract_first()
    try:
        try:
            bol = p.css('span[class="btn btn-success activity_status"]::text').extract_first().strip()
        except:
            bol = p.css('span[class="btn btn-warning activity_status"]::text').extract_first().strip()
    except:
        bol = p.css('span[class="btn btn-info activity_status disabled"]::text').extract_first().strip()
    strength = p.css('span[class="activity_td"]::text').extract()[0]
    time = p.css('span[class="activity_td"]::text').extract()[1]
    image = p.css('img[alt="活动封面"]::attr(src)').extract_first()
    item = {'标题': title, '简介': text, '状态': bol, '人数': strength, '时间': time, '图片': image}
    print(item)
    tm = threading.Thread(target=save_mongo, args=(item,))
    ti = threading.Thread(target=save_image, args=(item,))
    tm.start()
    ti.start()


def parse_page(text):
    html = Selector(text)
    content = html.xpath('//div[@class="panel-body"]')
    rom = content.xpath('//div[@class="activity-index-block"]')
    tl = []
    for p in rom:
        tl.append(threading.Thread(target=parse_one_item, args=(p,)))
    for th in tl:
        th.start()
    for th in tl:
        th.join()


def main():
    pl = []
    for i in range(1, 4):
        pl.append(multiprocessing.Process(target=parse_page, args=(get_page(i),), name=f'AcWing【{i}】'))
    for i in pl:
        i.start()
    for i in pl:
        i.join()
    print('【AcWing】爬取完毕')


if __name__ == "__main__":
    main()
