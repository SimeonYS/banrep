import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BanrepItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'
base = 'https://admin.banrepcultural.org/api/elasticsearch?type=article_category&page={}'

class BanrepSpider(scrapy.Spider):
	name = 'banrep'
	page = 0
	start_urls = [base.format(page)]

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['nodes']['article'])):
			title = data['nodes']['article'][index]['title']
			date = data['nodes']['article'][index]['date']
			link = data['nodes']['article'][index]['path']
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date, title=title))

		if self.page < data['pagination']['all']['total']:
			self.page += 12
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response, date, title):
		content = response.xpath('//div[@class="news-body"]//text() | //div[@class="body field"]//text()[not (ancestor::em)] | //div[contains(@class,"field field-name")]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BanrepItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
