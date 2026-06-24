# Tool设计
> 我觉得Tool的设计是三分之一。稳定的能力还是通过Tool实现。LLM是三分之一，提供泛化能力。Agent是三分之一，提供编排能力。

## Tool定义
* <Input extends AnyObject, Output, P extends ToolProgressData>
* 要素
    * 名称与别名：向后兼容
    * Zod Schema：入参数可控
    * 权限模型：输入验证、权限检查、运行时（并发）
    * 执行逻辑：它接收解析后的输入参数、工具使用上下文、权限检查函数、父消息引用和一个可选的进度回调。返回的结果携带输出数据和可选的上下文修改器。
    * UI渲染：很多歌渲染方法。

## 注册
* getAllBaseTools() 完整工具清单
* ToolSearchTool 延迟发现机制

## 核心工具
* BashTool：集成了多层安全防护的执行环境。还会分析是否为搜索/读取操作，用于UI展示。
* FileReadTool、FileEditTool、FileWriteTool：维护了文件状态缓存；编辑用字符串替换而非行号；写是覆盖。三者都可以更改contextModifier，修改缓存。
* GlobTool、GrepTool：文件名搜索、正则搜索内容。
* AgentTool：允许主智能体生成子智能体来处理子任务。子智能体拥有独立的上下文窗口和工具集，执行完成后将结果返回给主智能体。

## 工具执行
* runTools()：异步生成器，负责调度一批工具调用的执行。
    * 算法是：并发分区——能并发的合并然后并发、不能的串行；整体保证时序正确。
