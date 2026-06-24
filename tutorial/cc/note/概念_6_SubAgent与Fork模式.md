# 子智能体与Fork机制

## 子智能体
1. 子智能体：智能体唯一标识符（agentType）、使用场景描述（whenToUse）、允许/禁止的工具列表、预加载的 skill 名称、智能体专属 MCP 服务器、生命周期钩子、UI 显示颜色、模型指定、推理努力程度、权限模式、最大轮次限制、是否后台运行、隔离模式、是否省略 CLAUDE.md 上下文等。
2. 三种智能体：BuiltInAgentDefinition（内置智能体）、CustomAgentDefinition（自定义智能体）、PluginAgentDefinition（插件智能体）
3. 内置智能体：特定领域的专家。
    * Explore Agent：只读代码
    * Plan Agent
    * General Purpose Agent：通用智能体
    * Verification Agent：验证智能体

https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/04-quality-security/code-reviewer.md

```
1. 你输入“请帮我做 code review”
2. 主 Agent 判断代码审查任务非常适合这个 Subagent 的专长，它就会自动将任务委托出去
3. Task 工具会为 code-reviewer Subagent 创建一个全新的、独立的工作环境
4. Subagent 会加载它自己的系统提示词（你在 code-reviewer.md 中定义的规则），并且只能使用你在配置中允许它使用的工具
4.1 准备环节，根据配置去找skill/mcp
{
  "requesting_agent": "code-reviewer",
  "request_type": "get_review_context",
  "payload": {
    "query": "Code review context needed: ..."
  }
}
5. 当 Subagent 完成审查后，它的工作环境会关闭，并将最终审查结果通过 Task 工具的返回值，作为一个字符串传回给主 Agent.
5.1 过程中或者完成的时候，根据配置返回结果
{
  "agent": "code-reviewer",
  "status": "reviewing",
  "progress": {
    "files_reviewed": 47,
    "issues_found": 23,
    "critical_issues": 2,
    "suggestions": 41
  }
}
```

## Fork模式
1. 允许主智能体将同一时刻的完整上下文"分叉"给多个并行子任务，同时利用 Anthropic API 的 prompt cache 机制避免重复传输大量 token。
2. 首先保留完整的父 assistant 消息（包含所有 tool_use 块、thinking、text，但分配新的 UUID）；然后收集所有 tool_use 块；为每个 tool_use 生成统一的固定字符串占位符 tool_result；最后构建单条 user 消息，包含占位符结果和子任务指令。