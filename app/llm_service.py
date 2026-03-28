import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.exceptions import AppError

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

if OPENAI_BASE_URL:
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
else:
    client = OpenAI(api_key=OPENAI_API_KEY)


#日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

"""
=================================================
            辅助函数
=================================================
"""
def clean_json_text(raw_text: str) -> str:
    """
    获取清洗格式后的字符串
    """
    #strip() 是 Python 中字符串（str）类型的一个内置方法，它的主要作用是移除字符串首尾的指定字符。
    #如果不指定字符，默认会移除所有的空白字符，包括空格、制表符（\t）、换行符（\n）等。
    text = raw_text.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()
    elif text.startswith("```"):
        text = text.removeprefix("```").strip()

    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    return text

def normalize_extract_result(data: dict) -> dict:
    todos = data.get("todos", [])
    time_info = data.get("time_info", [])
    topic = data.get("topic", "")

    if isinstance(todos, str):
        todos = [todos]
    elif not isinstance(todos, list):
        todos = []

    if isinstance(time_info, str):
        time_info = [time_info]
    elif not isinstance(time_info, list):
        time_info = []

    if isinstance(topic, list):
        topic = ";".join(str(x) for x in topic)
    elif not isinstance(topic, str):
        topic = ""

    todos = [str(x) for x in todos]
    time_info = [str(x) for x in time_info]
    topic = str(topic)

    return {
        "todos": todos,
        "time_info": time_info,
        "topic": topic,
    }


def ensure_llm_config() -> None:
    if not OPENAI_API_KEY:
        raise AppError("CONFIG_ERROR", "服务端未配置 OPENAI_API_KEY")
    if not OPENAI_MODEL:
        raise AppError("CONFIG_ERROR", "服务端未配置 OPENAI_MODEL")

"""
=================================================
            大模型调用区域
=================================================
"""
#提示词
prompt_map = {
    "teacher":"你是一个专业的AI应用开发导师，请回答清晰、简洁、偏实战。",
    "coach": "你是一位转型教练，擅长帮助iOS 开发者转向 AI 应用开发，请给出鼓励性、落地性的建议。",
    "simple": "你是一个简洁的AI助手，请直接回答重点，尽量少废话。",
    "interviewer": "你是一位技术面试官，请从工厂实践和面试表达角度回答。",
}

def build_system_propmt(style: str) -> str:
    """
    给定身份 返回 系统提示词
    """
    return prompt_map.get(style, prompt_map["teacher"])


def chat_with_llm(message: str,history: list[dict] | None = None, style: str = "teacher") -> tuple[str, str]:
    '''
    聊天对话请求接口模型
    返回：（ai_message, model_name）模型返回的结果 和 用的模型名
    '''
    ensure_llm_config()

    system_propmt = build_system_propmt(style)
    history = history or []

    logging.info(
        f"开始调用模型 | model={OPENAI_MODEL} | style={style} | history_count={len(history)} | message={message}"
    )

    #发送给模型的消息
    messages = [
        {
            "role": "system",
            "content": system_propmt
        }
    ]

    #拼上历史信息
    if history :
        messages.extend(history)

    #拼上当前用户问的信息
    messages.append({
        "role": "user",
        "content": message,
    })

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.3,
    )

    ai_message = response.choices[0].message.content or ""

    logging.info(
        f"模型调用成功 | model={OPENAI_MODEL} | output_len={len(ai_message)}"
    )
    return ai_message, OPENAI_MODEL

#
def summary_text(content: str, max_sentences:int = 3) -> tuple[str, str]:
    """
    总结分析接口请求模型
    return：（summary_message, model_name）模型返回的结果 和 用的模型名
    """
    ensure_llm_config()

    summary_prompt = (
        "你是一名专业的信息总结助手"
        "请根据用户提供的内容，输出清晰、准确、简洁的中文总结。"
        "不要胡乱扩展，不要输出与原文无关的信息。"
    )

    user_prompt = (
        f"请将下面内容总结为不超过{max_sentences} 句话:\n\n"
        f"{content}"
    )

    logging.info(
        f"开始调用总结模型 | model={OPENAI_MODEL} | input_len={len(content)} | max_sentences={max_sentences}"
    )

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {'role': 'system', 'content': summary_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=0.2
    )

    summary_message = response.choices[0].message.content or ""

    logging.info(f"调用模型成功 | model={OPENAI_MODEL} | output_len={len(summary_message)}")
    return summary_message, OPENAI_MODEL


def rewrite_text(content: str, tone:str = "professional") -> tuple[str, str]:
    """
    return (rewritten_text, model_name)
    """
    ensure_llm_config()

    tone_prompt_map = {
        "formal": "请将用户提供的内容改写为正式、书面化表达。",
        "simple": "请将用户提供的内容改写得更简单、更直接、更容易理解。",
        "friendly": "请将用户提供的内容改写得更自然、友好、亲切。",
        "professional": "请将用户提供的内容改写得更专业、清晰、适合工作沟通。"
    }

    tone_prompt = tone_prompt_map.get(tone, tone_prompt_map["professional"])

    system_propmt = (
        "你是一名专业的文本改写助手。"
        "请保持原意不变，只优化表达方式。"
        "不要擅自添加原文没有的信息。"
    )

    user_prompt = (
        f'{tone_prompt}\n\n'
        f'原文如下: \n{content}'
    )

    logger.info(f'开始调用改写模型 | model={OPENAI_MODEL} | tone={tone} | input_len={len(content)}')

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {'role': 'system', 'content': system_propmt},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=0.3
    )

    rewritten_messages = response.choices[0].message.content or ""

    logging.info(f'改写模型调用成功 | model={OPENAI_MODEL} | output_len={len(rewritten_messages)}')

    return rewritten_messages, OPENAI_MODEL


def extract_info(content: str) -> tuple[dict, str]:
    """
    提取助手接口请求模型
    """
    ensure_llm_config()

    system_prompt = (
        "你是一名信息提取助手。"
        "请从用户输入的文本中提取待办事项、时间信息和核心主题。"
        "请严格输出 JSON，不要输出额外解释。"
        '输出格式为：{"todos": [...], "time_info": [...], "topic": "..."}'
    )

    logger.info(f'开始调用提取模型 | model={OPENAI_MODEL} | input_len={len(content)}')

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': content}
        ],
        temperature=0.1
    )

    raw_result = response.choices[0].message.content or ""

    cleaned_text = clean_json_text(raw_result)

    logging.info(
        f'提取模型调用成功 | model={OPENAI_MODEL} | input_len={len(raw_result)}'
    )

    try:
        parsed = json.loads(cleaned_text)
    except Exception:
        raise AppError("INVALID_MODEL_OUTPUT", f"模型没有返回合法 JSON: {raw_result}")

    normalized = normalize_extract_result(parsed)
    return normalized, OPENAI_MODEL
