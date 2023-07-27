#!/usr/bin/env python
# encoding: utf-8
"""
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2020/4/14
"""
import json
import time
import random
from scrapy import Spider
from scrapy.http import Request
from spiders.common import parse_user_info, parse_time, url_to_mid
from fake_useragent import UserAgent


class CommentSpider(Spider):
    """
    微博评论数据采集
    """
    name = "comment"

    def start_requests(self):
        """
        爬虫入口
        """
        # 这里tweet_ids可替换成实际待采集的数据
        tweet_ids = ['Na7iI7XcK']
        # self.cnt = 0
        for tweet_id in tweet_ids:
            mid = url_to_mid(tweet_id)
            url = f"https://weibo.com/ajax/statuses/buildComments?" \
                  f"is_reload=1&id={mid}&is_show_bulletin=2&is_mix=0&count=20&uid=2706896955&fetch_level=0"
            yield Request(url, callback=self.parse, meta={'source_url': url})

    async def parse(self, response, **kwargs):
        """
        网页解析
        """
        data = json.loads(response.text)
        for comment_info in data['data']:
            item = self.parse_comment(comment_info)
            yield item
        # wait_seconds = random.uniform(0, 2)
        # time.sleep(wait_seconds)
        if data.get('max_id', 0) != 0:
            url = response.meta['source_url'] + '&max_id=' + str(data['max_id'])
            # self.cnt += 1
            # push_url = f"https://rm.api.weibo.com/2/remind/push_count.json"\
            #            f"?trim_null=1&with_dm_group=1&with_reminding=1&with_settings=1&exclude_attitude=1&with_chat_group_notice=1&source=339644097&with_chat_group=1&with_dm_unread=1&callback=__jp{self.cnt}"
            # yield Request(push_url, callback=lambda x: None, meta=response.meta)
            # yield Request("https://weibo.com/ajax/log/rum", callback=lambda x: None, meta=response.meta)
            yield Request(url, callback=self.parse, meta=response.meta, dont_filter=True)

    @staticmethod
    def parse_comment(data):
        """
        解析comment
        """
        item = dict()
        try:
            item['created_at'] = parse_time(data['created_at'])
            item['_id'] = data['id']
            item['like_counts'] = data['like_counts']
            item['ip_location'] = data['source']
            item['content'] = data['text_raw']
            item['comment_user'] = parse_user_info(data['user'])
            return item
        except:
            return item
