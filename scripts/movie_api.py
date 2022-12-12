#!/usr/bin/env python3
"""
provide some functions for talking with tmdb and letterboxd

[x] movie search with fzf
[x] tmdb_id to json movie object
[x] letterboxd to tmdb_id (unused now)
[x] generate note.py markdown string
[x] add search yts
[x] add starting torrent
"""
import os
from typing import Optional
import dotenv
from requests_html import HTMLSession
from pprint import pprint
from iterfzf import iterfzf
from common import fzf_choose
from rutorrent import download_magnet

import requests

dotenv.load_dotenv(override=True)

TMDB_KEY = os.environ.get("TMDB_KEY")


if not TMDB_KEY:
    print("please set TMDB_KEY=... in .env or as environment variable")
    sys.exit(1)

TMDB_DEFAULT_PARAMS = {
    "api_key": TMDB_KEY,
    "language": "en-us",
    # "append_to_response": "credits",
}

SEARCH_ENDPOINT = "https://api.themoviedb.org/3/search/movie"
YTS_HOME = "https://yts.mx/"
YTS_ENDPOINT = f"{YTS_HOME}/api/v2/list_movies.json"


def main():
    while True:
        term = input(f"search {YTS_HOME} for movie: ")
        yts_data = search_yts_for_movie_obj(term)
        if yts_data:
            break
    torrent_url = choose_torrent(yts_data)
    print(f"{torrent_url=}")
    download_magnet(torrent_url)


def search_yts_for_movie_obj(search_term: str) -> Optional[dict]:
    print(f"{search_term=}")
    search_params = dict(
        query_term=search_term,
    )
    resp = requests.get(YTS_ENDPOINT, params=search_params)
    if not resp.ok:
        print(f"bad yts response {resp.status_code=}")
        return None
    y = resp.json()
    if y["data"]["movie_count"] <= 0:
        print(f"no movies found {search_term=}")
        return None
    movies = y["data"]["movies"]
    movie = fzf_choose(movies, lambda x: x["title_long"])
    pprint(movie)
    return movie


def choose_torrent(yts_movie: dict) -> str:
    movie = yts_movie
    torrent_url = fzf_choose(
        movie["torrents"],
        lambda t: f"{t['quality']=} {t['seeds']=} {t['size']=} {t['type']}",
        lambda t: t["url"],
    )
    return torrent_url


def search_to_template(query, num_actors=5):
    "main entrypoint. search a query and return a markdown template"
    t_id = search_movie_title_for_id(query)
    movie = get_tmdb_json(t_id, add_credits=True)
    movie_str = movie2trim(movie, add_kevbot_link=True)
    cast_str = movie2cast(movie, num_actors)
    out = f"== {movie_str}\n\n"
    out += f"=== Themes\n\n"
    out += f"=== Characters\n\n"
    out += f"{cast_str}\n\n"
    out += f"=== Memorable Parts\n\n"
    out += f"=== Reminded of\n\n"
    return out


def movie2trim(movie, add_kevbot_link=False):
    "return a string like `The Dark Knight (2008)`"
    title = movie.get("title", "")
    release_year = movie.get("release_date", "0000").split("-")[0]
    out = f"{title} ({release_year})"
    if add_kevbot_link:
        out += f"\nhttps://movies.kevbot.xyz/?m={movie['id']}"
    return out


def movie2cast(movie, num_actors=5):
    "return a string of the first N actors"
    if "credits" not in movie or "cast" not in movie["credits"]:
        print("no cast")
        return ""
    actor_titles = []
    for cast_member in movie["credits"]["cast"][:num_actors]:
        # name, character
        out = f".{cast_member.get('name')} as {cast_member.get('character')}"
        actor_titles.append(out)
    return "\n\n".join(actor_titles)


def letterboxd_to_tmdb_id(url):
    html_session = HTMLSession()
    r = html_session.get(url)
    out = r.html.find('a[data-track-action="TMDb"]', first=True)
    t_url = out.attrs["href"]
    t_id = t_url.split("/")[-2]
    return t_id


def id2url(tmdb_id, letterboxd=False):
    "tmdb_id -> link to tmdb page or letterboxd"
    if letterboxd:
        url = f"https://letterboxd.com/tmdb/{tmdb_id}"
    else:
        url = f"https://www.themoviedb.org/movie/{tmdb_id}"
    return url


def search_movie_title_for_id(query=None):
    "search a movie title, interactively choose one, and return its tmdb_id"
    if query is None:
        query = input("query:")
    params = TMDB_DEFAULT_PARAMS.copy()
    params["query"] = query
    r = requests.get(SEARCH_ENDPOINT, params=params)

    all_movies = r.json()["results"]
    choices = []
    for movie in all_movies:
        temp = movie.get("title")
        temp += " (" + movie.get("release_date", "").split("-")[0] + ")"
        temp += f" {movie.get('id')}"
        choices.append(temp)
    choice = iterfzf(choices)
    choice_id = int(choice.split(" ")[-1])
    return choice_id


def get_tmdb_json(movie_id, add_credits=False):
    tmdb_movie_api_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    # tmdb_movie_api_url = "https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_key}&language=en-us&append_to_response=credits"
    params = TMDB_DEFAULT_PARAMS.copy()
    if add_credits:
        params["append_to_response"] = "credits"
    r = requests.get(tmdb_movie_api_url, params=params)
    return r.json()


if __name__ == "__main__":
    main()
