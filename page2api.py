import requests
import json

zillow_sold_url = 'https://www.zillow.com/jacksonville-fl-postal_code/sold/?searchQueryState={"pagination":{},"usersSearchTerm":"postal_code","mapZoom":12,"isMapVisible":true,"filterState":{"pool":{"value":true},"sort":{"value":"globalrelevanceex"},"rs":{"value":true},"fsba":{"value":false},"fsbo":{"value":false},"nc":{"value":false},"cmsn":{"value":false},"auc":{"value":false},"fore":{"value":false}},"isListVisible":true}'

url = zillow_sold_url.replace("postal_code", "32218")
print(url)
api_url = "https://www.page2api.com/api/v1/scrape"
payload = {
    "api_key": "eb25710b64c8047831e0ebc4a40ff66eeb272277",
    "url": url,
    "real_browser": True,
    "merge_loops": True,
    "premium_proxy": "de",
    "scenario": [
        {
            "loop": [
                {"wait_for": "article.list-card"},
                {"execute_js": "var articles = document.querySelectorAll('article')"},
                {
                    "execute_js": "articles[Math.round(articles.length/8)].scrollIntoView({behavior: 'smooth'})"
                },
                {"wait": 2},
                {
                    "execute_js": "articles[Math.round(articles.length/6)].scrollIntoView({behavior: 'smooth'})"
                },
                {"wait": 2},
                {
                    "execute_js": "articles[Math.round(articles.length/4)].scrollIntoView({behavior: 'smooth'})"
                },
                {"wait": 2},
                {
                    "execute_js": "articles[Math.round(articles.length/2)].scrollIntoView({behavior: 'smooth'})"
                },
                {"wait": 2},
                {
                    "execute_js": "articles[Math.round(articles.length/1.5)].scrollIntoView({behavior: 'smooth'})"
                },
                {"wait": 2},
                {"execute": "parse"},
                {
                    "execute_js": "var next = document.querySelector('.search-pagination a[rel=next]'); if(next){ next.click() }"
                },
            ],
            "stop_condition": "var next = document.querySelector('.search-pagination a[rel=next]'); next === null || next.getAttributeNames().includes('disabled')",
        }
    ],
    "parse": {
        "properties": [
            {
                "_parent": "article.list-card",
                "price": ".list-card-price >> text",
                "url": "a >> href",
                "bedrooms": "ul.list-card-details li:nth-child(1) >> text",
                "bathrooms": "ul.list-card-details li:nth-child(2) >> text",
                "living_area": "ul.list-card-details li:nth-child(3) >> text",
                "status": "ul.list-card-details li:nth-child(4) >> text",
                "address": "a address.list-card-addr >> text",
            }
        ]
    },
}

headers = {"Content-type": "application/json", "Accept": "text/plain"}
response = requests.post(api_url, data=json.dumps(payload), headers=headers)
result = json.loads(response.text)


with open("test18.json", "a") as jspn_file:
    json.dump(response.json(), jspn_file)
