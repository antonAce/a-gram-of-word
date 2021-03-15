import aiohttp
import logging
from lxml import html


class CitizendiumIndexer:
    domain = 'https://en.citizendium.org'
    link_weight = 0.3

    def __query_scheme__(self, topic) -> str:
        query_topic = topic.replace(' ', '+')
        return f"{self.domain}/wiki?title=Special%3ASearch&profile=default&search={query_topic}&fulltext=Search"

    def __extract__(self, document: html.HtmlElement, weight: float) -> list:
        try:
            search_results = document.cssselect('ul.mw-search-results li')
            return [{
                'title': result.cssselect('div.mw-search-result-heading a')[0].text_content(),
                'href': self.domain + result.cssselect('div.mw-search-result-heading a')[0].attrib['href'],
                'weight': weight
            } for result in search_results]
        except Exception as ex:
            logging.error(ex)
            return []

    async def index(self, topic) -> list:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__query_scheme__(topic)) as response:
                document = html.fromstring(await response.text())
                links = self.__extract__(document, self.link_weight)

        return links


class EveripediaIndexer:
    domain = 'https://everipedia.org'
    link_weight = 0.3

    async def index(self, topic) -> list:
        request_body = {
            "query": topic,
            "langs": ["en"],
            "offset": 0,
            "filters": ["article", "category", "profile"]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.everipedia.org/v2/search/extended", json=request_body) as response:
                json_response = await response.json()
                articles = json_response['articles']

                links = [{
                    'title': article['page_title'],
                    'href': 'https://everipedia.org/wiki/lang_en/' + article['slug'],
                    'weight': self.link_weight
                } for article in articles]

        return links


class OxfordreIndexer:
    domain = 'https://oxfordre.com'
    link_weight = 0.4

    def __query_scheme__(self, topic) -> str:
        query_topic = topic.replace(' ', '+')
        return f"{self.domain}/search?q={query_topic}&searchBtn=Search&isQuickSearch=true"

    def __extract__(self, document: html.HtmlElement, weight: float) -> list:
        try:
            search_results = document.cssselect('#searchContent div.contentItem.hasAccess')
            return [{
                'title': result.cssselect('div.title-wrapper a')[0].text_content(),
                'href': self.domain + result.cssselect('div.title-wrapper a')[0].attrib['href'],
                'weight': weight
            } for result in search_results]
        except Exception as ex:
            logging.error(ex)
            return []

    async def index(self, topic) -> list:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__query_scheme__(topic)) as response:
                document = html.fromstring(await response.text())
                links = self.__extract__(document, self.link_weight)

        return links
