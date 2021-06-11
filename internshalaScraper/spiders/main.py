import scrapy
import time
from scrapy.exceptions import CloseSpider


class MainSpider(scrapy.Spider):
    name = 'main'
    allowed_domains = ['internshala.com']
    start_urls = ['https://internshala.com/internships']
    no_of_internships = 100
    page_no = 1
    def parse(self, response):
        internships = response.xpath('//div[@id = "internship_list_container"]/div/div')
        self.page_no += 1
        for internship in internships :
            data = {
            "Internship Name" : internship.xpath('.//div[@class = "heading_4_5 profile"]/a/text()').get(),
            "Internship Details Page Link" : response.urljoin(internship.xpath('.//div[@class = "heading_4_5 profile"]/a/@href').get()),
            "Internship Organization" : internship.xpath('.//div[@class = "heading_6 company_name"]/a/text()').get().strip(),
            "Internship Organization Page Link" : response.urljoin(internship.xpath('.//div[@class = "heading_6 company_name"]/a/@href').get()),
            "Location Of Internship" : internship.xpath('.//div[@id = "location_names"]//a/text()').get(),
            "Start Date Of Internship" : internship.xpath('.//div[./span[contains(text(), "Start Date")]]/following-sibling::div/span[2]/text()').get(),
            "Duration" : internships.xpath('.//div[./span[contains(text(), "Duration")]]/following-sibling::div/text()').get().strip(),
            "Stipend" : internships.xpath('.//div[./span[contains(text(), "Stipend")]]/following-sibling::div/span/text()').get().strip(),
            "Application Deadline" : internships.xpath('.//div[./span[contains(text(), "Apply By")]]/following-sibling::div/text()').get().strip()
            }

            view_detail_url = internship.xpath('.//a[@class = "view_detail_button"]/@href').get()
            view_detail_url = response.urljoin(view_detail_url)
        
            yield scrapy.Request(url=view_detail_url, callback=self.parse_detail, meta=data)
        time.sleep(0.5)
        yield scrapy.Request(url=f"https://internshala.com/internships/page-{self.page_no}")

    def parse_detail(self, response) :
        
        applicants = response.xpath('//div[@class = "applications_message"]/text()').get()
        openings = response.xpath('//div[contains(text(), "Number of openings")]/following-sibling::div[1]/text()').get().strip()
        if(applicants == "Be an early applicant") :
            applicants = "NULL"
        else :
            applicants = applicants.split(' ')[0]   

        data = {
            "Internship Name" : response.meta["Internship Name"],
            "Internship Details Page Link" : response.meta["Internship Details Page Link"],
            "Internship Organization" : response.meta["Internship Organization"],
            "Internship Organization Page Link" : response.meta["Internship Organization Page Link"],
            "Location Of Internship" : response.meta["Location Of Internship"],
            "Start Date Of Internship" : response.meta["Start Date Of Internship"],
            "Duration" : response.meta["Duration"],
            "Stipend" : response.meta["Stipend"],
            "Application Deadline" : response.meta["Application Deadline"],
            'Number of applicants' : applicants,
            'Number of openings' : openings
        }         
        if(self.no_of_internships > 0) :
            self.no_of_internships -= 1
            yield data
        else :
            raise CloseSpider('bandwidth_exceeded')