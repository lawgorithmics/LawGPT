import scrapy
from bs4 import BeautifulSoup
from furl import furl
import json

class PeraturanSpider(scrapy.Spider):
    name = "Peraturan.go.id"

    async def start(self):
        urls = [
            "https://peraturan.go.id/cari?PeraturanSearch%5Btentang%5D=&PeraturanSearch%5Bnomor%5D=&PeraturanSearch%5Btahun%5D=&PeraturanSearch%5Bjenis_peraturan_id%5D=3&PeraturanSearch%5Bpemrakarsa_id%5D=&PeraturanSearch%5Bstatus%5D=Berlaku&page=1"
        ]

        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )
            
    
    def parse(self, response):
        parsed_html = BeautifulSoup(response.body, 'lxml')
        links = parsed_html.find_all("a", href=True)
        count_peraturan = 0
        for link in links:
            if "id/" in link["href"]:
                count_peraturan += 1
                if "#" in link["href"]:
                    continue

                href = link["href"][3:]
                yield {
                    "url": f"https://peraturan.go.id/files{href}.pdf"
                }
        
        if not count_peraturan:
            # means this page is empty
            return
        
        # otherwise go to next page
        f_url = furl(response.request.url)
        current_page = int(f_url.args["page"])
        next_page = current_page + 1
        f_url.args["page"] = str(next_page)
        # recursively go
        yield scrapy.Request(
            url=f_url.url,
            callback=self.parse
        )
