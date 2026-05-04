"""Tests for ZhihuExtractor — dynamic fetcher paths."""

from unittest.mock import MagicMock, patch

from clawithme_cn.extractors.zhihu import ZhihuExtractor


class TestZhihuExtractor:
    def test_can_handle_zhihu(self):
        ex = ZhihuExtractor()
        assert ex.can_handle({"id": "zhihu"}) is True

    def test_can_handle_other(self):
        ex = ZhihuExtractor()
        assert ex.can_handle({"id": "twitter"}) is False

    def test_requires_dynamic_true(self):
        ex = ZhihuExtractor()
        assert ex.requires_dynamic is True

    @patch("clawithme.crawler.client.HttpClient")
    def test_extract_with_mock_response(self, mock_http_cls):
        mock_http = MagicMock()
        mock_http_cls.return_value = mock_http

        mock_page = MagicMock()
        mock_page.status = 200
        mock_page.url = "https://www.zhihu.com/people/testuser"
        mock_page.text = "mock"
        mock_page.body = b"mock"

        mock_page.css.side_effect = lambda sel: {
            ".ProfileHeader-title .ProfileHeader-name": [
                MagicMock(text="测试用户", attrib={})
            ],
            ".ProfileHeader-headline": [
                MagicMock(text="一个测试简介", attrib={})
            ],
            ".ProfileHeader-avatar img": [
                MagicMock(
                    text="",
                    attrib={"src": "https://pic.zhimg.com/avatar.jpg"}
                )
            ],
            ".ProfileHeader-detailItem--location": [
                MagicMock(text="北京", attrib={})
            ],
            ".FollowshipCard-count": [
                MagicMock(text="1.2k", attrib={})
            ],
        }.get(sel, [])

        with patch(
            "clawithme.crawler.client.CrawlerClient.fetch_dynamic",
            return_value=mock_page,
        ):
            ex = ZhihuExtractor()
            profile = ex.extract(
                {"id": "zhihu", "name": "知乎"}, "testuser"
            )

        assert profile.site_id == "zhihu"
        assert profile.display_name == "测试用户"
        assert profile.bio == "一个测试简介"
        assert profile.avatar_url == "https://pic.zhimg.com/avatar.jpg"
        assert profile.location == "北京"
        assert profile.follower_count == 1200
        assert profile.empty is False

    @patch("clawithme.crawler.client.HttpClient")
    def test_extract_fetch_returns_none(self, mock_http_cls):
        mock_http = MagicMock()
        mock_http_cls.return_value = mock_http

        with patch(
            "clawithme.crawler.client.CrawlerClient.fetch_dynamic",
            return_value=None,
        ):
            ex = ZhihuExtractor()
            profile = ex.extract(
                {"id": "zhihu", "name": "知乎"}, "testuser"
            )

        assert profile.site_id == "zhihu"
        assert profile.empty is True

    @patch("clawithme.crawler.client.HttpClient")
    def test_extract_signin_redirect_returns_empty(self, mock_http_cls):
        mock_http = MagicMock()
        mock_http_cls.return_value = mock_http

        mock_page = MagicMock()
        mock_page.status = 200
        mock_page.url = "https://www.zhihu.com/signin?next=/people/testuser"
        mock_page.text = ""

        with patch(
            "clawithme.crawler.client.CrawlerClient.fetch_dynamic",
            return_value=mock_page,
        ):
            ex = ZhihuExtractor()
            profile = ex.extract(
                {"id": "zhihu", "name": "知乎"}, "testuser"
            )

        assert profile.site_id == "zhihu"
        assert profile.empty is True

    @patch("clawithme.crawler.client.HttpClient")
    def test_extract_404_returns_empty(self, mock_http_cls):
        mock_http = MagicMock()
        mock_http_cls.return_value = mock_http

        mock_page = MagicMock()
        mock_page.status = 404
        mock_page.url = "https://www.zhihu.com/people/nonexistent"

        with patch(
            "clawithme.crawler.client.CrawlerClient.fetch_dynamic",
            return_value=mock_page,
        ):
            ex = ZhihuExtractor()
            profile = ex.extract(
                {"id": "zhihu", "name": "知乎"}, "nonexistent"
            )

        assert profile.site_id == "zhihu"
        assert profile.empty is True
