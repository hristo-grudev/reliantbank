import scrapy

from scrapy.loader import ItemLoader

from ..items import ReliantbankItem
from itemloaders.processors import TakeFirst
import requests

base_url = "https://www.reliantbank.com/about/reliant-news/page/{}/"

class ReliantbankSpider(scrapy.Spider):
	name = 'reliantbank'
	page = 1
	start_urls = [base_url.format(page)]

	def parse(self, response):

		post_links = response.xpath('//div[@class="fl-post-grid-text"]')
		for post in post_links:
			url = post.xpath('.//a[@class="fl-post-grid-more"]/@href').get()
			date = post.xpath('.//span[@class="fl-post-grid-date"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		if post_links:
			self.page += 1
			yield scrapy.Request(base_url.format(self.page), self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="entry"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=ReliantbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
