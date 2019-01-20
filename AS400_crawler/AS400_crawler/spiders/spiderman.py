import scrapy
from scrapy.selector import Selector
from AS400_crawler.items import As400CrawlerItem
from scrapy.http import Request
from lxml import etree
import re

class MySpider(scrapy.Spider):
    name = "AS400_crawler"
    allowed_domains = ['sg.jobsdb.com']
    start_urls = ['http://sg.jobsdb.com/j?q=AS400&l=Singapore']

    def start_requests(self):
        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        for url in self.start_urls:
            yield Request(url, headers=headers,callback=self.parse)

    def parse(self,response):
        item = As400CrawlerItem()
        hxs = Selector(response).xpath("//li[contains(@class,'result')]")
        elements = hxs.extract()
        for element in elements:
            item["source"] = "JobsDB"
            item["company"] = MySpider.getcompanyname(self,element)
            item["jobtitle"] = MySpider.getjobtitle(self,element)
            item["location"] = MySpider.getlocation(self,element)
            item["summary"] = MySpider.getsummary(self,element)
            yield item
        
        visited_links=[]
        links = hxs.xpath('//a/@href').extract()
        link_validator= re.compile("^(?:http|https):\/\/(?:[\w\.\-\+]+:{0,1}[\w\.\-\+]*@)?(?:[a-z0-9\-\.]+)(?::[0-9]+)?(?:\/|\/(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+)|\?(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+))?$")

        for link in links:
            if link_validator.match(link) and not link in visited_links:
                visited_links.append(link)
                yield Request(link, self.parse)
            else:
                full_url=response.urljoin(link)
                visited_links.append(full_url)
                yield Request(full_url, self.parse)




    def getcompanyname(self,element):
        parentnode = etree.XML(element)
        companyElement = parentnode.xpath("//li//span[@class='company']")
        if len(companyElement) <= 0:
            result = ""            
        else:
            result = companyElement[0].text
        return result

    def getjobtitle(self,element):
        parentnode = etree.XML(element)
        jobtitleElement = parentnode.xpath("//li//h2//a[@class='jobtitle']")
        if len(jobtitleElement) <= 0:
            result = ""
        else:
            result = jobtitleElement[0].text
        return result

    def getlocation(self,element):
        parentnode = etree.XML(element)
        locationElement = parentnode.xpath("//li//span[@class='location']")
        if len(locationElement) <= 0:
            result = ""           
        else:
            result = locationElement[0].text
        return result

    def getsummary(self,element):
        parentnode = etree.XML(element)
        summaryElement = parentnode.xpath("//li//div[@class='summary']")
        if len(summaryElement) <= 0:
            result = ""
        else:
            result = summaryElement[0].text
        return result





