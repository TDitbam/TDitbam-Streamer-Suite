import io
import json
import unittest

from core.update_checker import (
    UpdateCheckError,
    compare_versions,
    fetch_latest_tag,
    parse_version_tag,
)


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def opener_for(payload, captured=None):
    def opener(request, timeout):
        if captured is not None:
            captured["url"] = request.full_url
            captured["headers"] = dict(request.header_items())
            captured["timeout"] = timeout
        return FakeResponse(json.dumps(payload).encode("utf-8"))

    return opener


class UpdateCheckerTests(unittest.TestCase):
    def test_parse_stable_version_tags(self):
        self.assertEqual((3, 6, 2), parse_version_tag("v3.6.2"))
        self.assertEqual((10, 0, 1), parse_version_tag("10.0.1"))
        self.assertIsNone(parse_version_tag("v3.7.0-beta"))
        self.assertIsNone(parse_version_tag("latest"))

    def test_fetch_chooses_highest_stable_tag_not_first_item(self):
        captured = {}
        result = fetch_latest_tag(
            opener=opener_for(
                [
                    {"name": "v3.6.1"},
                    {"name": "v4.0.0-beta"},
                    {"name": "v3.6.3"},
                    {"name": "v3.6.2"},
                ],
                captured,
            )
        )

        self.assertEqual("v3.6.3", result.tag_name)
        self.assertEqual((3, 6, 3), result.version)
        self.assertTrue(result.download_url.endswith("/releases/tag/v3.6.3"))
        self.assertIn("/tags?per_page=100", captured["url"])
        self.assertEqual(
            "application/vnd.github+json", captured["headers"]["Accept"]
        )

    def test_invalid_or_empty_tag_response_is_reported(self):
        for payload in ({"name": "v3.6.2"}, [], [{"name": "nightly"}]):
            with self.subTest(payload=payload):
                with self.assertRaises(UpdateCheckError):
                    fetch_latest_tag(opener=opener_for(payload))

    def test_version_comparison(self):
        self.assertEqual(-1, compare_versions((3, 6, 1), (3, 6, 2)))
        self.assertEqual(0, compare_versions((3, 6, 2), (3, 6, 2)))
        self.assertEqual(1, compare_versions((3, 6, 3), (3, 6, 2)))


if __name__ == "__main__":
    unittest.main()
