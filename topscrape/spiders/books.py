import requests
import scrapy
from bs4 import BeautifulSoup
from scrapy import Selector
from scrapy.http import Response

from topscrape.services import convert_to_int


class BooksSpider(scrapy.Spider):
    name = "books"

    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> dict:
        for url in response.css(
                ".product_pod > h3 > a::attr(href)"
        ).getall():

            detail_page_url = response.urljoin(url)

            page = self.get_detail_page(detail_page_url)

            title = page.css("div.col-sm-6.product_main > h1::text").get()
            price = page.css(".price_color::text").get()[2:]
            amount_in_stock = page.css(
                "p.instock.availability"
            ).xpath("string()").get().strip()
            _, rating = page.css("p.star-rating::attr(class)").get().split()
            category = page.xpath(
                "//th[text()='Product Type']/following-sibling::td/text()"
            ).get()
            description = page.css("article.product_page > p::text").get()
            upc = page.xpath(
                "//th[text()='UPC']/following-sibling::td/text()"
            ).get()

            yield {
                "Title": title,
                "Price": price,
                "Amount_in_stock": amount_in_stock,
                "Rating": convert_to_int(rating),
                "Category": category,
                "Description": description,
                "UPC": upc,
            }

        next_page = response.css("li.next > a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def get_detail_page(self, url: str) -> Selector | None:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            return Selector(text=str(soup))
        else:
            return None
