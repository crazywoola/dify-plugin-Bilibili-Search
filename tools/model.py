from pydantic import BaseModel, Field


class VideoSearchData(BaseModel):
    type: str
    typename: str
    bvid: str
    title: str
    description: str
    pic: str
    play: int
    review: int
    pubdate: int
    duration: str
    rank_score: int | None = None
    like: int


class SearchData(BaseModel):
    seid: str
    page: int
    pagesize: int
    numResults: int
    numPages: int
    result: list[VideoSearchData] = Field(default_factory=list)


class SearchResult(BaseModel):
    code: int
    message: str
    ttl: int
    data: SearchData


class VideoOwner(BaseModel):
    mid: int
    name: str
    face: str


class VideoStats(BaseModel):
    aid: int
    view: int
    danmaku: int
    reply: int
    favorite: int
    coin: int
    share: int
    now_rank: int
    his_rank: int
    like: int
    dislike: int | None = None
    evaluation: str | None = None
    vt: int | None = None


class VideoData(BaseModel):
    bvid: str
    tname: str
    tname_v2: str | None = None
    pic: str
    title: str
    pubdate: int
    ctime: int
    desc: str
    owner: VideoOwner
    stat: VideoStats


class VideoResult(BaseModel):
    code: int
    message: str
    ttl: int
    data: VideoData
