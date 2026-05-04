"""Zhihu profile extractor — uses DynamicFetcher for JS-rendered pages."""

from __future__ import annotations

from clawithme.crawler.base import Profile, ProfileExtractor
from clawithme.crawler.client import CrawlerClient
from clawithme.crawler.utils import first_text, parse_count
from clawithme.logging import get_logger

logger = get_logger()

# Known CSS selectors for zhihu profile page (React-rendered, may change)
SELECTORS = {
    "display_name": [
        ".ProfileHeader-title .ProfileHeader-name",
        ".ProfileHeader-name",
        "h1.ProfileHeader-title",
    ],
    "bio": [
        ".ProfileHeader-headline",
        ".ProfileHeader-detailItem--bio",
    ],
    "avatar_img": [
        ".ProfileHeader-avatar img",
        ".Avatar img",
        "img.Avatar-image",
    ],
    "location": [
        ".ProfileHeader-detailItem--location",
        ".ProfileHeader-infoItem--location",
    ],
    "follower_count": [
        ".FollowshipCard-count",
        ".ProfileHeader-followership strong",
    ],
}


class ZhihuExtractor(ProfileExtractor):
    """Extract public profile data from 知乎 (zhihu.com)."""

    site_id = "zhihu"
    requires_dynamic = True

    def extract(self, site: dict, username: str) -> Profile:
        url = f"https://www.zhihu.com/people/{username}"
        profile = Profile(
            site_id="zhihu",
            site_name=site.get("name", "知乎"),
            url=url,
            username=username,
        )

        client = CrawlerClient(timeout_ms=30000)
        response = client.fetch_dynamic(
            url,
            wait_selector=".ProfileHeader",
            disable_resources=True,
            block_ads=True,
        )

        if response is None:
            logger.warning("zhihu_no_response", username=username)
            return profile

        # Check for signin redirect
        if "/signin" in response.url:
            logger.info("zhihu_login_required", username=username, redirected_to=response.url)
            return profile

        if response.status != 200:
            logger.warning("zhihu_bad_status", username=username, status=response.status)
            return profile

        # Extract display name
        name = first_text(response, SELECTORS["display_name"])
        if name:
            profile.display_name = name

        # Extract bio
        bio = first_text(response, SELECTORS["bio"])
        if bio:
            profile.bio = bio

        # Extract avatar URL
        for sel in SELECTORS["avatar_img"]:
            imgs = response.css(sel)
            if imgs:
                src = imgs[0].attrib.get("src", "")
                if src and not src.startswith("data:"):
                    profile.avatar_url = src
                    break

        # Extract location
        location = first_text(response, SELECTORS["location"])
        if location:
            profile.location = location

        # Extract follower count
        follower_text = first_text(response, SELECTORS["follower_count"])
        if follower_text:
            profile.follower_count = parse_count(follower_text)

        logger.info("zhihu_extracted", username=username, display_name=profile.display_name)
        return profile
