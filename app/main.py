import os

from app.models import (
    EchoRequest,
    AnalyzeRequest,
    ChatRequest,
    SummaryRequest,
    RewriteRequest,
    ExtractRequest,
    MeetingDigestRequest,
    TaskBriefRequest,
    PingResponse,
    PriceResponse,
    SearchResponse,
    EchoResponse,
    AnalyzeResponse,
    ChatResponse,
    SummaryResponse,
    RewriteResponse,
    ExtractResponse,
    MeetingDigestResponse,
    TaskBriefResponse,
    HealthResponse,
    InfoResponse
)

import time
import logging
import uuid

from fastapi import FastAPI,Query,HTTPException,Request
from contextlib import asynccontextmanager
from app.responses import success_response
from app.responses import build_ai_data

from app.llm_service import chat_with_llm, OPENAI_MODEL
from app.llm_service import summary_text
from app.llm_service import rewrite_text
from app.llm_service import extract_info

from app.workflow_service import build_meet_digest
from app.workflow_service import build_task_brief
from app.exceptions import AppError

APP_VERSION = "0.1.0"
SERVICE_NAME = "ai-agent-ios-backend"
API_PREFIX = "/api/v1"

#目前支持的接口名
SUPPORTED_ENDPOINTS = [
    f"{API_PREFIX}/chat",
    f"{API_PREFIX}/summary",
    f"{API_PREFIX}/rewrite",
    f"{API_PREFIX}/extract",
    f"{API_PREFIX}/meeting_digest",
    f"{API_PREFIX}/task_brief",
    "/health",
    "/info",
]

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    1.服务启动时 日志
    2.遇到 yield FastAPI 接管，应用开始正式运行。
    3.服务关闭时 执行yield 后面的

    :param _app: “这个参数是框架约定要传进来的，但我当前不用”
    :return:
    """
    logging.info("=== Application Startup ===")
    logging.info(f"Service Name: {SERVICE_NAME}")
    logging.info(f"Version: {APP_VERSION}")
    logging.info(f"Default Model: {OPENAI_MODEL}")
    logging.info(f"Supported Endpoints: {', '.join(SUPPORTED_ENDPOINTS)}")
    yield
    logging.info("=== Application Shutdown ===")

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def log_request(request: Request,call_next):
    """
    中间件 对FastAPI 请求做监听 记录时间 和 接口相关信息
    :param request:
    :param call_next:
    :return:
    """
    request_id = uuid.uuid4().hex[:12]
    request.state.request_id = request_id

    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    duration_ms = round(duration * 1000,2)
    response.headers["X-Process-Time-MS"] = str(duration_ms)
    response.headers["X-Request-ID"] = request_id

    logging.info(f"[{request_id}]{request.method} {request.url.path} -> {response.status_code} {duration_ms} ms")
    return response

def build_error_detail(error_code: str, error_message: str) -> dict:
    """
    编译报错详情
    """
    return {
        "error_code": error_code,
        "error_message": error_message
    }

def safe_service_call(func, error_prefix: str, *args, **kwargs):
    """
        统一处理接口 判断是否报错
    :param func: 接口方法
    :param error_prefix: 接口爆仓文案
    :param args:
    :param kwargs:
    :return: args kwargs
    """
    try:
        return func(*args, **kwargs)
    except AppError as e:
        logging.exception(f"{error_prefix} | AppError: {e.error_code} | {e.error_message}")
        message = str(e)

        raise HTTPException(
            status_code=500,
            detail = build_error_detail(
                error_code = e.error_code,
                error_message = message
            )
        )

    except Exception as e:
        logging.exception(f"{error_prefix} | Exception: {e}")
        raise HTTPException(
            status_code=500,
            detail=build_error_detail(
                error_code="MODEL_CALL_FAILED",
                error_message=f"{error_prefix}: {e}"
            )
        )



@app.get("/health",response_model=HealthResponse)
def health():
    """
    健康检查
    """
    return success_response({
        "status": "ok"
    })

@app.get("/info",response_model=InfoResponse)
def info():
    """
    服务信息
    """
    return success_response({
        "service_name": SERVICE_NAME,
        "version": APP_VERSION,
        "default_model": OPENAI_MODEL,
        "endpoints": SUPPORTED_ENDPOINTS
    })

@app.get("/ping", response_model=PingResponse)
def ping():
    return success_response({
            "message": "pong",
            "status": "ok"
        })



@app.post(f"{API_PREFIX}/chat",response_model=ChatResponse)
def chat(data: ChatRequest):
    history_messages = [
        {"role":item.role,"content":item.content} for item in data.history
    ]
    ai_message, model_name = safe_service_call(
        chat_with_llm,
        "大模型调用失败",
        message = data.message,
        history = history_messages,
        style = data.style
    )

    return success_response({
        "user_message": data.message,
        "ai_message": ai_message,
        "model": model_name,
        "meta": {
            "style": data.style,
            "history_count": len(data.history),
            "user_message_length": len(data.message),
            "ai_message_length": len(ai_message)
        }
    })

@app.post(f"{API_PREFIX}/summary",response_model=SummaryResponse)
def summary(data: SummaryRequest):
    summary_result,model_name = safe_service_call(
        summary_text,
        "总结模型调用失败",
        content = data.content,
        max_sentences = data.max_sentences
    )

    return success_response(
        build_ai_data(
            model= model_name,
            original_content=data.content,
            meta={
                "input_length": len(data.content),
                "output_length": len(summary_result),
                "max_sentences": data.max_sentences
            },
            extra={
                "summary": summary_result,
            }
        )
    )

@app.post(f"{API_PREFIX}/rewrite",response_model=RewriteResponse)
def rewrite(data: RewriteRequest):
    """
    文本改写 - 模型
    """
    rewritten_result,model_name = safe_service_call(
        rewrite_text,
        "改写模型调用失败",
        content = data.content,
        tone = data.tone
    )

    return success_response(
        build_ai_data(
            model= model_name,
            original_content=data.content,
            meta={
                "input_length": len(data.content),
                "output_length": len(rewritten_result),
                "tone": data.tone
            },
            extra = {
                "rewritten_content": rewritten_result
            }
        )
    )

@app.post(f"{API_PREFIX}/extract",response_model=ExtractResponse)
def extract(data: ExtractRequest):
    """
    信息提取 - 模型
    """
    extract_result,model_name = safe_service_call(
        extract_info,
        "提取模型调用失败",
        content = data.content
    )

    '''
        因为system 设定了 
        返回 '输出格式为：{"todos": [...], "time_info": [...], "topic": "..."}'
    '''
    todos = extract_result.get("todos",[])
    time_info = extract_result.get("time_info",[])
    topic = extract_result.get("topic","")

    return success_response(
        build_ai_data(
            model= model_name,
            original_content=data.content,
            meta={
                "input_length": len(data.content),
                "todo_count": len(todos)
            },
            extra={
                "time_info": time_info,
                "topic": topic,
                "todos": todos
            }
        )
    )


@app.post(f"{API_PREFIX}/meeting_digest",response_model=MeetingDigestResponse)
def meeting_digest(data: MeetingDigestRequest):
    """
    两个基础能力组合 - 会议纪要整理 模型
    :return MeetingDigestResponse
    """
    digest_result,model_name = safe_service_call(
        build_meet_digest,
        error_prefix="会议纪要整理失败",
        content = data.content,
        max_sentences = data.max_sentences
    )

    return success_response(
        build_ai_data(
            model= model_name,
            original_content=data.content,
            meta=digest_result["meta"],
            extra={
                "summary": digest_result["summary"],
                "todos": digest_result["todos"],
                "topic": digest_result["topic"],
                "time_info": digest_result["time_info"]
            }
        )
    )


@app.post(f"{API_PREFIX}/task_brief", response_model=TaskBriefResponse)
def task_brief(data: TaskBriefRequest):
    """
     两个基础能力组合 - 任务简报生成 模型
     :return TaskBriefResponse
     """
    task_brief_result,model_name = safe_service_call(
        build_task_brief,
        error_prefix="任务简报生成失败",
        content = data.content,
        max_sentences = data.max_sentences
    )

    return success_response(
        build_ai_data(
            model=model_name,
            original_content=data.content,
            meta=task_brief_result["meta"],
            extra={
                "summary": task_brief_result["summary"],
                "todos": task_brief_result["todos"],
                "topic": task_brief_result["topic"],
                "time_info": task_brief_result["time_info"],
                "priority": task_brief_result["priority"]
            }
        )
    )



