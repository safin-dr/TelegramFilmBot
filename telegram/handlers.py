import typing as tp

from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import aiohttp

import telegram.keyboard as kb
import database.requests as rq
from telegram.utils import get_movie_string, get_extra_links
from web.http_operations import get_movie_info_by_name, get_movie_google_links_by_name
from web.storage_classes import Movie


router: Router = Router()


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer(f"Добрый день, уважаемый {message.from_user.first_name}!\n\n Что интересует сегодня?",
                         reply_markup=kb.main, parse_mode="Markdown")


@router.message(F.text == 'Помощь')
async def text_help(message: Message) -> None:
    await command_help(message)


@router.message(Command("help"))
async def command_help(message: Message) -> None:
    await message.reply("Вы обратились за помощью, это уже большой шаг! Я умею: \n \
                        \n🤓👉 Серфить интернет в поисках желаемого фильма или сериала названию, \n \
                        \n😈🤌 Выдавать историю Ваших последних запросов по команде '/history', \n \
                        \n🤖🤙 Выдавать статистику Ваших последних запросов по команде '/stats'",
                        reply_markup=kb.help_buttons,
                        parse_mode="Markdown")


@router.callback_query(F.data == 'search')
async def callback_search(callback: CallbackQuery) -> None:
    await callback.answer('Введите название желаемого фильма.')


@router.callback_query(F.data == 'history')
async def callback_history(callback: CallbackQuery) -> None:
    await callback.answer("Это был пранк inline клавиатурой, для просмотра истории запросов нажмите '/history'.")


@router.callback_query(F.data == 'stats')
async def callback_stats(callback: CallbackQuery) -> None:
    await callback.answer("Это был пранк inline клавиатурой, для просмотра статистики запросов нажмите '/stats'.")


@router.message(F.text == 'Моя история')
async def text_history(message: Message) -> None:
    await command_history(message)


@router.message(Command("history"))
async def command_history(message: Message) -> None:
    await message.reply("Ваша история наверняка очень глубокая и интересная!")
    history: str = "Вот что могу сказать по последним запросам: \n"
    history_lines: list[tuple[str, tp.Any]] = await rq.get_history(message.from_user.id, 20)
    for line in history_lines:
        history += "\n🛜Запрос:  " + str(line[0]) + "\n⏰ Время запроса:  " + str(line[1]) + "\n"
    await message.answer(history)


@router.message(F.text == 'Моя статистика')
async def text_stats(message: Message) -> None:
    await command_stats(message)


@router.message(Command("stats"))
async def command_stats(message: Message) -> None:
    await message.reply("По статистике каждый второй является ботом. Чур я не бот")
    history: str = "Вот что могу сказать по статистике Ваших последних запросов: \n"
    history_lines = await rq.get_stats(message.from_user.id, 30)
    for line in history_lines:
        history += "\n🎥 Фильм:  " + str(line[0]) + "\n❓ Запрашивался "
        if (line[1] % 10 in {2, 3, 4}):
            history += str(line[1]) + " раза \n"
        else:
            history += str(line[1]) + " раз \n"
    await message.answer(history)


@router.message(Command("search"))
async def text_search(message: Message) -> None:
    await search_mode(message)


@router.message(F.text == "Поиск фильма, сериала")
async def search_mode(message: Message) -> None:
    await message.answer('Что будем искать?')


@router.message()
async def get_movie_responce(message: Message) -> None:
    async with aiohttp.ClientSession() as session:
        movie: Movie = await get_movie_info_by_name(session=session, name=message.text)
        if movie is not None:
            await rq.set_request(user_id=message.from_user.id, query=message.text, title=movie.name)
            links: list[str] = await get_movie_google_links_by_name(session=session, name=message.text)
            movie.main_link = links[0]
            if links[1]:
                movie.second_link = links[1]
            if links[2]:
                movie.reserve_link1 = links[2]
            if links[3]:
                movie.reserve_link2 = links[3]
            if links[4]:
                movie.reserve_link3 = links[4]
            if movie.picture_url:
                await message.reply_photo(types.URLInputFile(movie.picture_url), caption=get_movie_string(movie))
            else:
                await message.reply(get_movie_string(movie))
            await message.answer(get_extra_links(movie))
        else:
            await message.reply("К сожалению, мне не удалось выполнить Ваш запрос 😭😭😭")
