# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BlogPostItem(scrapy.Item):
    # Input từ User
    keyword = scrapy.Field()

    # Dữ liệu Cào được (Raw)
    source_url = scrapy.Field()
    raw_text = scrapy.Field()
    image_url = scrapy.Field()  # Link ảnh gốc

    # Dữ liệu AI xử lý (Output)
    ai_title = scrapy.Field()
    ai_content = scrapy.Field()
    ai_excerpt = scrapy.Field()

    # Dữ liệu WordPress
    wp_media_id = scrapy.Field() # ID ảnh sau khi upload
