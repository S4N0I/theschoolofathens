import scrapy
import sys
import re
import wikipedia
import time
from urllib.parse import unquote
import numpy as np


born_patterns = list(map(lambda regex: re.compile(regex, re.IGNORECASE), [
    r"\d+\s*(BC|AD)",
    r"\d+\s*(january|february|march|april|may|june|july|august|september|october|november|december)\s*\d+",
    r"(january|february|march|april|may|june|july|august|september|october|november|december)\s*\d+,\s*\d+",
    r"\d+(st|nd|rd|th)\s*century\s*(AD|BC|BCE|CE)",
    r"\d+\s*(AD|BC|BCE|CE)?"
]))

number_pattern = re.compile(r"\d+", re.IGNORECASE)
month_pattern = re.compile(r"(january|february|march|april|may|june|july|august|september|october|november|december)", re.IGNORECASE)
month_nr = {'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06', 'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12'}

pageid_map = {}

class PhilSpider(scrapy.Spider):
    name = "philosophers"
    allowed_domains = ["en.wikipedia.org"]
    download_delay = 1.0
    start_urls = ['https://en.wikipedia.org/wiki/List_of_philosophers_(A-C)', 'https://en.wikipedia.org/wiki/List_of_philosophers_(D-H)', 'https://en.wikipedia.org/wiki/List_of_philosophers_(I-Q)', 'https://en.wikipedia.org/wiki/List_of_philosophers_(R-Z)']

    def parse(self, response):
       for philosopher_link in response.css('div[class=mw-parser-output] > ul li a[href^="/wiki/"]::attr(href)').extract():
           url = response.urljoin(philosopher_link)
           req = scrapy.Request(url, callback=self.parse_philosopher)
           yield req


    def parse_philosopher(self, response):
        data = {}
        data['url'] = response.url
        data['img'] = self.get_img(response)
        data['pageid'] = self.resolve_pageid(response.url)
        data['name'] = self.parse_name(response)
        data['born'] = self.parse_born(response)
        data['school'] = self.parse_school(response)
        data['influences'] = self.parse_influences(response)
        data['influenced'] = self.parse_influenced(response)

        yield data

    
    def resolve_pageid(self, url):
        if url not in pageid_map:
            time.sleep(0.1)
            try:
                title = self.normalize(unquote(url.split('wiki/')[1]))
                pageid = wikipedia.page(title).pageid
                pageid_map[url] = pageid
                return pageid
            except:
                return None
        else:
            print('TABLE LOOKUP')
            return pageid_map[url]


    def normalize(self, str):
        return str.replace('_', ' ')


    def parse_name(self, response):
        matches = response.css('table[class="infobox biography vcard"] tbody tr th div::text').extract()
        return self.first_or_none(matches)

    
    def get_img(self, response):
        img_selector = response.xpath('//table/tbody/tr/td//img')
        if 'src' in img_selector.attrib:
            return 'https:' + img_selector.attrib['src']
        else:
            return None


    def parse_born(self, response):
        born = None
        matched_pattern = None
        bday = response.xpath('//table/tbody/tr//*[contains(@class, "bday")]/text()').get()
        if bday is not None:
            born = bday
        else:
            born_str = response.xpath('//table/tbody/tr/th[text() = "Born"]/following-sibling::td').xpath('string()').get()
            if born_str is not None:
                for pattern in born_patterns:
                    match = pattern.search(born_str)
                    if match is not None:
                        matched_pattern = pattern
                        born = match.group()
                        break

        try:
            return self.date_str_to_int(self.born_str_to_date_str(born, matched_pattern))
        except:
            return None

    
    def born_str_to_date_str(self, born_str, matched_pattern):
        if matched_pattern == born_patterns[0]:
            year_str = number_pattern.match(born_str).group()
            return self.year_sign(born_str) + year_str
        elif matched_pattern == born_patterns[1] or matched_pattern == born_patterns[2]:
            number_matches = re.findall(number_pattern, born_str)
            day_str = number_matches[0]
            if len(day_str) == 1:
                day_str = '0' + day_str
            year_str = number_matches[1]
            month_str = month_nr[re.findall(month_pattern, born_str)[0].lower()]
            return year_str + '-' + month_str + '-' + day_str
        elif matched_pattern == born_patterns[3]:
            century_str = number_pattern.match(born_str).group()
            return self.year_sign(born_str) + century_str + '00'
        elif matched_pattern == born_patterns[4]:
            year_str = number_pattern.match(born_str).group()
            return self.year_sign(born_str) + year_str
        else:
            return born_str

    
    def year_sign(self, born_str):
        if 'BC' in born_str or 'BCE' in born_str:
            return '-'
        else:
            return ''


    def date_str_to_int(self, date_str):
        datetime = np.datetime64(date_str)
        return int(datetime.astype('<M8[s]').astype(np.int64))

    
    def parse_school(self, response):
        school_data = []
        links = response.xpath('//table/tbody/tr/th[a[text() = "School"]]/following-sibling::td/a')
        for link in links:
            school_entry = {}
            school_entry['name'] = link.xpath('text()').get()
            school_entry['url'] = link.attrib['href']
            school_entry['pageid'] = self.resolve_pageid(response.urljoin(link.attrib['href']))
            school_data.append(school_entry)
        return school_data


    def parse_influences(self, response):
        influences_data = []
        links_pattern_1 = response.xpath('//table/tbody/tr//div[@class="NavHead" and contains(text(),"Influences")]/following-sibling::ul//li/a')
        links_pattern_2 = response.xpath('//table/tbody/tr//div[@class="NavHead" and contains(text(),"Influences")]/following-sibling::ul//li//div/a')
        links = links_pattern_1 + links_pattern_2
        for link in links:
            influences_entry = {}
            influences_entry['name'] = link.xpath('text()').get()
            influences_entry['url'] = link.attrib['href']
            influences_entry['pageid'] = self.resolve_pageid(response.urljoin(link.attrib['href']))
            influences_data.append(influences_entry)
        return influences_data

    
    def parse_influenced(self, response):
        influenced_data = []
        links_pattern_1 = response.xpath('//table/tbody/tr//div[@class="NavHead" and contains(text(),"Influenced")]/following-sibling::ul//li/a')
        links_pattern_2 = response.xpath('//table/tbody/tr//div[@class="NavHead" and contains(text(),"Influenced")]/following-sibling::ul//li//div/a')
        links = links_pattern_1 + links_pattern_2
        for link in links:
            influenced_entry = {}
            influenced_entry['name'] = link.xpath('text()').get()
            influenced_entry['url'] = link.attrib['href']
            influenced_entry['pageid'] = self.resolve_pageid(response.urljoin(link.attrib['href']))
            influenced_data.append(influenced_entry)
        return influenced_data


    def first_or_none(self, list):
        if not list:
            return None
        else:
            return list[0]




