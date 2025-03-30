import os
import typing as tp

import aiohttp
from bs4 import BeautifulSoup

from web.storage_classes import Movie
from telegram.utils import normalize, choose_apropriate_description, choose_apropriate_picture


headers = {"X-API-KEY": os.environ["KP_API_TOKEN"]}


async def get_movie_info_by_name(session: aiohttp.ClientSession, name: str) -> tp.Optional[Movie]:
    """
    Get movie information by name with async HTTP request to the Kinopoisk API
    :param name: The name of the movie to search for
    :return: A Movie object containing information about the movie if found
    """
    query: str = normalize(name)
    params: dict[str, str] = {"query": query}
    async with session.get("https://api.kinopoisk.dev/v1.4/movie/search",
                           headers=headers,
                           params=params
                           ) as response:
        if response.status == 200:
            data: tp.Any = await response.json()
            try:
                required_info: tp.Any = data["docs"][0]
                if required_info["name"]:
                    return Movie(name=required_info["name"],
                                 eng_name=required_info["alternativeName"],
                                 genres=[genre["name"] for genre in required_info["genres"]],
                                 rating=required_info["rating"]["kp"],
                                 description=choose_apropriate_description(
                                     required_info["shortDescription"],
                                     required_info["description"],
                                 ),
                                 picture_url=await choose_apropriate_picture(
                                     session,
                                     required_info["poster"]["url"],
                                     required_info["backdrop"]["url"],
                                 ),
                                 main_link="Ссылка пока не найдена",
                                 second_link="Ссылка пока не найдена",
                                 reserve_link1="Ссылка пока не найдена",
                                 reserve_link2="",
                                 reserve_link3="")
            except IndexError:
                pass
        return None


async def async_fetch(session: aiohttp.ClientSession, query: str) -> str:
    """
    Asyncronously fetch (get-request) single url using provided session
    :param session: aiohttp session object
    :param url: target http url
    :return: fetched text
    """
    headers: dict[str, str] = {
        'user-agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36'
        )
    }
    url: str = "https://www.google.com/search?q={" + str(query) + "}%20смотреть%20онлайн"
    async with session.get(url, headers=headers) as response:
        text = await response.text()
    return text


async def get_movie_google_links_by_name(session: aiohttp.ClientSession, name: str, limit: int = 5) -> list[str]:
    """
    Get the Google search link for watching a movie online by its name.

    This function performs a Google search with the specified movie name to find a link for watching the movie online.

    :param session: An aiohttp ClientSession for making HTTP requests.
    :param name: The name of the movie to search for.
    :return: A first Google search result link for watching the movie online.
    """
    html: tp.Any = await async_fetch(session=session, query=name)
    links: list[str] = []
    for paragraph in BeautifulSoup(html, 'html.parser').find_all('a', href=True):
        if len(links) == limit:
            break
        if (paragraph.get('data-jsarwt') == "1") and (paragraph.get('data-ved')[-3:] == 'QAQ'):
            links.append(paragraph.get('href'))
    return links
