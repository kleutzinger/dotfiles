#!/usr/bin/env -S uv run --script --with requests,click

import os
import json
import requests
import click
from typing import TypedDict, List
from common import fzf_choose

API_KEY = os.getenv("START_GG_API_KEY")
if not API_KEY:
    raise ValueError("START_GG_API_KEY environment variable is required")


class Bracket(TypedDict):
    title: str
    VODs: List[str]
    BracketUrl: str
    Date: str


"""
example response from
https://tril.kevbot.xyz/custom/brackets

[
  {
    "title": "Get On My Level: Forever - Canadian Fighting Game Championships",
    "VODs": [],
    "BracketUrl": "https://www.start.gg/tournament/get-on-my-level-forever-canadian-fighting-game-championships/event/super-smash-bros-melee-singles",
    "Date": "2025-07-05"
    "relativeDate": "X days ago"
  }, ...
]

"""


def url2slug(url: str) -> str:
    path_segments = [segment for segment in url.split("/") if segment]
    i = path_segments.index("tournament")
    return "/".join(path_segments[i : i + 4])


def get_brackets() -> List[Bracket]:
    """Fetch brackets from the API"""
    return requests.get("https://tril.kevbot.xyz/custom/brackets").json()


def get_entrants(slug: str, num: int = 100):
    """Fetch entrants from start.gg API"""
    query = """
    query GetEventSeeds($slug: String!, $num: Int!) {
        event(slug: $slug) {
            id
            name
            phases {
                seeds(query: {
                    page: 1
                    perPage: $num
                }) {
                    nodes {
                        seedNum
                        entrant {
                            name
                        }
                    }
                }
            }
        }
    }
    """

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    response = requests.post(
        "https://api.start.gg/gql/alpha",
        json={"query": query, "variables": {"slug": slug, "num": num}},
        headers=headers,
    )

    if response.status_code != 200:
        click.echo(f"Error: {response.status_code}", err=True)
        click.echo(response.text, err=True)
        raise click.Abort()

    data = response.json()
    if "errors" in data:
        click.echo("GraphQL Errors:", err=True)
        for error in data["errors"]:
            click.echo(error["message"], err=True)
        raise click.Abort()

    return data["data"]["event"]


@click.group()
def cli():
    """Bracket information tool"""
    pass


def choose_bracket() -> Bracket:
    """Choose a bracket from the available ones"""
    brackets = get_brackets()
    chosen = fzf_choose(
        brackets, display_func=lambda x: f"{x.get('title')}{x.get('relativeDate')}"
    )
    return chosen


@cli.command()
def bracket() -> Bracket:
    """List available brackets, choose one"""
    click.echo(json.dumps(choose_bracket(), indent=2))
    return Bracket


@cli.command()
@click.option("--bracket", help="URL or slug of the bracket")
@click.option(
    "--num", default=100, help="Number of seeds to fetch (default: 100, max: 512)"
)
def entrants(bracket, num):
    if num > 512:
        click.echo("Error: --num cannot exceed 512", err=True)
        raise click.Abort()
    """Get entrants for a bracket"""
    if bracket:
        # If it's a URL, convert to slug
        if bracket.startswith("http"):
            slug = url2slug(bracket)
        else:
            slug = bracket
    else:
        chosen = choose_bracket()
        slug = url2slug(chosen["BracketUrl"])

    event = get_entrants(slug, num)
    click.echo(f"\nEvent: {event['name']}")

    # Get seeds from the first phase
    if event["phases"] and event["phases"][0]["seeds"]["nodes"]:
        seeds = event["phases"][0]["seeds"]["nodes"]
        click.echo(f"Tournament: https://start.gg/{slug}")
        click.echo(f"Total Seeds: {len(seeds)}")
        click.echo("\nSeeds (ordered by seed number):")
        # Sort by seed number
        sorted_seeds = sorted(seeds, key=lambda x: x["seedNum"])
        for seed in sorted_seeds:
            name = seed["entrant"]["name"]
            # Split name on | and take the right part if it exists, otherwise keep full name
            name = name.split(" | ")[-1]
            click.echo(f"{seed['seedNum']:03d} - {name}")
    else:
        click.echo("No seeds found for this event.")


if __name__ == "__main__":
    cli()
