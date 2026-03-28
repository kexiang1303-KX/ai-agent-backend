from pydantic import BaseModel,Field
from typing import Literal


"""
    ===== 请求模型 =====
"""
class EchoRequest(BaseModel):
    text: str

class AnalyzeRequest(BaseModel):
    content: str
    mode: str

class ChatHistoryItem(BaseModel):
    role: Literal["user", "system", "developer", "assistant"] # 注意：原图拼写错误 developer -> developer
    content: str = Field(..., min_length=1,max_length=2000)

class ChatRequest(BaseModel):
    message: str = Field(...,min_length=1,max_length=2000)
    history: list[ChatHistoryItem] = []
    style: Literal["teacher", "coach", "simple","interviewer"] = "teacher" #默认 teacher

class SummaryRequest(BaseModel):
    content: str = Field(..., min_length=1,max_length=6000)
    max_sentences: int = Field(3, ge=1, le=10)  #默认值3，最小1 最大10

class RewriteRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
    tone: Literal["formal", "simple", "friendly", "professional"] = "professional" #默认职业

class ExtractRequest(BaseModel):
    content: str = Field(..., min_length=1,max_length=4000)

class MeetingDigestRequest(BaseModel):
    content: str = Field(..., min_length=1,max_length=8000)
    max_sentences: int = Field(3, ge=1, le=10)

class TaskBriefRequest(BaseModel):
    content: str = Field(..., min_length=1,max_length=4000)
    max_sentences: int = Field(2, ge=1, le=5)

"""
    ===== data 模型 =====
"""
class InfoData(BaseModel):
    service_name: str
    version: str
    default_model: str
    endpoints: list[str]

class HealthData(BaseModel):
    status: str

class PingData(BaseModel):
    message: str
    status: str

class PriceData(BaseModel):
    symbol: str
    mock_price: float
    source: str

class SearchData(BaseModel):
    keyword: str
    limit: int
    results: list[str]
    source: str

class EchoData(BaseModel):
    message: str
    length: str
    summary: str

class AnalyzeData(BaseModel):
    content: str
    mode: str
    summary: str

'''
    “聊天”
'''
class ChatMeta(BaseModel):
    style: str
    history_count: int
    user_message_length: int
    ai_message_length: int

class ChatData(BaseModel):
    user_message: str
    ai_message: str
    model: str
    meta: ChatMeta

'''
    “缩短信息”
'''
class SummaryMeta(BaseModel):
    input_length: int
    output_length: int
    max_sentences: int

class SummaryData(BaseModel):
    original_content: str
    summary: str
    model: str
    meta: SummaryMeta

'''
    “换个说法”
'''
class RewriteMeta(BaseModel):
    input_length: int
    output_length: int
    tone: str

class RewriteData(BaseModel):
    original_content: str
    rewritten_content: str
    model: str
    meta: RewriteMeta

'''
    "提取信息"
'''
class ExtractMeta(BaseModel):
    input_length: int
    todo_count: int

class ExtractData(BaseModel):
    original_content: str
    todos : list[str] #需求列表
    time_info: list[str] #时间信息
    topic: str    #主题
    model: str
    meta: ExtractMeta

class MeetingDigestMeta(BaseModel):
    input_length: int
    summary_length: int
    todo_count: int
    max_sentences: int

class MeetingDigestData(BaseModel):
    original_content: str
    summary: str
    todos: list[str]
    time_info: list[str]
    topic: str
    model: str
    meta: MeetingDigestMeta

class TaskBriefMeta(BaseModel):
    input_length: int           #输入长度
    summary_length: int         #概要长度
    todo_count: int             #需求个数
    has_time_info: bool

class TaskBriefData(BaseModel):
    original_content: str       #输入原文
    summary: str                #概要总结
    todos : list[str]           #需求列表
    time_info: list[str]        #时间相关信息
    topic: str                  #主题
    priority: str               #优先级
    model: str
    meta: TaskBriefMeta
"""
    ===== 各接口的 response 模型 =====
"""
class InfoResponse(BaseModel):
    code: int
    message: str
    data: InfoData

class HealthResponse(BaseModel):
    code: int
    message: str
    data: HealthData

class TaskBriefResponse(BaseModel):
    code: int
    message: str
    data: TaskBriefData

class MeetingDigestResponse(BaseModel):
    code: int
    message: str
    data: MeetingDigestData

class ExtractResponse(BaseModel):
    code: int
    message: str
    data: ExtractData

class RewriteResponse(BaseModel):
    code: int
    message: str
    data: RewriteData

class SummaryResponse(BaseModel):
    code: int
    message: str
    data: SummaryData

class ChatResponse(BaseModel):
    code: int
    message: str
    data: ChatData


class PingResponse(BaseModel):
    code: int
    message: str
    data: PingData


class PriceResponse(BaseModel):
    code: int
    message: str
    data: PriceData


class SearchResponse(BaseModel):
    code: int
    message: str
    data: SearchData


class EchoResponse(BaseModel):
    code: int
    message: str
    data: EchoData


class AnalyzeResponse(BaseModel):
    code: int
    message: str
    data: AnalyzeData



class MarketData:
    def __init__(self,symbol,price,exchange,is_hot):
        self.symbol = symbol
        self.price = price
        self.exchange = exchange
        self.is_hot = is_hot


    def show_info(self):
        print("=== 市场数据 ===")
        print(f'交易对：{self.symbol}')
        print(f'价格：{self.price}')
        print(f'交易所：{self.exchange}')
        print(f"热门: {self.is_hot}")

    def is_price_high(self, threshold):
        return self.price > threshold

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "price": self.price,
            "exchange": self.exchange,
            "is_hot": self.is_hot
        }