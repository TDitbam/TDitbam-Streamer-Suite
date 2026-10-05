"""Small, dependency-free GitHub Tag update checker."""

import json
import re
from dataclasses import dataclass
from typing import Callable, Optional, Tuple
from urllib.parse import quote
from urllib.request import Request, urlopen

from .version import (
    GITHUB_RELEASES_URL,
    GITHUB_REPOSITORY_URL,
    GITHUB_TAGS_API_URL,
)


VersionTuple = Tuple[int, int, int]
STABLE_VERSION_TAG = re.compile(r"^[vV]?(\d+)\.(\d+)\.(\d+)$")


class UpdateCheckError(RuntimeError):
    """Raised when GitHub does not return a usable stable version tag."""


@dataclass(frozen=True)
class UpdateInfo:
    tag_name: str
    version: VersionTuple
    download_url: str


def parse_version_tag(tag_name: str) -> Optional[VersionTuple]:
    match = STABLE_VERSION_TAG.fullmatch((tag_name or "").strip())
    if not match:
        return None
    return tuple(int(component) for component in match.groups())


def compare_versions(current: VersionTuple, latest: VersionTuple) -> int:
    return (current > latest) - (current < latest)


def _release_url(tag_name: str) -> str:
    encoded_tag = quote(tag_name, safe="")
    return f"{GITHUB_RELEASES_URL}/tag/{encoded_tag}"


def fetch_latest_tag(timeout: float = 8.0, opener: Callable = urlopen) -> UpdateInfo:
    """Return the highest stable semantic version from repository tags."""
    request = Request(
        GITHUB_TAGS_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "TDitbam-Streamer-Suite-Update-Checker",
            "X-GitHub-Api-Version": "2026-03-10",
        },
    )
    try:
        with opener(request, timeout=timeout) as response:
            payload = json.load(response)
    except Exception as error:
        raise UpdateCheckError(f"GitHub tag request failed: {error}") from error

    if not isinstance(payload, list):
        raise UpdateCheckError("GitHub returned an invalid tag response.")

    stable_tags = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        tag_name = str(item.get("name", "")).strip()
        version = parse_version_tag(tag_name)
        if version is not None:
            stable_tags.append((version, tag_name))

    if not stable_tags:
        raise UpdateCheckError("No stable version tags were found on GitHub.")

    version, tag_name = max(stable_tags, key=lambda entry: entry[0])
    return UpdateInfo(
        tag_name=tag_name,
        version=version,
        download_url=_release_url(tag_name),
    )


def repository_url() -> str:
    return GITHUB_REPOSITORY_URL
