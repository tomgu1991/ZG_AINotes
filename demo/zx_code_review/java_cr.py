import json
from typing import List, Mapping
from openai import OpenAI
from tree_sitter import Language, Parser
import tree_sitter_java as java
import os

JAVA_SYSTEM_PROMPT = """
你是一个很好的Java代码审查员。只关注当前函数里面所有除零的错误,如果有多个位置发生错误，那么都返回。
你的输入有两部分：
<method_line>=函数声明所在的行号
<method_name>=当前函数的名称，包含参数类型以区分重载
<method_content>=当前函数的内容，包含注释


你的输出格式为json，包含以下字段：
{
  [
    method_line: int, // 方法所在行号
    method_name: str, // 方法名称
    result: bool, // 是否存在问题,true表示存在问题，false表示没有问题
    code: str // 如果存在问题，返回发生除零所在行的代码片段; 如果没有问题，返回空字符串
    explanation: str // 如果存在问题，解释问题所在；如果没有问题，说明代码没有问题
    possibility: float // 问题可能性的概率，取值范围0~1，
  ]
}
特别的说明:对于possibility越接近1表示越有可能存在问题。当明确变量初始化为0时或者代码里面有值与零比较的情况，结果越大；如果是外部输入的变量，结果越小。

比如:
{
  [
    method_line: 3, // 方法所在行号
    method_name: "divide", // 方法名称
    result: true, // 是否存在问题,true表示存在问题，false表示没有问题
    code: "int x = y / b;", // 如果存在问题，返回代码片段; 如果没有问题，返回空字符串
    explanation: "除零错误：在第5行，变量b初始化为0，导致除法运算异常",
    possibility: 0.9 // 问题可能性的概率，取值范围0~1，
  ],
  [
    method_line: 3, // 方法所在行号
    method_name: "divide2", // 方法名称
    result: true, // 是否存在问题,true表示存在问题，false表示没有问题
    explanation: "除零错误：在第5行，变量b是外部输入并且有复杂计算过程，导致除法运算异常",
    code: "int x = y / b;", // 如果存在问题，返回代码片段; 如果没有问题，返回空字符串
    possibility: 0.1 // 问题可能性的概率，取值范围0~1，
  ],
  [
    method_line: 15, // 方法所在行号
    method_name: "add", // 方法名称
    result: false, // 是否存在问题,true表示存在问题，false表示没有问题
    code: "", // 如果存在问题，返回代码片段; 如果没有问题，返回空字符串
    explanation: "代码没有问题" // 如果存在问题，解释问题所在；如果没有问题，说明代码没有问题
  ]
}
"""

JAVA_USER_PROMPT = """
请审查以下Java方法，找出可能的除零错误。
<method_line>={method_line}
<method_name>={method_name}
<method_content>={method_content}
"""

class JavaMethodData:
    """Java方法数据类，包含方法名,内容,行号"""

    def __init__(self, name: str, content: str, line_number: int):
        self.name = name
        self.content = content
        self.line_number = line_number

def list_methods(file_path: str) -> Mapping[str, str]:
    """Given java file, list all methods in it with their content and comments.

    Args:
        file_path (str): path to the java file

    Returns:
        Mapping[str, str]: mapping of method names to their content
    """
    result: Mapping[str, str] = {}
    
    # 读取Java文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # 初始化tree-sitter解析器
    JAVA = Language(java.language())
    # JAVA = get_language("java")
    parser = Parser(language=JAVA)
    
    # 解析源代码
    tree = parser.parse(source_code.encode('utf-8'))
    root = tree.root_node
    
    # 获取所有方法声明节点
    methods = _find_methods(root, source_code)
    
    return methods


def _find_methods(node, source_code: str) -> Mapping[str, str]:
    """递归查找所有方法声明节点"""
    result: Mapping[str, str] = {}
    
    # 查找method_declaration类型的节点
    if node.type == 'method_declaration':
        # 获取方法名
        method_name = _extract_method_name(node, source_code)
        # 获取方法完整内容（包括注释）
        method_content = _extract_method_content(node, source_code)
        if method_name:
            result[method_name] = JavaMethodData(name=method_name, content=method_content, line_number=node.start_point[0] + 1)
    
    # 递归遍历子节点
    for child in node.children:
        result.update(_find_methods(child, source_code))
    
    return result


def _extract_method_name(node, source_code: str) -> str:
    """从方法声明节点提取方法名（包含参数类型以区分重载）"""
    method_name = ""
    params = []
    
    for child in node.children:
        if child.type == 'identifier':
            method_name = source_code[child.start_byte:child.end_byte]
        elif child.type == 'formal_parameters':
            # 提取参数列表
            params = _extract_parameters(child, source_code)
    
    if method_name:
        # 返回格式: methodName(param1Type,param2Type)
        param_str = ",".join(params) if params else ""
        return f"{method_name}({param_str})"
    return ""


def _extract_parameters(node, source_code: str) -> List[str]:
    """从formal_parameters节点提取参数类型列表"""
    params = []
    
    for child in node.children:
        if child.type == 'formal_parameter':
            # 获取参数类型
            param_type = ""
            for param_child in child.children:
                if param_child.type in ['type_identifier', 'primitive_type', 'array_type']:
                    param_type = source_code[param_child.start_byte:param_child.end_byte]
                    params.append(param_type)
                    break
    
    return params


def _extract_method_content(node, source_code: str) -> str:
    """提取方法的完整内容（包括javadoc注释）"""
    start = node.start_byte
    
    # 向前查找javadoc注释
    lines = source_code[:start].split('\n')
    comment_start = start
    
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if line.startswith('*/'):
            # 找到javadoc结束，从/**开始
            for j in range(i, -1, -1):
                if '/**' in lines[j]:
                    comment_start = sum(len(l) + 1 for l in lines[:j])
                    break
            break
        elif not line.startswith('*') and not line.startswith('//') and line:
            break
    
    end = node.end_byte
    content = source_code[comment_start:end]
    
    return content if isinstance(content, str) else content.decode('utf-8')

def run_java_code_review(file_path: str) -> None:
    # https://api-docs.deepseek.com/
    client = OpenAI(api_key=os.getenv("DEEPSEEK_AI_KEY"), base_url="https://api.deepseek.com")
    # https://api-docs.deepseek.com/quick_start/pricing
    model = "deepseek-chat"

    """运行Java代码审查"""
    methods = list_methods(file_path)
    final_results = []
    for method_name, method_content in methods.items():
        print(f"方法名: {method_name} : {method_content.line_number}\n内容:\n{method_content.content}\n{'-'*40}\n")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": JAVA_SYSTEM_PROMPT},
                {"role": "user", "content": JAVA_USER_PROMPT.format(method_line=method_content.line_number, method_name=method_name, method_content=method_content.content)},
            ],
            stream=False
        )
        result = response.choices[0].message.content
        if result.startswith("```json"):
            result = result[len("```json"):].strip()
        if result.endswith("```"):
            result = result[:-3].strip()
        json_result = json.loads(result)
        print(f"审查结果: {json_result}")
        final_results.append(json_result)
        pass
    print(f"最终审查结果: {final_results}")
    os.makedirs("outputs/java", exist_ok=True)
    with open(f"outputs/java/java_code_review_{file_path.split('/')[-1]}.json", "w") as f:
        json.dump(final_results, f, indent=4)
    pass


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--input", type=Path, help="输入文件", required=True)
    args = arg_parser.parse_args()
    java_file_path = args.input
    print(f"输入文件: {java_file_path}")
    methods = list_methods(java_file_path)
    print(f"方法列表: {len(methods)}")
    run_java_code_review(java_file_path.__str__())
    pass