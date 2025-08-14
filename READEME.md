# Test how work splash-scrapy

### First site OLX
https://www.olx.ua/uk/
### Second site 
https://quotes.toscrape.com

# Start work with splash

### Need install in docker

```
sudo docker pull scrapinghub/splash
```

### Start server

```
sudo docker run -it -p 8050:8050 --rm scrapinghub/splash
```

### Run

```
curl 'http://localhost:8050/render.html?url=https://quotes.toscrape.com/js/'
```

## setting.py

```python
# Splash Server Endpoint
SPLASH_URL = 'http://localhost:8050'


# Enable Splash downloader middleware and change HttpCompressionMiddleware priority
DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Enable Splash Deduplicate Args Filter
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

# Define the Splash DupeFilter
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
```

---

# How make a Screenshot

## First variable

```python
import scrapy
from scrapy_splash import SplashRequest
import base64

class AccountSpider(scrapy.Spider):
    name = "account"

    def start_requests(self):
        url = "http://www.olx.ua"
        yield SplashRequest(
            url,
            callback = self.parse,
            endpoint = 'render.json',
            args = {
                'wait': 2,
                'html' : 1,
                'png' : 1,
                'width' : 1000,
                })

def parse(self, response):
    print("work")
    imgdata = base64.b64decode(response.data['png'])
    filename = 'some_image.png'
    with open(filename, 'wb') as f:
        f.write(imgdata)
```

## Second variable

```python
import scrapy
from scrapy_splash import SplashRequest
import base64

lua_script = """

function main(splash, args)
  splash:set_user_agent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
  splash.images_enabled = true
  -- splash.private_mode_enabled = false

  assert(splash:go(args.url))
  splash:wait(2)

  -- Scroll multiple times
  for i = 1, 2, 1 do
    splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
    splash:wait(2)  -- wait for new content
  end

  return {
    html = splash:html(),
    png = splash:png(),  -- optional screenshot
  }
end
"""


class AccountSpider(scrapy.Spider):
    name = "account"
    #allowed_domains = ["www.olx.ua"]
    #start_urls = ["http://www.olx.ua/uk/account/?ref[0][params][url]=http%3A%2F%2Fwww.olx.ua%2Fuk%2F&ref[0][action]=redirector&ref[0][method]=index"]

    def start_requests(self):
        url = "http://www.olx.ua"
        yield SplashRequest(
            url,
            callback = self.parse,
            endpoint='execute',
            args = {
                'lua_source': lua_script,
                'html' : 1,
                'width' : 1000,
            })

    def parse(self, response):
        png_base64 = response.data.get("png")
        if png_base64:
            png_bytes = base64.b64decode(png_base64)
            with open("screenshot.png", "wb") as f:
                f.write(png_bytes)
```

---

# Get data Lua

```lua
lua_script = """

function main(splash, args)
    splash:set_user_agent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")

    assert(splash:go(args.url))
    splash:wait(2)

    -- Scroll multiple times
    for i = 1, 2, 1 do
        -- splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
        splash:runjs("window.scrollTo(0, document.body.scrollHeight-2000);")
        splash:wait(2)  -- wait for new content
        end
    return {
        html = splash:html(),
        png = splash:png(),  -- optional screenshot
    }
end
"""
```

---

# Click on button

```python
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
        png_base64 = response.data.get("png")
        if png_base64:
            png_bytes = base64.b64decode(png_base64)
            with open("screenshot.png", "wb") as f:
                f.write(png_bytes)
```

---

# Write text

```python
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
```


