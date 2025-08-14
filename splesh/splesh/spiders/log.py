import scrapy
# from ..items import SpleshItem
import base64

from scrapy_splash import SplashRequest

lua_script = """
function main(splash, args)
    splash:init_cookies(splash.args.cookies)
    assert(splash:go(args.url))
    splash:set_viewport_full()
    splash:wait(1)
    local username = splash:select('input[name=username]')
    username:mouse_click()
    splash:send_text('foobar')
    splash:wait(1)
    local password  = splash:select('input[name=password]')
    password:mouse_click()
    splash:send_text('foobar')
    splash:wait(1)
    
    local loging = splash:select('input[value=Login]')
    loging:mouse_click()
    splash:wait(1)
    
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


class LogSpider(scrapy.Spider):
    name = "log"

    def start_requests(self):
        url = 'https://quotes.toscrape.com/login'
        yield SplashRequest(
            url = url,
            callback=self.parse,
            endpoint='execute',
            args={
                'width': 1000,
                'lua_source': lua_script,
            })

    def parse(self, response):
        print("!!!")
        print(str(response.data.get("url")))
        png_base64 = response.data.get("png")
        if png_base64:
            png_bytes = base64.b64decode(png_base64)
            with open("screen.png", "wb") as f:
                f.write(png_bytes)

