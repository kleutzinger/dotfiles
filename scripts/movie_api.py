#!/usr/bin/env python3
"""
provide some functions for talking with tmdb and letterboxd

[x] movie search with fzf
[x] tmdb_id to json movie object
[x] letterboxd to tmdb_id (unused now)
[x] generate note.py markdown string
[x] add search yts
[x] add starting torrent
[x] random movie from watchlist
"""
import os
from typing import Optional
import dotenv
from pprint import pprint
from iterfzf import iterfzf
from common import fzf_choose, get_url
from rutorrent import download_magnet

import requests

dotenv.load_dotenv(override=True)

TMDB_KEY = os.environ.get("TMDB_KEY")


if not TMDB_KEY:
    print("please set TMDB_KEY=... in .env or as environment variable")

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
        print(f"search {YTS_HOME} for movie to download")
        print(f"leave empty to choose random movie from watchlist")
        term = input("> ")
        if term == "":
            yts_data = get_random_watchlist_movie(num_choices=3)
        else:
            yts_data = search_yts_for_movie_obj(term)
        if yts_data is not None:
            break
    torrent_url = choose_torrent_quality(yts_data)
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
    if len(movies) > 1:
        movie = fzf_choose(movies, lambda x: x["title_long"])
    else:
        movie = movies[0]
    pprint(movie)
    return movie


def choose_torrent_quality(yts_movie_options: dict) -> str:
    """
    choose a single torrent url from yts quality options such as:
        2 t['quality']='720p' t['seeds']=30 t['size']='908.63 MB' bluray
        1 t['quality']='3D' t['seeds']=4 t['size']='1.88 GB' bluray
        0 t['quality']='1080p' t['seeds']=54 t['size']='1.88 GB' bluray
    """
    movie = yts_movie_options
    is1080 = lambda t: "1080" in t["quality"]
    torrent_url = fzf_choose(
        # we want 1080p movies to show up first
        list(sorted(movie["torrents"], key=is1080, reverse=True)),
        display_func=lambda t: f"{t['quality']:8} {t['type']:8} ({t['size']}, seeds={t['seeds']})",
        output_func=lambda t: t["url"],
        prompt=movie["title_long"] + " >"
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
    req = get_url(url)
    out = req.html.find('a[data-track-action="TMDb"]', first=True)
    t_url = out.attrs["href"]
    t_id = t_url.split("/")[-2]
    return t_id


def tmdb_id_to_imdb_id(tmdb_id: str) -> str:
    tmdb = get_tmdb_json(tmdb_id)
    return tmdb["imdb_id"]


def get_random_watchlist_movie(num_choices: int) -> Optional[dict]:
    "get a random movie from my watchlist"
    print("getting thedookmaster's watchlist...")
    url = "https://letterboxd.com/thedookmaster/watchlist/by/shuffle/"
    req = get_url(url, execute_js=True)
    links = req.html.links
    movie_links = list(filter(lambda l: "/film/" in l, links))[:num_choices]
    print(list(movie_links))
    link_choice = fzf_choose(movie_links)
    tmdb_id = letterboxd_to_tmdb_id("https://letterboxd.com" + link_choice)
    imdb_id = tmdb_id_to_imdb_id(tmdb_id)
    movie = search_yts_for_movie_obj(imdb_id)
    return movie


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
    print(f"fetching {movie_id=} from api.themoviedb.org")
    tmdb_movie_api_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    # tmdb_movie_api_url = "https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_key}&language=en-us&append_to_response=credits"
    params = TMDB_DEFAULT_PARAMS.copy()
    if add_credits:
        params["append_to_response"] = "credits"
    r = requests.get(tmdb_movie_api_url, params=params)
    return r.json()


if __name__ == "__main__":
    main()
