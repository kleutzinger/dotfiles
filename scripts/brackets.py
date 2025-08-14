#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click",
#     "requests",
# ]
# ///

import os
import json
import requests
import click
from typing import TypedDict, List
from common import fzf_choose
from datetime import datetime

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


def get_latest_bracket() -> Bracket:
    """Get the most recent bracket based on date"""
    brackets = get_brackets()
    if not brackets:
        raise click.ClickException("No brackets found")

    # Filter out future brackets and sort by date (most recent first)
    today = datetime.now().date()
    past_brackets = []

    for bracket in brackets:
        try:
            bracket_date = datetime.strptime(bracket.get("Date", ""), "%Y-%m-%d").date()
            if bracket_date <= today:
                past_brackets.append(bracket)
        except (ValueError, TypeError):
            # Skip brackets with invalid dates
            continue

    if not past_brackets:
        raise click.ClickException("No past brackets found")

    # Sort by date (most recent first)
    sorted_brackets = sorted(
        past_brackets, key=lambda x: x.get("Date", ""), reverse=True
    )
    return sorted_brackets[0]


def choose_bracket(latest: bool = False) -> Bracket:
    """Choose a bracket from the available ones"""
    if latest:
        return get_latest_bracket()

    brackets = get_brackets()
    chosen = fzf_choose(
        brackets,
        display_func=lambda x: f"{x.get('relativeDate'):12} - {x.get('title', '')}",
    )
    return chosen


@cli.command()
@click.option("--latest", is_flag=True, help="Choose the most recent bracket")
@click.option("--upload", is_flag=True, help="Upload a new bracket")
def bracket(latest: bool = False, upload: bool = False) -> Bracket:
    """List available brackets, choose one"""
    bracket = choose_bracket(latest=latest)
    if upload:
        bracket_url = bracket.get("BracketUrl")
        vod = bracket["VODs"][0]["url"]
        click.echo(f"vodbackup.py --cleanup --bracket-url {bracket_url} {vod}")
    else:
        click.echo(json.dumps(bracket, indent=2))
    return Bracket


@cli.command()
@click.option("--bracket", help="URL or slug of the bracket")
@click.option("--latest", is_flag=True, help="Choose the most recent bracket")
@click.option(
    "--not-kevbot",
    is_flag=True,
    help="Return just the opponent's name (only works for kevbot sets)",
)
def set(bracket, latest, not_kevbot):
    """List all sets and select one"""
    if bracket:
        # If it's a URL, convert to slug
        if bracket.startswith("http"):
            slug = url2slug(bracket)
        else:
            slug = bracket
    else:
        chosen = choose_bracket(latest=latest)
        slug = url2slug(chosen["BracketUrl"])

    # Update query to focus on entrants
    query = """
        query EventSets($slug: String!) {
            event(slug: $slug) {
                name
                phases {
                    sets {
                        nodes {
                            id
                            round
                            fullRoundText
                            slots {
                                entrant {
                                    name
                                    participants {
                                        gamerTag
                                        user {
                                            id
                                        }
                                    }
                                }
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

    event = data["data"]["event"]
    if not event["phases"]:
        click.echo("No phases found for this event.")
        return

    all_sets = []
    for phase in event["phases"]:
        if phase["sets"]["nodes"]:
            all_sets.extend(phase["sets"]["nodes"])

    if not all_sets:
        click.echo("No sets found for this event.")
        return

    # Format set display strings focusing on entrants
    kevbot_sets = []
    other_sets = []

    for s in all_sets:
        if s["slots"][0]["entrant"] and s["slots"][1]["entrant"]:
            p1 = s["slots"][0]["entrant"]["name"].split(" | ")[-1]
            p2 = s["slots"][1]["entrant"]["name"].split(" | ")[-1]
            round_text = s["fullRoundText"] or f"Round {s['round']}"
            display = f"{round_text}: {p1} vs {p2}"

            # Check if kevbot is in the set
            is_kevbot_set = False
            for slot in s["slots"]:
                for participant in slot["entrant"]["participants"]:
                    if (
                        "kevbot" in participant.get("gamerTag", "").lower()
                        or participant.get("user", {}).get("id") == "658c6a49"
                    ):
                        is_kevbot_set = True
                        break

            if is_kevbot_set:
                kevbot_sets.append((f"[kevbot] {display}", s))
            else:
                other_sets.append((display, s))

    # Combine lists with kevbot sets first, both sorted by round
    kevbot_sets.sort(key=lambda x: x[1]["round"])
    other_sets.sort(key=lambda x: x[1]["round"])
    set_displays = kevbot_sets + other_sets

    # Let user choose a set
    chosen_display, chosen_set = fzf_choose(set_displays, display_func=lambda x: x[0])

    # Handle --not-kevbot flag
    if not_kevbot:
        # Check if this is a kevbot set
        is_kevbot_set = False
        kevbot_slot = None
        opponent_slot = None

        for i, slot in enumerate(chosen_set["slots"]):
            for participant in slot["entrant"]["participants"]:
                if (
                    "kevbot" in participant.get("gamerTag", "").lower()
                    or participant.get("user", {}).get("id") == "658c6a49"
                ):
                    is_kevbot_set = True
                    kevbot_slot = i
                    opponent_slot = 1 - i  # Get the other slot (0->1, 1->0)
                    break
            if is_kevbot_set:
                break

        if is_kevbot_set:
            opponent_name = chosen_set["slots"][opponent_slot]["entrant"]["name"].split(
                " | "
            )[-1]
            click.echo(opponent_name)
            return
        else:
            click.echo("Error: Selected set does not contain kevbot", err=True)
            raise click.Abort()

    # Display detailed information about chosen set focusing on entrants
    click.echo("\nChosen Set Details:")
    click.echo(
        f"Round: {chosen_set['fullRoundText'] or f'Round {chosen_set["round"]}'}"
    )

    # Show detailed entrant information
    for i, slot in enumerate(chosen_set["slots"], 1):
        entrant = slot["entrant"]
        click.echo(f"\nPlayer {i}:")
        click.echo(f"Team/Name: {entrant['name']}")
        if entrant.get("participants"):
            for participant in entrant["participants"]:
                if participant.get("gamerTag"):
                    click.echo(f"Gamer Tag: {participant['gamerTag']}")
                if participant.get("user", {}).get("id") == "658c6a49":
                    click.echo("*** This is kevbot ***")

    # Print full JSON for debugging
    click.echo("\nFull Set Data:")
    click.echo(json.dumps(chosen_set, indent=2))


@cli.command()
@click.option("--bracket", help="URL or slug of the bracket")
@click.option("--latest", is_flag=True, help="Choose the most recent bracket")
@click.option(
    "--num", default=100, help="Number of seeds to fetch (default: 100, max: 512)"
)
def entrants(bracket, latest, num):
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
        chosen = choose_bracket(latest=latest)
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
