import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publications = load_module(
    "update_scholar_publications", "bin/update_scholar_publications.py"
)
citations = load_module("update_scholar_citations", "bin/update_scholar_citations.py")


class ScholarPublicationSyncTests(unittest.TestCase):
    def test_normalize_title_ignores_case_punctuation_and_spacing(self):
        left = publications.normalize_title("Beyond the ROC Curve: Activity Monitoring")
        right = publications.normalize_title(
            "  BEYOND the ROC curve — activity   monitoring  "
        )

        self.assertEqual(left, right)

    def test_existing_titles_are_normalized(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bib") as bib_file:
            bib_file.write("@article{x,\n  title={A Study: With Punctuation}\n}\n")
            bib_file.flush()

            titles = publications.load_existing_titles(bib_file.name)

        self.assertIn("a study with punctuation", titles)

    def test_pub_to_bibtex_adds_google_scholar_id(self):
        publication = {
            "author_pub_id": "dOZXFgoAAAAJ:new-id",
            "bib": {
                "title": "A New Paper",
                "author": "Hong, Sungjun and Doe, Jane",
                "journal": "Test Journal",
                "pub_year": "2026",
            },
        }

        cite_key, bibtex = publications.pub_to_bibtex(publication)

        self.assertEqual("hong2026new", cite_key)
        self.assertIn("google_scholar_id={new-id}", bibtex)

    def test_fill_publication_details_preserves_author_pub_id(self):
        publication = {
            "author_pub_id": "dOZXFgoAAAAJ:new-id",
            "bib": {"title": "A New Paper"},
        }
        filled = {"bib": {"title": "A New Paper", "journal": "Test Journal"}}

        with patch.object(publications.scholarly, "fill", return_value=filled):
            result = publications.fill_publication_details([publication])

        self.assertEqual("dOZXFgoAAAAJ:new-id", result[0]["author_pub_id"])

    def test_fill_publication_details_is_atomic_on_failure(self):
        publication = {
            "author_pub_id": "dOZXFgoAAAAJ:new-id",
            "bib": {"title": "A New Paper"},
        }

        with patch.object(
            publications.scholarly, "fill", side_effect=RuntimeError("blocked")
        ):
            with self.assertRaisesRegex(RuntimeError, "papers.bib was not changed"):
                publications.fill_publication_details([publication])


class ScholarProxyTests(unittest.TestCase):
    def test_proxy_is_optional_when_secret_is_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(publications.configure_proxy())
            self.assertFalse(citations.configure_proxy())

    def test_proxy_is_enabled_when_secret_is_available(self):
        with (
            patch.dict(os.environ, {"SCRAPER_API_KEY": "test-key"}, clear=True),
            patch.object(publications, "ProxyGenerator") as proxy_factory,
            patch.object(publications.scholarly, "use_proxy") as use_proxy,
        ):
            proxy_factory.return_value.ScraperAPI.return_value = True

            self.assertTrue(publications.configure_proxy())

        proxy_factory.return_value.ScraperAPI.assert_called_once_with("test-key")
        use_proxy.assert_called_once_with(proxy_factory.return_value)


class ScholarUnavailableContractTests(unittest.TestCase):
    """The workflows branch on exit 75, so the classification must hold."""

    def setUp(self):
        # Point OUTPUT_FILE at a path that does not exist, so these tests never
        # read the repo's real cache. If they did, a cache already stamped with
        # today's date would trip the "already up-to-date" early return and the
        # fetch under test would never run.
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        patcher = patch.object(
            citations, "OUTPUT_FILE", os.path.join(self._tmpdir.name, "absent.yml")
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_unavailable_is_a_runtime_error_subclass(self):
        # `except ScholarUnavailable` must not swallow a plain RuntimeError,
        # but the existing atomicity tests still assert RuntimeError.
        for module in (publications, citations):
            self.assertTrue(issubclass(module.ScholarUnavailable, RuntimeError))
            self.assertNotIsInstance(RuntimeError("x"), module.ScholarUnavailable)
            self.assertEqual(75, module.EXIT_SCHOLAR_UNAVAILABLE)

    def test_fetch_failure_raises_unavailable_not_plain_error(self):
        with (
            patch.object(citations, "configure_proxy"),
            patch.object(
                citations.scholarly,
                "search_author_id",
                side_effect=Exception("Cannot Fetch from Google Scholar."),
            ),
        ):
            with self.assertRaises(citations.ScholarUnavailable):
                citations.get_scholar_citations()

    def test_empty_author_response_raises_unavailable(self):
        with (
            patch.object(citations, "configure_proxy"),
            patch.object(
                citations.scholarly, "search_author_id", return_value={"scholar_id": "p"}
            ),
            patch.object(citations.scholarly, "fill", return_value=None),
        ):
            with self.assertRaises(citations.ScholarUnavailable):
                citations.get_scholar_citations()

    def test_incomplete_metrics_is_not_classified_as_unavailable(self):
        # Bad data we *did* receive is a real failure: it must stay exit 1.
        incomplete_author = {"citedby": 1, "hindex": 5, "publications": []}
        with (
            patch.object(citations, "configure_proxy"),
            patch.object(
                citations.scholarly, "search_author_id", return_value={"scholar_id": "p"}
            ),
            patch.object(citations.scholarly, "fill", return_value=incomplete_author),
        ):
            with self.assertRaises(RuntimeError) as ctx:
                citations.get_scholar_citations()
        self.assertNotIsInstance(ctx.exception, citations.ScholarUnavailable)

    def test_publication_fill_failure_is_unavailable(self):
        publication = {"author_pub_id": "x:y", "bib": {"title": "A Paper"}}
        with patch.object(
            publications.scholarly, "fill", side_effect=RuntimeError("blocked")
        ):
            with self.assertRaises(publications.ScholarUnavailable):
                publications.fill_publication_details([publication])


class ScholarCitationSyncTests(unittest.TestCase):
    def test_incomplete_response_preserves_existing_cache(self):
        existing_data = {
            "metadata": {
                "last_updated": "2000-01-01",
                "total_citations": 100,
                "h_index": 5,
                "i10_index": 4,
            },
            "papers": {"profile:paper": {"citations": 10}},
        }

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".yml") as cache_file:
            yaml.safe_dump(existing_data, cache_file)
            cache_file.flush()

            incomplete_author = {
                "citedby": 101,
                "hindex": 5,
                "publications": [],
            }
            with (
                patch.object(citations, "OUTPUT_FILE", cache_file.name),
                patch.object(citations, "configure_proxy"),
                patch.object(
                    citations.scholarly,
                    "search_author_id",
                    return_value={"scholar_id": "profile"},
                ),
                patch.object(
                    citations.scholarly, "fill", return_value=incomplete_author
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "incomplete author metrics"):
                    citations.get_scholar_citations()

            cache_file.seek(0)
            self.assertEqual(existing_data, yaml.safe_load(cache_file))


if __name__ == "__main__":
    unittest.main()
