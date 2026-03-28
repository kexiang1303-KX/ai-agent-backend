from app.llm_service import summary_text,extract_info
from app.rules import infer_priority

def build_meet_digest(content: str, max_sentences: int = 3) -> tuple[dict, str]:
    """
    返回: (meeting_digest_data, model_name)
    meeting_digest_data:
    {
        "summary": "...",
        "todos": [...],
        "time_info": [...],
        "topic": "...",
        "meta": {...}
    }
    """
    summary_result, model_name = summary_text(
        content=content,
        max_sentences=max_sentences
    )

    extract_result, _ = extract_info(
        content=content,
    )
    todos = extract_result.get("todos",[])
    time_info = extract_result.get("time_info",[])
    topic = extract_result.get("topic","")

    result = {
        "summary": summary_result,
        "todos": todos,
        "time_info": time_info,
        "topic": topic,
        "meta": {
            "input_length": len(content),
            "todo_count": len(todos),
            "summary_length": len(summary_result),
            "max_sentences": max_sentences
        }
    }

    return result, model_name


def build_task_brief(content: str, max_sentences: int = 2) -> tuple[dict, str]:
    """
    :param content:输入内容
    :param max_sentences: 最大句数
    :return: 大模型返回的result拼接
    """
    summary_result, model_name = summary_text(
        content=content,
        max_sentences=max_sentences
    )

    extract_result, _ = extract_info(
        content=content,
    )
    todos = extract_result.get("todos", [])
    time_info = extract_result.get("time_info", [])
    topic = extract_result.get("topic", "")

    priority = infer_priority(content,time_info)

    result = {
        "summary": summary_result,
        "todos": todos,
        "time_info": time_info,
        "topic": topic,
        "priority": priority,
        "meta": {
            "input_length": len(content),
            "summary_length": len(summary_result),
            "todo_count": len(todos),
            "has_time_info": len(time_info) > 0,
        }
    }

    return result, model_name


