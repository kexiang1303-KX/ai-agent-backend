def infer_priority(content: str, time_info: list[str]) -> str:
    """
    根据信息内容和提取出的时间信息，判断任务优先级。
    返回值：
    - high
    - medium
    """
    text = content.strip()

    #紧急度 关键字
    URGENT_KEYWORDS = ["今天","明天","本周","下周","尽快","截止","马上","立即"]

    if time_info:
        return "high"

    if any(keyword in text for keyword in URGENT_KEYWORDS):
        return "high"

    return "medium"
