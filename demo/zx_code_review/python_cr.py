from pathlib import Path
from hello_agents.tools import Tool, ToolParameter
from typing import Dict, Any, List
import ast
from hello_agents import SimpleAgent, HelloAgentsLLM
from typing import Dict, Any, List
import os
from hello_agents import ToolRegistry

# 快速演示 - 定义简单的代码分析工具
class PyCodeAnalysisTool(Tool):
    """代码静态分析工具"""

    def __init__(self):
        super().__init__(
            name="code_analysis",
            description="快速分析Python代码结构"
        )
    
    def run(self, parameters: Dict[str, Any]) -> str:
        """分析代码并返回结果"""
        file_path = parameters.get("file_path", "")
        if not file_path:
            return "错误：文件路径不能为空"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                tree = ast.parse(code)

                # 统计信息
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

                result = {
                    "函数数量": len(functions),
                    "类数量": len(classes),
                    "代码行数": len(code.split('\n')),
                    "函数列表": [f.name for f in functions],
                    "类列表": [c.name for c in classes]
                }
                print(f"PyQuickAnalysisTool run result: {result}")
                return str(result)
        except SyntaxError as e:
            return f"语法错误：{code}, {str(e)}"
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type="string",
                description="要分析的Python文件路径",
                required=True
            )
        ]

class PyStyleCheckTool(Tool):
    """代码风格检查工具"""

    def __init__(self):
        super().__init__(
            name="style_check",
            description="检查代码是否符合自定义规则"
        )

    def run(self, parameters: Dict[str, Any]) -> str:
        """检查代码风格"""
        file_path = parameters.get("file_path", "")
        if not file_path:
            return "错误：文件路径不能为空"
        
        issues = []

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                # 检查行长度
                if len(line) > 79:
                    issues.append(f"第{i}行：超过79个字符")

                if line.__contains__('return True'):
                    issues.append(f"第{i}行：使用了return True")

                # 检查缩进
                if line.startswith(' ') and not line.startswith('    '):
                    if len(line) - len(line.lstrip()) not in [0, 4, 8, 12]:
                        issues.append(f"第{i}行：缩进不规范")

        if not issues:
            return "代码风格良好，符合PEP 8规范"
        return "发现以下问题：\n" + "\n".join(issues)
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type="string",
                description="要检查的Python文件路径",
                required=True
            )
        ]

def init_env():
    os.environ["LLM_MODEL_ID"] = "deepseek-chat"
    os.environ["LLM_API_KEY"] = os.environ.get("DEEPSEEK_AI_KEY", "")
    os.environ["LLM_BASE_URL"] = "https://api.deepseek.com"
    os.environ["LLM_TIMEOUT"] = "60"
    print("✅ 库导入和配置完成")
    print("✅ 环境配置完成")
    print(f"✅ 使用模型: {os.getenv('LLM_MODEL_ID')}")
    print(f"✅ API地址: {os.getenv('LLM_BASE_URL')}")
    pass

def run_python_code_review(input_file: str):
    init_env()
    print("Running Python code review...")
    # 创建工具注册表
    tool_registry = ToolRegistry()
    tool_registry.register_tool(PyCodeAnalysisTool())
    tool_registry.register_tool(PyStyleCheckTool())

    # 初始化LLM
    llm = HelloAgentsLLM()

    # 定义系统提示词
    system_prompt = """你是一位经验丰富的代码审查专家。你的任务是：

    1. 使用code_analysis工具分析代码结构, 并打印工具的原始结果。注意参数名为file_path，值为待审查的代码文件路径
    2. 使用style_check工具检查代码风格, 并打印工具的原始结果。注意参数名为file_path，值为待审查的代码文件路径
    3. 基于分析结果，提供详细的审查报告

    审查报告仅需要包括如下三个方面：
    - 代码结构分析: 需包含PyCodeAnalysisTool工具的结果
    - 风格问题: 需包含PyStyleCheckTool工具的结果
    - 潜在bug，列举<问题描述> 和 <代码内容>

    请以Markdown格式输出报告。"""

    # 创建智能体
    agent = SimpleAgent(
        name="代码审查助手",
        llm=llm,
        system_prompt=system_prompt,
        tool_registry=tool_registry
    )

    print("✅ 智能体创建完成")
    print(f"智能体名称: {agent.name}")
    print(f"可用工具: {list(tool_registry._tools.keys())}")

    # 读取示例代码

    with open(input_file, "r", encoding="utf-8") as f:
        sample_code = f.read()

    print("=== 待审查的代码路径 ===")
    print(input_file)
    print("\n" + "="*50 + "\n")
    print("=== 待审查的代码 ===")
    print(sample_code)
    print("\n" + "="*50 + "\n")

    print("=== 开始代码审查 ===")
    review_result = agent.run(f"请审查以下Python代码文件: {input_file}")
    print("=== 代码审查结果 ===")
    print(review_result)

    # 保存审查报告
    Path("outputs").mkdir(parents=True, exist_ok=True)
    with open("outputs/review_report_py.md", "w", encoding="utf-8") as f:
        f.write(review_result)

    print("\n✅ 审查报告已保存到 outputs/review_report_py.md")
    pass