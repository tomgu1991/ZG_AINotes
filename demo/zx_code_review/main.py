import argparse
from pathlib import Path
from hello_agents import SimpleAgent, HelloAgentsLLM
from typing import Dict, Any, List
import os

from wandb import agent
from python_cr import PyCodeAnalysisTool, PyStyleCheckTool
from hello_agents import ToolRegistry

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

def run_python_code_review(input_file: Path):
    print("Running Python code review...")
    # 创建工具注册表
    tool_registry = ToolRegistry()
    tool_registry.register_tool(PyCodeAnalysisTool())
    tool_registry.register_tool(PyStyleCheckTool())

    # 初始化LLM
    llm = HelloAgentsLLM()

    # 定义系统提示词
    system_prompt = """你是一位经验丰富的代码审查专家。你的任务是：

    1. 使用code_analysis工具分析代码结构, 并打印工具的原始结果
    2. 使用style_check工具检查代码风格，并打印工具的原始结果
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

    print("=== 待审查的代码 ===")
    print(sample_code)
    print("\n" + "="*50 + "\n")
    # res = PyCodeAnalysisTool().run({"code": sample_code})
    # print(f"代码分析工具结果: {res}")


    print("=== 开始代码审查 ===")
    review_result = agent.run(f"请审查以下Python代码:\n\n```python\n{sample_code}\n```\n\n\
                              注意parameters字段如果code,那么用code=r\"\" 来传递代码内容。")
    print(review_result)

    # 保存审查报告
    Path("outputs").mkdir(parents=True, exist_ok=True)
    with open("outputs/review_report_py.md", "w", encoding="utf-8") as f:
        f.write(review_result)

    print("\n✅ 审查报告已保存到 outputs/review_report_py.md")
    pass

def main():
    print("Hello from zx-code-review!")
    init_env()
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--lang", type=str, help="语言", default="py", required=True)
    arg_parser.add_argument("--input", type=Path, help="输入文件", required=True)
    args = arg_parser.parse_args()
    if args.lang == "py":
        run_python_code_review(args.input)
    else:
        print(f"不支持的语言: {args.lang}")
    pass


if __name__ == "__main__":
    main()
