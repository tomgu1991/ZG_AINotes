# mcp-demo: search_paper
> [MCP: Build Rich-Context AI Apps with Anthropic](https://www.deeplearning.ai/short-courses/mcp-build-rich-context-ai-apps-with-anthropic/)

## 环境
依赖uv，nodejs
```
uv init
uv venv
.venv/bin/python3 --version
uv add mcp arxiv
```

## 测试Server
Note: A server using the stdio transport is launched as a subprocess by the MCP client. On the other hand, a remote server is an independent processes running separately from the client and needs to be already running before the MCP client connects to it.
### 本地server
```
npx @modelcontextprotocol/inspector uv run server.py
```

1. 点击左侧的Connect
2. 选择主页面的Resource/Prompt/Tools
3. 可以看到具体的内容

### SSE-server
```
第一个terminal
> uv run sse_server.py
INFO:     Started server process [82535]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
此时，可以打开浏览器输入：http://127.0.0.1:8001/sse 查看状态

第二个terminal
npx @modelcontextprotocol/inspector
然后在URL里面设置http://127.0.0.1:8001/sse，类型选择sse即可
```


## Client
```
uv add anthropic python-dotenv nest_asyncio
uv run mcp_chatbot.py // 这个走不通，买不到key
uv run mcp_chatbot_deepseek.py // 这个可以
```

使用hunyuan模型调用tools，参考test_hunyuan_tools.py
```
uv run test_hunyuan_tools.py
```