from aiohttp import web
from bs4 import BeautifulSoup
import httpx
import re


class Proxy:
    def __init__(self, original_domain, proxy_domain):
        self.original_domain = original_domain
        self.proxy_domain = proxy_domain

    @staticmethod
    def add_trademark(document: str) -> str:
        """Adds ™ sign to every six letters word in the text of the HTML document"""

        six_letters_word = re.compile(r"\b\w{6}\b")

        soup = BeautifulSoup(document, features="lxml")
        word_elements = soup.find_all(text=six_letters_word)
        for el in word_elements:
            new_text = str(el)
            word = six_letters_word.search(new_text)
            while word:
                end_of_word = word.end()
                new_text = new_text[:end_of_word] + "™" + new_text[end_of_word:]
                word = six_letters_word.search(new_text, pos=end_of_word)
            el.replace_with(new_text)

        return str(soup)

    async def proxify(self, request):
        # getting original page or file
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.original_domain + str(request.rel_url),
                headers=dict(request.headers),
            )

        content_type_header = response.headers.get("content-type")
        expires_header = response.headers.get("expires")

        # removing charset info, leaving only content type
        content_type = content_type_header.split(";")[0] if content_type_header else None

        if "text" not in content_type:
            return web.Response(
                body=response.content,
                content_type=content_type,
                headers={"Expires": expires_header},
            )

        document = response.text.replace(self.original_domain, self.proxy_domain)

        if "html" in content_type:
            document = self.add_trademark(document)

        return web.Response(text=document, content_type=content_type)


def main():
    host = "127.0.0.1"
    port = 8000

    hacker_news = Proxy("https://news.ycombinator.com", f"http://{host}:{port}")
    app = web.Application()
    app.router.add_get("/{path:.*}", hacker_news.proxify)

    web.run_app(app, host=host, port=port, access_log=None)


if __name__ == "__main__":
    main()
