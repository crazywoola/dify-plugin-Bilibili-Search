from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.util import coerce_page, parse_cookies, search_bilibili


class BilibiliSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        keyword = tool_parameters.get("keyword")
        if not keyword:
            raise ValueError("Keyword is required")

        page = coerce_page(tool_parameters.get("page", 1))

        cookies = self.runtime.credentials.get("cookies")
        if not cookies:
            raise ValueError("Bilibili cookies are not configured")

        res = search_bilibili(
            keyword=keyword,
            page=page,
            cookies=parse_cookies(cookies),
        )

        yield self.create_json_message(res.data.model_dump())
