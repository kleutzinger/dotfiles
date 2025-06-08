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
    "title": "Unranked",
    "VODs": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    "BracketUrl": "https://www.start.gg/tournament/unranked/event/melee-singles",
    "Date": "2025-07-19"
  },
  {
    "title": "Get On My Level: Forever - Canadian Fighting Game Championships",
    "VODs": [],
    "BracketUrl": "https://www.start.gg/tournament/get-on-my-level-forever-canadian-fighting-game-championships/event/super-smash-bros-melee-singles",
    "Date": "2025-07-05"
  }, ...

"""


def url2slug(url: str) -> str:
    path_segments = [segment for segment in url.split("/") if segment]
    i = path_segments.index("tournament")
    return "/".join(path_segments[i : i + 4])


def get_brackets() -> List[Bracket]:
    """Fetch brackets from the API"""
    return requests.get("https://tril.kevbot.xyz/custom/brackets").json()


def get_entrants(slug: str):
    """Fetch entrants from start.gg API"""
    query = """
    query EventEntrants($slug: String!) {
      event(slug: $slug) {
        id
        name
        entrants(query: {
          page: 1
          perPage: 100
        }) {
          pageInfo {
            total
            totalPages
          }
          nodes {
            id
            participants {
              id
              gamerTag
            }
          }
        }
      }
    }
    """

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    response = requests.post(
        "https://api.start.gg/gql/alpha",
        json={"query": query, "variables": {"slug": slug}},
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


@cli.command()
def bracket() -> Bracket:
    """List available brackets, choose one"""
    brackets = get_brackets()
    chosen = fzf_choose(brackets, display_func=lambda x: x["title"])
    click.echo(json.dumps(chosen, indent=2))
    return Bracket


@cli.command()
@click.option("--bracket", help="URL or slug of the bracket")
def entrants(bracket):
    """Get entrants for a bracket"""
    if bracket:
        # If it's a URL, convert to slug
        if bracket.startswith("http"):
            slug = url2slug(bracket)
        else:
            slug = bracket
    else:
        # Choose from available brackets
        brackets = get_brackets()
        chosen = fzf_choose(brackets, display_func=lambda x: x["title"])
        slug = url2slug(chosen["BracketUrl"])

    event = get_entrants(slug)
    click.echo(f"\nEvent: {event['name']}")
    click.echo(f"Total Entrants: {event['entrants']['pageInfo']['total']}")
    click.echo("\nEntrants:")
    for entrant in event["entrants"]["nodes"]:
        for participant in entrant["participants"]:
            click.echo(f"- {participant['gamerTag']}")


if __name__ == "__main__":
    cli()
