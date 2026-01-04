# mcp-demo: search_paper
> [MCP: Build Rich-Context AI Apps with Anthropic](https://www.deeplearning.ai/short-courses/mcp-build-rich-context-ai-apps-with-anthropic/)

1. 环境
依赖uv，nodejs
```
uv init
uv venv
.venv/bin/python3 --version
uv add mcp arxiv
```

2. 测试Server
```
npx @modelcontextprotocol/inspector uv run server.py
```

1. 点击左侧的Connect
2. 选择主页面的Resource/Prompt/Tools
3. 可以看到具体的内容

3. Client
```
uv add anthropic python-dotenv nest_asyncio
uv run mcp_chatbot.py
```
TBD：需要api_key(试图用hunyuan的接口替换失败，可能API用的不对或者能力不支持)