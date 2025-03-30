from dataclasses import dataclass


@dataclass
class Movie:
    """
    This dataclass represents information about movie
    """
    name: str
    eng_name: str
    genres: list[str]
    rating: float
    description: str
    picture_url: str
    main_link: str
    second_link: str
    reserve_link1: str
    reserve_link2: str
    reserve_link3: str
