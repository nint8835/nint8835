import os
from typing import Any, Dict, Iterator

import pygal
import requests
from dotenv import load_dotenv
from pygal.style import Style

load_dotenv()

# Colours to be used for languages lacking their own colour.
# Selected from https://github.com/ozh/github-colors from the languages that were
# deemed unlikely to ever appear in this graph.
FILLER_COLOURS = ["#E8274B", "#64C800", "#9DC3FF", "#a957b0", "#cd6400"]

LANGUAGES_QUERY = """
query ($first: Int, $after: String) {
  viewer {
    repositories(
      first: $first
      after: $after
      ownerAffiliations: [OWNER]
      isFork: false
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        languages(first: 20) {
          edges {
            size
            node {
              name
              color
            }
          }
        }
        repositoryTopics(first: 10) {
          nodes {
            topic {
              name
            }
          }
        }
      }
    }
  }
}
"""


def fetch_repos() -> Iterator[Dict[str, Any]]:
    variables = {"first": 100}
    has_next_page = True

    while has_next_page:
        resp = requests.post(
            "https://api.github.com/graphql",
            json={"query": LANGUAGES_QUERY, "variables": variables},
            headers={"Authorization": f"Bearer {os.environ['GITHUB_PAT']}"},
        )
        resp.raise_for_status()

        data = resp.json()["data"]
        repositories_resp = data["viewer"]["repositories"]

        has_next_page = repositories_resp["pageInfo"]["hasNextPage"]
        variables["after"] = repositories_resp["pageInfo"]["endCursor"]

        yield from repositories_resp["nodes"]


language_counts: Dict[str, int] = {}
language_colours: Dict[str, str] = {"Other": FILLER_COLOURS.pop()}

for repository in fetch_repos():
    if any(
        topic["topic"]["name"] == "language-stats-ignored"
        for topic in repository["repositoryTopics"]["nodes"]
    ):
        continue
    for language in repository["languages"]["edges"]:
        lang_name = language["node"]["name"]
        language_counts[lang_name] = (
            language_counts.get(lang_name, 0) + language["size"]
        )

        if lang_name not in language_colours:
            language_colours[lang_name] = language["node"]["color"]

for language, colour in language_colours.items():
    if colour is None:
        language_colours[language] = FILLER_COLOURS.pop()

sorted_languages = sorted(
    language_counts, key=lambda k: language_counts[k], reverse=True
)

top_language_counts = {key: language_counts[key] for key in sorted_languages[:10]}
top_language_counts["Other"] = sum(
    language_counts[key] for key in sorted_languages[10:]
)

style = Style(colors=list(language_colours[lang] for lang in top_language_counts))

chart = pygal.Pie(style=style)
chart.uuid = "4845283b-3763-48f2-a4a5-440176c46fed"
chart._tooltip_data = lambda *args, **kwargs: None

for language, byte_count in top_language_counts.items():
    chart.add(language, byte_count)

chart.render_to_file("languages.svg")
