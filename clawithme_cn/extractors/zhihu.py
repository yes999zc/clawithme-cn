"""Zhihu profile extractor."""

from __future__ import annotations

from clawithme.crawler.base import Profile, ProfileExtractor


class ZhihuExtractor(ProfileExtractor):
    """Extract public profile data from 知乎 (zhihu.com)."""

    site_id = "zhihu"

    def can_handle(self, site: dict) -> bool:
        return site.get("id") == "zhihu"

    def extract(self, site: dict, username: str) -> Profile:
        profile = Profile(
            site_id="zhihu",
            site_name=site.get("name", "知乎"),
            url=f"https://www.zhihu.com/people/{username}",
            username=username,
        )
        # TODO: Phase 3.1.2 — actual Scrapling DynamicFetcher scraping
        return profile
