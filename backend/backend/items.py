# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BlogPostItem(scrapy.Item):
    """Blog post item - Clean version"""
    
    # Input từ User
    keyword = scrapy.Field()

    # Dữ liệu từ Google Search + Scraping
    source_url = scrapy.Field()
    raw_text = scrapy.Field()
    image_url = scrapy.Field()

    # Dữ liệu AI tạo ra (Output)
    ai_title = scrapy.Field()
    ai_content = scrapy.Field()
    ai_excerpt = scrapy.Field()