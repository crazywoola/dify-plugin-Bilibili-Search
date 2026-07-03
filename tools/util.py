import time
import urllib.parse
from functools import reduce
from hashlib import md5
from http.cookies import SimpleCookie
from typing import Any

import httpx

from tools.model import SearchResult, VideoResult

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "dnt": "1",
    "pragma": "no-cache",
    "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
}

# fmt: off
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]
# fmt: on


def get_mixin_key(orig: str) -> str:
    return reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, "")[:32]


def enc_wbi(params: dict, img_key: str, sub_key: str) -> dict:
    mixin_key = get_mixin_key(img_key + sub_key)
    params["wts"] = round(time.time())
    params = dict(sorted(params.items()))
    params = {
        k: "".join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v in params.items()
    }
    query = urllib.parse.urlencode(params)
    params["w_rid"] = md5((query + mixin_key).encode()).hexdigest()
    return params


def get_wbi_keys() -> tuple[str, str]:
    resp = httpx.get("https://api.bilibili.com/x/web-interface/nav", headers=HEADERS)
    resp.raise_for_status()
    json_content = resp.json()
    img_url: str = json_content["data"]["wbi_img"]["img_url"]
    sub_url: str = json_content["data"]["wbi_img"]["sub_url"]
    img_key = img_url.rsplit("/", 1)[1].split(".")[0]
    sub_key = sub_url.rsplit("/", 1)[1].split(".")[0]
    return img_key, sub_key


def get_signed_params(params: dict) -> dict:
    img_key, sub_key = get_wbi_keys()
    return enc_wbi(params, img_key, sub_key)


def parse_cookies(cookie_str: str) -> dict[str, str]:
    cookie = SimpleCookie()
    cookie.load(cookie_str)
    return {key: morsel.value for key, morsel in cookie.items()}


def coerce_page(value: Any, default: int = 1) -> int:
    """Coerce a page parameter to a positive int, falling back to `default`.

    LLM-filled number parameters may arrive as strings or garbage
    (e.g. the search keyword); never let that crash the tool.
    """
    try:
        page = int(float(value))
    except (TypeError, ValueError):
        return default
    return max(page, 1)


def search_bilibili(
    keyword: str, page: int, cookies: dict, type: str = "video"
) -> SearchResult:
    url = "https://api.bilibili.com/x/web-interface/wbi/search/type"

    params = {
        "keyword": keyword,
        "page": page,
        "search_type": type,
    }

    with httpx.Client() as client:
        response = client.get(
            url=url,
            headers=HEADERS,
            params=get_signed_params(params),
            cookies=cookies,
        )
        response.raise_for_status()

    return SearchResult.model_validate(response.json())


def get_video_info(bvid: str, cookies: dict) -> VideoResult:
    url = "https://api.bilibili.com/x/web-interface/view"

    params = {
        "bvid": bvid,
    }

    with httpx.Client() as client:
        response = client.get(
            url=url,
            headers=HEADERS,
            params=get_signed_params(params),
            cookies=cookies,
        )
        response.raise_for_status()

    return VideoResult.model_validate(response.json())
