# ===== 统一接口成功返回 基础类 =====
def success_response(data: dict, code: int = 0, message: str = "success"):
    return {
        "code": code,
        "message": message,
        "data": data,
    }

#这意味着在 * 之后定义的所有参数（即 model, meta, original_content, extra），
#在调用函数时必须使用关键字（即参数名）来传递，不能使用位置参数。
def build_ai_data(
        *,
        model: str,
        meta: dict,
        original_content: str | None = None,
        extra: dict | None = None
) -> dict:
    """
    :param model:            #模型名
    :param meta:             #长度信息
    :param original_content: #原始文本
    :param extra:            #这个接口特有的字段
    :return:                 #返回对应的response
    """
    data = {
        "model": model,
        "meta": meta,
    }

    if original_content is not None :
        data["original_content"] = original_content

    if extra is not None :
        data.update(extra)

    return data