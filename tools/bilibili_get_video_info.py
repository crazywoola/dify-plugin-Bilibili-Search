from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.util import get_video_info, parse_cookies


class BilibiliGetVideoInfoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        bvid = tool_parameters.get("bvid")
        if not bvid:
            raise ValueError("BVID is required")

        cookies = self.runtime.credentials.get("cookies")
        if not cookies:
            raise ValueError("Bilibili cookies are not configured")

        res = get_video_info(
            bvid=bvid,
            cookies=parse_cookies(cookies),
        )

        yield self.create_json_message(res.data.model_dump())
