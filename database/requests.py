from datetime import datetime
import typing as tp

from sqlalchemy.future import select
from sqlalchemy.sql import func

from database.models import async_session, Request


async def set_request(user_id: int, query: str, title: str) -> None:
    async with async_session() as session:
        request: Request = Request(user_id=user_id, query=query, time=datetime.now(), title=title)
        session.add(request)
        await session.commit()


async def get_history(user_id: int, limit: int) -> list[tuple[str, datetime]]:
    async with async_session() as session:
        result: tp.Any = await session.execute(
            select(Request.query, Request.time)
            .where(Request.user_id == user_id)
            .order_by(Request.time.desc())
            .limit(limit=limit)
        )
        history: list[tuple[tp.Any, tp.Any]] = [(row.query, row.time) for row in result.all()]
        return history


async def get_stats(user_id, limit: int) -> list[tuple[str, tp.Any]]:
    async with async_session() as session:
        result: tp.Any = await session.execute(
            select(Request.title, func.count(Request.title).label("count"))
            .where(Request.user_id == user_id)
            .group_by(Request.title)
            .order_by(func.count(Request.title).desc())
            .limit(limit=limit)
        )
        common_titles: list[tuple[str, int]] = [(row.title, row.count) for row in result.all()]
        return common_titles
