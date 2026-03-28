# AI Agent iOS Backend

一个基于 FastAPI 构建的 AI 应用后端学习项目，用于练习 AI 接口封装、结构化输出、工作流编排、日志、错误处理和 API 版本化设计。

## 技术栈

- Python
- FastAPI
- Uvicorn
- OpenAI / OpenRouter API
- Pydantic

## 启动方式

### 1. 安装依赖
确保你已经创建虚拟环境并安装依赖。
```bash
uv sync
```

### 2. 配置环境变量
在项目根目录创建 `.env` 文件，并配置：

### 3. 启动服务
在虚拟环境 
```bash
uv run uvicorn app.main:app --reload
````

启动后访问:
- [Swagger 文档](http://127.0.0.1:8000/docs)
- [OpenAPI JSON](http://127.0.0.1:8000/openapi.json)

## 核心接口

- `POST /api/v1/chat`：基础聊天
- `POST /api/v1/summary`：文本总结
- `POST /api/v1/rewrite`：文本改写
- `POST /api/v1/extract`：信息提取
- `POST /api/v1/meeting_digest`：会议纪要整理
- `POST /api/v1/task_brief`：任务简报生成
- `GET /health`：健康检查
- `GET /info`：服务信息

## 请求示例
```json
{
  "content": "明天下午开会讨论需求。",
  "max_sentences": 2
}
```

### 文本总结

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "明天下午开会讨论需求。",
    "max_sentences": 2
  }'
```

### 任务简报生成
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/task_brief" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "这周需要把 FastAPI 的 /chat、/summary、/rewrite 接口联调完成，下周一前给 iOS 端测试地址，同时补齐欢迎页文案。",
    "max_sentences": 2
  }'
```
## 项目结构

```text
app/
  main.py               # 路由入口、middleware、启动逻辑
  models.py             # Pydantic 数据模型
  responses.py          # 统一成功响应结构
  llm_service.py        # 基础模型调用能力
  workflow_service.py   # 业务编排逻辑
  rules.py              # 本地规则判断
  exceptions.py         # 自定义异常类型
```

## 当前特性

- 统一成功响应结构
- 统一结构化错误返回
- 请求日志与异常日志
- 请求耗时响应头 `X-Process-Time-MS`
- 请求链路标识 `X-Request-ID`
- API 版本前缀 `/api/v1`
- 健康检查 `/health`
- 服务信息 `/info`

## 环境变量示例

```env
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=openai/gpt-5.2
