#!/usr/bin/env python

"""Fetch publications from Google Scholar and merge new entries into papers.bib."""

import os
import re
import sys
import unicodedata

import yaml
from scholarly import ProxyGenerator, scholarly

# See bin/update_scholar_citations.py for the rationale behind this exit code.
EXIT_SCHOLAR_UNAVAILABLE: int = 75


class ScholarUnavailable(RuntimeError):
    """Google Scholar could not be reached or refused the request."""


def load_scholar_user_id() -> str:
    """Load the Google Scholar user ID from the configuration file."""
    config_file = "_data/socials.yml"
    if not os.path.exists(config_file):
        print(f"Configuration file {config_file} not found.")
        sys.exit(1)
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    scholar_user_id = config.get("scholar_userid")
    if not scholar_user_id:
        print("No 'scholar_userid' found in _data/socials.yml.")
        sys.exit(1)
    return scholar_user_id


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


def normalize_title(title: str) -> str:
    """Normalize a title for punctuation- and whitespace-insensitive matching."""
    normalized = unicodedata.normalize("NFKC", title).casefold()
    return " ".join(re.sub(r"[^\w]+", " ", normalized).split())


def make_cite_key(bib: dict) -> str:
    """Generate a BibTeX citation key like 'lee2023deep'."""
    authors = bib.get("author", "unknown")
    first_author_last = authors.split(",")[0].strip().split()[-1].lower()
    # Remove non-ascii characters
    first_author_last = unicodedata.normalize("NFKD", first_author_last)
    first_author_last = re.sub(r"[^a-z]", "", first_author_last)

    year = bib.get("pub_year", "0000")

    title = bib.get("title", "untitled")
    # Pick the first meaningful word from the title (skip short words)
    skip = {"a", "an", "the", "of", "for", "and", "in", "on", "to", "with", "is", "are", "it", "by", "from"}
    first_word = "untitled"
    for word in title.split():
        cleaned = re.sub(r"[^a-zA-Z]", "", word).lower()
        if cleaned and cleaned not in skip:
            first_word = cleaned
            break

    return f"{first_author_last}{year}{first_word}"


def escape_bibtex(value: str) -> str:
    """Escape special BibTeX characters."""
    value = value.replace("&", r"\&")
    value = value.replace("%", r"\%")
    value = value.replace("$", r"\$")
    # Don't escape braces or backslashes that may already be LaTeX
    return value


def pub_to_bibtex(pub: dict) -> tuple[str, str]:
    """Convert a scholarly publication dict to a BibTeX entry string.

    Returns (cite_key, bibtex_string).
    """
    bib = pub.get("bib", {})
    cite_key = make_cite_key(bib)

    # Determine entry type
    venue = bib.get("venue", "") or bib.get("journal", "") or bib.get("conference", "")
    if bib.get("citation", ""):
        # Try to detect conference proceedings
        citation = bib.get("citation", "").lower()
        if any(kw in citation for kw in ["proceedings", "conference", "workshop", "congress", "symposium"]):
            entry_type = "inproceedings"
        else:
            entry_type = "article"
    else:
        entry_type = "article"

    fields = []

    if bib.get("title"):
        fields.append(f"  title={{{escape_bibtex(bib['title'])}}}")

    if bib.get("author"):
        # scholarly returns "Author1 and Author2 and ..." format
        author_str = bib["author"]
        if isinstance(author_str, list):
            author_str = " and ".join(author_str)
        fields.append(f"  author={{{escape_bibtex(author_str)}}}")

    if entry_type == "article":
        journal = bib.get("journal") or bib.get("venue") or ""
        if journal:
            fields.append(f"  journal={{{escape_bibtex(journal)}}}")
    else:
        booktitle = bib.get("conference") or bib.get("venue") or bib.get("journal") or ""
        if booktitle:
            fields.append(f"  booktitle={{{escape_bibtex(booktitle)}}}")

    if bib.get("volume"):
        fields.append(f"  volume={{{bib['volume']}}}")
    if bib.get("number"):
        fields.append(f"  number={{{bib['number']}}}")
    if bib.get("pages"):
        fields.append(f"  pages={{{bib['pages']}}}")
    if bib.get("pub_year"):
        fields.append(f"  year={{{bib['pub_year']}}}")
    if bib.get("publisher"):
        fields.append(f"  publisher={{{escape_bibtex(bib['publisher'])}}}")

    # Link the entry to its Scholar citation record (citations badge on the
    # publications page reads _data/citations.yml keyed by this id).
    author_pub_id = pub.get("author_pub_id", "")
    if ":" in author_pub_id:
        fields.append(f"  google_scholar_id={{{author_pub_id.split(':')[-1]}}}")

    fields_str = ",\n".join(fields)
    return cite_key, f"@{entry_type}{{{cite_key},\n{fields_str}\n}}"


def load_existing_keys(bib_path: str) -> set[str]:
    """Extract existing citation keys from a .bib file."""
    keys = set()
    if not os.path.exists(bib_path):
        return keys
    with open(bib_path, "r") as f:
        content = f.read()
    for match in re.finditer(r"@\w+\{([^,]+),", content):
        keys.add(match.group(1).strip())
    return keys


def load_existing_titles(bib_path: str) -> set[str]:
    """Extract normalized existing titles from a .bib file for dedup."""
    titles = set()
    if not os.path.exists(bib_path):
        return titles
    with open(bib_path, "r") as f:
        content = f.read()
    for match in re.finditer(r"title\s*=\s*\{(.+?)\}", content):
        titles.add(normalize_title(match.group(1)))
    return titles


def fill_publication_details(publications: list[dict]) -> list[dict]:
    """Fetch full metadata atomically so partial records are never committed."""
    filled_pubs = []
    failures = []

    for pub in publications:
        title = pub.get("bib", {}).get("title", "Unknown")
        try:
            filled = scholarly.fill(pub)
            # scholarly may omit this link on a filled result; preserve it so
            # the generated BibTeX entry still receives its citation badge.
            if pub.get("author_pub_id") and not filled.get("author_pub_id"):
                filled["author_pub_id"] = pub["author_pub_id"]
            filled_pubs.append(filled)
        except Exception as e:
            failures.append(f"{title}: {e}")

    if failures:
        raise ScholarUnavailable(
            "Could not fetch complete metadata for new publications; papers.bib was not changed:\n- "
            + "\n- ".join(failures)
        )

    return filled_pubs


def main() -> None:
    scholar_id = load_scholar_user_id()
    bib_path = "_bibliography/papers.bib"

    print(f"Fetching publications for Google Scholar ID: {scholar_id}")

    configure_proxy()
    scholarly.set_timeout(15)
    scholarly.set_retries(3)

    try:
        author = scholarly.search_author_id(scholar_id)
        author_data = scholarly.fill(author)
    except Exception as e:
        raise ScholarUnavailable(f"Could not fetch author data: {e}") from e

    publications = author_data.get("publications", [])
    if not publications:
        print("No publications found.")
        return

    print(f"Found {len(publications)} publications on Google Scholar.")

    existing_keys = load_existing_keys(bib_path)
    existing_titles = load_existing_titles(bib_path)

    # Only fill publications that are actually new — fill() makes one Scholar
    # request per publication, which is what pushed CI past its timeout.
    new_pubs = []
    for pub in publications:
        title = normalize_title(pub.get("bib", {}).get("title", ""))
        if title and title in existing_titles:
            continue
        new_pubs.append(pub)

    print(f"{len(new_pubs)} publications not yet in {bib_path}.")

    filled_pubs = fill_publication_details(new_pubs)

    new_entries = []
    for pub in filled_pubs:
        bib = pub.get("bib", {})
        title = normalize_title(bib.get("title", ""))

        # Re-check in case fill() normalized the title differently
        if title and title in existing_titles:
            continue

        cite_key, bibtex = pub_to_bibtex(pub)

        # Ensure unique cite key
        base_key = cite_key
        counter = 2
        while cite_key in existing_keys:
            cite_key = f"{base_key}{counter}"
            bibtex = bibtex.replace(f"{{{base_key},", f"{{{cite_key},", 1)
            counter += 1

        existing_keys.add(cite_key)
        existing_titles.add(title)
        new_entries.append(bibtex)
        print(f"  NEW: {bib.get('title', 'Unknown')} ({bib.get('pub_year', '?')})")

    if not new_entries:
        print("No new publications to add.")
        return

    print(f"\nAppending {len(new_entries)} new entries to {bib_path}")

    with open(bib_path, "a") as f:
        f.write("\n")
        for entry in new_entries:
            f.write(f"\n{entry}\n")

    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except ScholarUnavailable as e:
        print(f"Google Scholar unavailable: {e}")
        print("Leaving papers.bib untouched.")
        sys.exit(EXIT_SCHOLAR_UNAVAILABLE)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
