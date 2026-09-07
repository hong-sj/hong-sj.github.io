#!/usr/bin/env python

import os
import sys
import yaml
from datetime import datetime
from scholarly import ProxyGenerator, scholarly

# Exit code for "Google Scholar was unreachable" (EX_TEMPFAIL, sysexits.h).
# Google blocks datacenter IP ranges, so a scheduled GitHub Actions run is
# refused far more often than a run from a residential connection. That is a
# transient environment problem, not a bug, so it gets its own exit code: the
# workflow downgrades it to a warning while the cached data is still fresh.
# Every other failure (bad config, incomplete response, unwritable file) keeps
# exit code 1 and fails the run immediately.
EXIT_SCHOLAR_UNAVAILABLE: int = 75


class ScholarUnavailable(RuntimeError):
    """Google Scholar could not be reached or refused the request.

    Subclasses RuntimeError so that `except ScholarUnavailable` matches only
    fetch failures, while a plain RuntimeError (bad data we did receive) still
    falls through to the hard-failure path.
    """


def load_scholar_user_id() -> str:
    """Load the Google Scholar user ID from the configuration file."""
    config_file = "_data/socials.yml"
    if not os.path.exists(config_file):
        print(
            f"Configuration file {config_file} not found. Please ensure the file exists and contains your Google Scholar user ID."
        )
        sys.exit(1)
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        scholar_user_id = config.get("scholar_userid")
        if not scholar_user_id:
            print(
                "No 'scholar_userid' found in the configuration file. Please add 'scholar_userid' to _data/socials.yml."
            )
            sys.exit(1)
        return scholar_user_id
    except yaml.YAMLError as e:
        print(
            f"Error parsing YAML file {config_file}: {e}. Please check the file for correct YAML syntax."
        )
        sys.exit(1)


SCHOLAR_USER_ID: str = load_scholar_user_id()
OUTPUT_FILE: str = "_data/citations.yml"


def configure_proxy() -> bool:
    """Use ScraperAPI when its key is available in the environment."""
    api_key = os.environ.get("SCRAPER_API_KEY")
    if not api_key:
        print(
            "Warning: SCRAPER_API_KEY is not configured; querying Google Scholar directly."
        )
        return False

    proxy = ProxyGenerator()
    if not proxy.ScraperAPI(api_key):
        raise RuntimeError("Could not configure the ScraperAPI proxy.")

    scholarly.use_proxy(proxy)
    print("Using ScraperAPI for Google Scholar requests.")
    return True


def get_scholar_citations() -> None:
    """Fetch and update Google Scholar citation data."""
    print(f"Fetching citations for Google Scholar ID: {SCHOLAR_USER_ID}")
    today = datetime.now().strftime("%Y-%m-%d")

    existing_data = None
    # Check if the output file was already updated today
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r") as f:
                existing_data = yaml.safe_load(f)
            if (
                existing_data
                and "metadata" in existing_data
                and "last_updated" in existing_data["metadata"]
            ):
                print(f"Last updated on: {existing_data['metadata']['last_updated']}")
                if existing_data["metadata"]["last_updated"] == today:
                    print("Citations data is already up-to-date. Skipping fetch.")
                    return
        except Exception as e:
            print(
                f"Warning: Could not read existing citation data from {OUTPUT_FILE}: {e}. The file may be missing or corrupted."
            )

    citation_data = {"metadata": {"last_updated": today}, "papers": {}}

    configure_proxy()
    scholarly.set_timeout(15)
    scholarly.set_retries(3)
    try:
        author = scholarly.search_author_id(SCHOLAR_USER_ID)
        author_data = scholarly.fill(author)
    except Exception as e:
        raise ScholarUnavailable(
            f"Could not fetch author data for user ID '{SCHOLAR_USER_ID}': {e}"
        ) from e

    if not author_data:
        raise ScholarUnavailable(
            f"Google Scholar returned no author data for user ID '{SCHOLAR_USER_ID}'."
        )

    required_metrics = ("citedby", "hindex", "i10index")
    missing_metrics = [key for key in required_metrics if key not in author_data]
    if missing_metrics:
        raise RuntimeError(
            "Google Scholar returned incomplete author metrics: "
            + ", ".join(missing_metrics)
        )

    citation_data["metadata"]["total_citations"] = author_data["citedby"]
    citation_data["metadata"]["h_index"] = author_data["hindex"]
    citation_data["metadata"]["i10_index"] = author_data["i10index"]
    print(
        f"Author stats — citations: {citation_data['metadata']['total_citations']}, "
        f"h-index: {citation_data['metadata']['h_index']}, "
        f"i10-index: {citation_data['metadata']['i10_index']}"
    )

    publications = author_data.get("publications")
    if not publications:
        raise RuntimeError(
            f"No publications found in author data for user ID '{SCHOLAR_USER_ID}'; preserving the previous cache."
        )

    publication_errors = []
    for pub in publications:
        try:
            pub_id = pub.get("pub_id") or pub.get("author_pub_id")
            if not pub_id:
                publication_errors.append(
                    f"No ID found for publication: {pub.get('bib', {}).get('title', 'Unknown')}"
                )
                continue

            title = pub.get("bib", {}).get("title", "Unknown Title")
            year = pub.get("bib", {}).get("pub_year", "Unknown Year")
            citations = pub.get("num_citations", 0)

            print(f"Found: {title} ({year}) - Citations: {citations}")

            citation_data["papers"][pub_id] = {
                "title": title,
                "year": year,
                "citations": citations,
            }
        except Exception as e:
            publication_errors.append(
                f"Could not process publication '{pub.get('bib', {}).get('title', 'Unknown')}': {e}"
            )

    if publication_errors:
        raise RuntimeError(
            "Google Scholar returned incomplete publication data; preserving the previous cache:\n- "
            + "\n- ".join(publication_errors)
        )

    # Always write the file so last_updated reflects the date of the latest successful fetch,
    # even when citation counts are unchanged.
    if existing_data and existing_data.get("papers") == citation_data["papers"]:
        print("No changes in citation counts. Updating last_updated date only.")

    try:
        with open(OUTPUT_FILE, "w") as f:
            yaml.dump(citation_data, f, width=1000, sort_keys=True)
        print(f"Citation data saved to {OUTPUT_FILE}")
    except Exception as e:
        print(
            f"Error writing citation data to {OUTPUT_FILE}: {e}. Please check file permissions and disk space."
        )
        sys.exit(1)


if __name__ == "__main__":
    try:
        get_scholar_citations()
    except ScholarUnavailable as e:
        print(f"Google Scholar unavailable: {e}")
        print("Leaving the existing citation cache untouched.")
        sys.exit(EXIT_SCHOLAR_UNAVAILABLE)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
