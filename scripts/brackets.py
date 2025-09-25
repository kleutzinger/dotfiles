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
import subprocess

KEVBOT_SGG_ID = "658c6a49"

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
@click.option("--execute", is_flag=True, help="execute Uploading a new bracket")
def bracket(
    latest: bool = False, upload: bool = False, execute: bool = False
) -> Bracket:
    """List available brackets, choose one"""
    bracket = choose_bracket(latest=latest)
    if upload or execute:
        title = bracket.get("title", "")
        title = title.replace("'", "")
        bracket_url = bracket.get("BracketUrl")
        vod = bracket["VODs"][0]["url"]
        cmd = f"vodbackup.py --cleanup --title '{title}' --bracket-url '{bracket_url}' '{vod}'"
        if upload:
            click.echo(cmd)
        if execute:
            click.echo(f"executing: {cmd}")
            subprocess.run(cmd, shell=True, check=True)
    else:
        click.echo(json.dumps(bracket, indent=2))
    return Bracket


@cli.command()
@click.option("--tournament-url", required=True, help="URL of the tournament")
@click.option("--event-name", required=True, help="Name of the event")
def tourney2slug(tournament_url, event_name):
    """Find event by name in tournament and return the full slug"""
    # Extract tournament slug from URL
    tournament_slug = url2slug(tournament_url)

    # Query start.gg API to get tournament and find event by name
    query = """
    query GetTournamentEvents($slug: String!) {
        tournament(slug: $slug) {
            id
            name
            slug
            events {
                id
                name
                slug
            }
        }
    }
    """

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    response = requests.post(
        "https://api.start.gg/gql/alpha",
        json={"query": query, "variables": {"slug": tournament_slug}},
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

    tournament = data["data"]["tournament"]
    if not tournament:
        click.echo(f"Tournament not found: {tournament_slug}", err=True)
        raise click.Abort()

    # Find event by name (case-insensitive)
    matching_events = []
    for event in tournament["events"]:
        if event["name"].lower() == event_name.lower():
            matching_events.append(event)

    if not matching_events:
        click.echo(
            f"Event '{event_name}' not found in tournament '{tournament['name']}'",
            err=True,
        )
        click.echo("Available events:", err=True)
        for event in tournament["events"]:
            click.echo(f"  - {event['name']}", err=True)
        raise click.Abort()

    if len(matching_events) > 1:
        click.echo(f"Multiple events found with name '{event_name}':", err=True)
        for event in matching_events:
            click.echo(f"  - {event['name']} (slug: {event['slug']})", err=True)
        raise click.Abort()

    # Return the full slug
    event_slug = matching_events[0]["slug"]

    # Check if event_slug already contains the tournament part
    if event_slug.startswith(tournament_slug):
        full_slug = event_slug
    else:
        full_slug = f"{tournament_slug}/event/{event_slug}"

    click.echo(full_slug)
    return full_slug


@cli.command()
@click.option("--bracket", help="URL or slug of the bracket")
@click.option("--latest", is_flag=True, help="Choose the most recent bracket")
def sets(bracket, latest):
    """Show kevbot's sets with win/loss format"""
    if bracket:
        # If it's a URL, convert to slug
        if bracket.startswith("http"):
            slug = url2slug(bracket)
        else:
            slug = bracket
    else:
        chosen = choose_bracket(latest=latest)
        slug = url2slug(chosen["BracketUrl"])

    # Enhanced query to get all sets from all phases and phase groups with pagination
    query = """
        query EventSets($slug: String!, $perPage: Int!) {
            event(slug: $slug) {
                name
                phases {
                    id
                    name
                    phaseGroups {
                        nodes {
                            id
                            displayIdentifier
                            sets(perPage: $perPage) {
                                nodes {
                                    id
                                    round
                                    fullRoundText
                                    winnerId
                                    displayScore
                                    slots {
                                        entrant {
                                            id
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
                    sets(perPage: $perPage) {
                        nodes {
                            id
                            round
                            fullRoundText
                            winnerId
                            displayScore
                            slots {
                                entrant {
                                    id
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
        json={"query": query, "variables": {"slug": slug, "perPage": 500}},
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

    # Collect all sets from all phases and phase groups (deduplicate by set ID)
    all_sets_dict = {}
    for phase in event["phases"]:
        # Get sets directly from phase
        if phase["sets"]["nodes"]:
            for s in phase["sets"]["nodes"]:
                all_sets_dict[s["id"]] = s

        # Get sets from phase groups (pools)
        if phase["phaseGroups"]["nodes"]:
            for phase_group in phase["phaseGroups"]["nodes"]:
                if phase_group["sets"]["nodes"]:
                    for s in phase_group["sets"]["nodes"]:
                        all_sets_dict[s["id"]] = s

    all_sets = list(all_sets_dict.values())

    # Filter for kevbot sets
    kevbot_sets = []
    for s in all_sets:
        if s["slots"][0]["entrant"] and s["slots"][1]["entrant"]:
            # Check if kevbot is in the set
            kevbot_slot = None
            opponent_slot = None

            for i, slot in enumerate(s["slots"]):
                if slot["entrant"] and slot["entrant"]["participants"]:
                    for participant in slot["entrant"]["participants"]:
                        if participant and (
                            "kevbot" in participant.get("gamerTag", "").lower()
                            or (
                                participant.get("user")
                                and participant.get("user", {}).get("id")
                                == KEVBOT_SGG_ID
                            )
                        ):
                            kevbot_slot = i
                            opponent_slot = 1 - i
                            break
                if kevbot_slot is not None:
                    break

            if kevbot_slot is not None:
                opponent_name = s["slots"][opponent_slot]["entrant"]["name"].split(
                    " | "
                )[-1]
                round_text = s["fullRoundText"] or f"Round {s['round']}"

                # Abbreviate round names
                round_lower = round_text.lower().replace("-", "")

                # Start with bracket type
                if "winners" in round_lower:
                    abbrev = "W"
                elif "losers" in round_lower:
                    abbrev = "L"
                elif "grand" in round_lower:
                    abbrev = "GF"
                else:
                    abbrev = ""

                # Add round type
                if "quarter" in round_lower:
                    abbrev += "Q"
                elif "semi" in round_lower:
                    abbrev += "S"
                elif "final" in round_lower:
                    if abbrev != "GF":  # Don't add F to GF
                        abbrev += "F"

                round_text = abbrev if abbrev else round_text

                # Determine win/loss and format score
                if s["winnerId"] and s["displayScore"]:
                    kevbot_won = (
                        s["winnerId"] == s["slots"][kevbot_slot]["entrant"]["id"]
                    )

                    # Parse the actual score from displayScore
                    score_text = s["displayScore"]
                    import re

                    # Try multiple patterns to extract scores
                    # Pattern 1: "3 - 1" or "3-1"
                    score_match = re.search(r"(\d+)\s*-\s*(\d+)", score_text)
                    if not score_match:
                        # Pattern 2: "Name 3-Name 1"
                        score_match = re.search(r"\s(\d+)-.*?\s(\d+)", score_text)
                    if not score_match:
                        # Pattern 3: Just look for any two numbers
                        numbers = re.findall(r"\d+", score_text)
                        if len(numbers) >= 2:
                            score1, score2 = numbers[0], numbers[1]
                        else:
                            score1, score2 = None, None
                    else:
                        score1, score2 = score_match.groups()

                    if score1 and score2:
                        # Determine which score is kevbot's based on slot position
                        if kevbot_slot == 0:
                            kevbot_score = score1
                            opponent_score = score2
                        else:
                            kevbot_score = score2
                            opponent_score = score1
                        formatted_score = f"{kevbot_score}-{opponent_score}"
                    else:
                        # Show the raw score if we can't parse it
                        formatted_score = f"[{score_text}]"

                    status = ""
                else:
                    status = ""
                    formatted_score = "?-?"

                kevbot_sets.append(
                    {
                        "opponent": opponent_name,
                        "status": status,
                        "score": formatted_score,
                        "round": round_text,
                        "round_num": s["round"],
                    }
                )

    if not kevbot_sets:
        click.echo("No sets found for kevbot in this tournament.")
        return

    # Sort by round number (reverse for most recent first)
    kevbot_sets.sort(key=lambda x: x["round_num"], reverse=True)

    # Print console summary
    if kevbot_sets:
        click.echo("Tournament Results:")
        for set_info in kevbot_sets:
            click.echo(
                f"{set_info['opponent']} {set_info['score']} {set_info['round']}"
            )
        click.echo()

    # Generate HTML table
    html_rows = []
    for set_info in kevbot_sets:
        html_rows.append(
            f"<tr><td>{set_info['opponent']}</td><td>{set_info['status']}</td><td>{set_info['score']} {set_info['round']}</td></tr>"
        )

    html_table = f"<table><tbody>{''.join(html_rows)}</tbody></table>"

    # Copy HTML to clipboard
    try:
        result = subprocess.run(
            ["xclip", "-selection", "clipboard", "-i", "-t", "text/html"],
            input=html_table,
            text=True,
            check=True,
        )
        click.echo("HTML table copied to clipboard!")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error copying to clipboard: {e}", err=True)
    except FileNotFoundError:
        click.echo("xclip not found.")


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
