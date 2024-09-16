import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class LabirintruSpider(scrapy.Spider):
    name = "labirintru"
    allowed_domains = ["labirint.ru"]
    start_urls = ["https://www.labirint.ru/search/%D1%84%D0%B0%D0%BD%D1%82%D0%B0%D1%81%D1%82%D0%B8%D0%BA%D0%B0/?stype=0"]

    def parse(self, response:HtmlResponse):

        # Получаем ссылку на следующую страницу, если она есть
        next_page = response.xpath('//div[@class="pagination-next"]/a/@href').get()
        if next_page:
            # Рекурсивный вызов функции со ссылкой следующей страницей
            yield response.follow(next_page, callback=self.parse)
        else:
            print('Следующих страниц больше нет')

        # Собираем ссылки со всех книг на странице
        links = response.xpath("//a[@class='product-card__img']/@href").getall()
        for link in links:
            # Делаем запросы для каждой ссылки, ответы от запросов будут направлятся в book_parse
            yield response.follow(link, callback=self.book_parse)

    # Функция парсит страницу книги
    def book_parse(self, response:HtmlResponse):
        name = response.xpath("//h1/text()").get()  # название книги
        author = response.xpath("//a[@data-event-label='author']/text()").getall()  # автор
        translator = response.xpath("//a[@data-event-label='translator']/text()").getall()  # переводчик
        artist = response.xpath("//div[@class='authors']/a[not(@data-event-label='author') and "
                                "not(@data-event-label='translator') and "
                                "not(@data-event-label='editor')]/text()").getall()  # художник
        editor = response.xpath("//a[@data-event-label='editor']/text()").getall()  # редактор
        publishing = response.xpath("//a[@data-event-label='publisher']/text()").getall()  # издательство
        year = response.xpath("//div[@class='publisher']/text()").getall()  # год
        series = response.xpath("//a[@data-event-label='series']/text()").getall()  # серия
        collection = response.xpath("//div[@class='collections']/a/text()").getall()  # коллекция
        genre = response.xpath("//a[@data-event-label='genre']/text()").getall()  # жанр
        weight = response.xpath("//div[@class='weight']/text()").get()  # вес книги
        dimensions = response.xpath("///div[@class='dimensions']/text()").get()  # размеры
        rating = response.xpath("//div[@id='rate']/text()").get()  # рейтинг
        price = response.xpath("//span[@class='buying-pricenew-val-number']/text()").get()  # цена
        link = response.url  # url

        # Отправляем данные в Pipeline
        yield BookparserItem(name=name, author=author, translator=translator, artist=artist, editor=editor,
                             publishing=publishing, year=year, series=series, collection=collection, genre=genre,
                             weight=weight, dimensions=dimensions, rating=rating, price=price, link=link)
