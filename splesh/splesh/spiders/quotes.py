import scrapy
#from ..items import SpleshItem
import base64

from scrapy_splash import SplashRequest

lua_script = """
function main(splash, args)
    assert(splash:go(args.url))
    
    for i = 1, 9, 1 do 
        local new_page = splash:select('body > div > nav > ul > li.next > a')
        assert(new_page:mouse_click())
        assert(splash:wait(1))
        end
     
    return {
        url = splash:url(),
        html = splash:html(),
        png  = splash:png(),
    }
end
"""

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    def start_requests(self):
        url = 'https://quotes.toscrape.com/js/'
        yield SplashRequest(
            url,
            callback=self.parse,
            endpoint='execute',
            args={
                'wait': 2,
                'lua_source': lua_script,
                'html': 1,
                'width': 1000,
                'url' : 'https://quotes.toscrape.com/js/'
            })

    def parse(self, response):
        print("!!!")
        print(str(response.data.get("url")))
        png_base64 = response.data.get("png")
        if png_base64:
            png_bytes = base64.b64decode(png_base64)
            with open("screenshot.png", "wb") as f:
                f.write(png_bytes)

