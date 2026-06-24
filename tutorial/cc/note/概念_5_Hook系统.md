# Hook-生命周期管理

> 观察者模式（Observer Pattern）结合责任链模式（Chain of Responsibility）
> 
> 每个生命周期事件就是一个"信号"，多个钩子可以监听同一个信号，按优先级依次处理，任何一个钩子都可以选择"阻断信号传播"。

1. 5种Hook：
    * Command：Shell、脚本检查
    * Prompt：LLM推理、内容审核
    * Agent：LLM多步、测试验证
    * HTTP：网络请求、CI集成
    * Function：回调函数、运行时拦截
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "python3 scripts/validate_command.py",
        "timeout": 5000,
        "message": "Validating bash command safety..."
      }]
    }]
  }
}

{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "prompt",
        "prompt": "Analyze this file write operation. If it modifies any file in src/core/, respond with {\"decision\": \"block\", \"reason\": \"Core module changes require code review\"}. Otherwise respond with {\"decision\": \"approve\"}. Input: $ARGUMENTS"
      }]
    }]
  }
}
```
2. 生命周期事件：
    * 覆盖工具调用、用户交互、会话管理、子代理、压缩、权限、配置变更等完整的 Agent 生命周期。每个事件都有明确的触发时机、输入结构和退出码语义。
3. 协议：输出是一个结构化的JSON。
    * decision：approve/block
    * 其他特定生命周期事件的字段