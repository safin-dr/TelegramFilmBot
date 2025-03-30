import re
import typing as tp

import aiohttp
from web.storage_classes import Movie


def normalize(data: str) -> str:
    """
    Converts string to lowercase,
    removes special characters and collapses whitespaces
    :param data: The input string to be normalized
    :return: normalized string
    """
    data = re.sub(r"[^\w\s_]", "", data.lower())
    data = re.sub(r"[\s_]+", " ", data.strip())
    return data


def get_movie_string(movie: Movie) -> str:
    """
    Generate text with movie's information that our bot will send to the user
    :param movie: Movie information data
    :return: string displaying movie's information
    """
    return (
        f"😎 {movie.name} 😎 \n"
        + "\n🤯 Жанр: " + ", ".join([f"{genre}" for genre in movie.genres])
        + f"\n🤩 Рейтинг на Кинопоиске: {movie.rating:.1f}"
        + f"\n👾 Описание: {movie.description}"
        + f"\n▶️ Ссылка на просмотр: {movie.main_link}"
        + f"\n💅 Ещё одна ссылка: {movie.second_link}"
    )


def get_extra_links(movie: Movie) -> str:
    """
    Generate text with movie's extra links
    :param movie: Movie information data
    :return: string displaying extra links
    """
    return (
        "🆘 Совсем запасные ссылки жесть (на случай блокировки основных):"
        + f"\n1️⃣{movie.reserve_link1}"
        + f"\n2️⃣{movie.reserve_link2}"
        + f"\n3️⃣{movie.reserve_link3}"
    )


def choose_apropriate_description(short_description: str,
                                  full_description: str) -> str:
    """
    Choose an appropriate movie description to fit
    within the character limit of a Telegram message

    This function first checks if a short description
    is provided. If it's available and within the character limit,
    it's returned. Otherwise, it considers the full description
    and truncates it to fit within the character limit
    without splitting words

    :param short_description: A short movie description
    :param full_description: A full movie description
    :return: An appropriate movie description that fits
    within the character limit
    """
    returned_description: str = short_description if short_description else full_description
    if len(returned_description) < 800:
        return returned_description
    else:
        last_space_index = returned_description.find(". ", 500, 750)
        return returned_description[:last_space_index] + "<TLDR...>"


async def choose_apropriate_picture(session: aiohttp.ClientSession,
                                    poster_url: str | None,
                                    backdrop_url: str | None) -> tp.Optional[str]:
    """
    Choose an appropriate picture URL between the poster and backdrop URLs based on their file size.
    This function checks the content length of both URLs and returns the poster URL if its file size is smaller than
    or equal to 7 MB. Otherwise, it returns the backdrop URL.

    :param poster_url: The URL of the movie's poster image
    :param backdrop_url: The URL of the movie's backdrop image
    :return: The selected image URL (poster or backdrop) based on file size
    """
    if not poster_url and not backdrop_url:
        return None
    async with session.head(poster_url) as response:
        content_length: str | None = response.headers.get("Content-Length")
        if content_length is not None:
            return poster_url if int(content_length) <= 7345728 else backdrop_url
        return None
