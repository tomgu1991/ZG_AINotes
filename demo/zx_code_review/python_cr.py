from hello_agents.tools import Tool, ToolParameter
from typing import Dict, Any, List
import ast

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
        code = parameters.get("code", "")
        if not code:
            return "错误：代码不能为空"
        
        try:
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
                name="code",
                type="string",
                description="要分析的Python代码",
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
        code = parameters.get("code", "")
        if not code:
            return "错误：代码不能为空"
        
        issues = []

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
                name="code",
                type="string",
                description="要检查的Python代码",
                required=True
            )
        ]