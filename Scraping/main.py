import json
import scrapy
from models import Quote, Author
from itemadapter import ItemAdapter
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field


class QuoteItem(Item):
    author = Field()
    quote = Field()
    tags = Field()


class AuthorItem(Item):
    fullname = Field()
    born_date = Field()
    born_location = Field()
    description = Field()


class DataPipline:
    quotes = []
    authors = []

    def process_item(self, item, spider):
        adaptor = ItemAdapter(item)
        if isinstance(item, QuoteItem):
            quote = Quote(
                author=adaptor.get("author"),
                quote=adaptor.get("quote"),
                tags=adaptor.get("tags")
            )
            quote.save()
        elif isinstance(item, AuthorItem):
            author = Author(
                fullname=adaptor.get("fullname"),
                born_date=adaptor.get("born_date"),
                born_location=adaptor.get("born_location"),
                description=adaptor.get("description")
            )
            author.save()
        return item

    def close_spider(self, spider):
        with open("quotes.json", "w", encoding="utf-8") as fd:
            json.dump(self.quotes, fd, indent=2, ensure_ascii=False)
        with open("authors.json", "w", encoding="utf-8") as fd:
            json.dump(self.authors, fd, indent=2, ensure_ascii=False)


class QuotesSpider(scrapy.Spider):
    name = "get_quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]
    custom_settings = {"ITEM_PIPELINES": {DataPipline: 300}}

    def parse(self, response, **kwargs):
        for q in response.xpath('/html//div[@class="quote"]'):
            quote = q.xpath('span[@class="text"]/text()').get().strip()
            author = q.xpath('span/small[@class="author"]/text()').get().strip()
            tags = q.xpath('div[@class="tags"]/a/text()').extract()
            # TODO: clear tags
            yield QuoteItem(quote=quote, author=author, tags=tags)
            yield response.follow(url=self.start_urls[0] + q.xpath('span/a/@href').get(),
                                  callback=self.parse_author)  # Вказуємо яку функцію потрібно використати яка буде
            # займатись цим парсингом(посилання)
        next_link = response.xpath('/html//li[@class="next"]/a/@href').get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)

    @classmethod
    def parse_author(cls, response, **kwargs):
        content = response.xpath("/html//div[@class='author-details']")  # <-
        fullname = content.xpath("h3[@class='author-title']/text()").get().strip()
        born_date = content.xpath("p/span[@class='author-born-date']/text()").get().strip()
        born_location = content.xpath("p/span[@class='author-born-location']/text()").get().strip()
        description = content.xpath("div[@class='author-description']/text()").get().strip()
        yield AuthorItem(fullname=fullname, born_date=born_date, born_location=born_location, description=description)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()
