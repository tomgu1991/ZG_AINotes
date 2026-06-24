# CC Security Review
> https://github.com/anthropics/claude-code-security-review

```
claudecode/
├── constants.py.           # Constants and configuration values for ClaudeCode.
├── github_action_audit.py  # Main audit script for GitHub Actions
├── prompts.py              # Security audit prompt templates
├── findings_filter.py      # False positive filtering logic
├── claude_api_client.py    # Claude API client for false positive filtering
├── json_parser.py          # Robust JSON parsing utilities
├── requirements.txt        # Python dependencies
├── test_*.py               # Test suites
└── evals/                  # Eval tooling to test CC on arbitrary PRs
```

## 总结
1. constants.py: 超时、重试等等配置
    * “指数退避（Exponential Backoff）”算法，等待时间 = min(初始延迟 * (2 ^ 重试次数), RATE_LIMIT_BACKOFF_MAX)
2. logger.py: 用python3自己的logging模块处理
3. claude_api_client.py: 封装cc的请求相关内容
    * 有call_with_retry
    * _generate_single_finding_prompt，对于一个结果进行prmopt构建，
4. findings_filter.py: 处理误报。
    * 有HardExclusionRules：正则表达式
    * 用cc-api过滤
5. json_parser.py：解析json，也是一样需要增则匹配、各种方式上。
    * 返回结果也有状态，如果失败，caller会尝试重试
6. github_action_audit.py：主流程
    * 读取环境变量、初始化组件、构建各种元数据和diff
    * 生成review的prompt
    * 调用cc的能力去review
    * 进行过滤分析
7. prompts.py: review的prompt


## Prompt模板

1. 单个问题的校验：Respond with EXACTLY this JSON structure
```python
f"""I need you to analyze a security finding from an automated code audit and determine if it's a false positive.

{pr_info}

{filtering_section}

Assign a confidence score from 1-10:
- 1-3: Low confidence, likely false positive or noise
- 4-6: Medium confidence, needs investigation  
- 7-10: High confidence, likely true vulnerability

Finding to analyze:
\```json
{finding_json}
\```
{file_content}

Respond with EXACTLY this JSON structure (no markdown, no code blocks):
{{
  "original_severity": "HIGH",
  "confidence_score": 8,
  "keep_finding": true,
  "exclusion_reason": null,
  "justification": "Clear SQL injection vulnerability with specific exploit path"
}}"""
```

2. code review的分析:
```
You are a senior security engineer conducting a focused security review of GitHub PR.

CONTEXT: MR信息

Files Modified: XXX

OBJECTIVE: 高置信度、不是通用审查、仅关注安全
Perform a security-focused code review to identify HIGH-CONFIDENCE security vulnerabilities that could have real exploitation potential. This is not a general code review - focus ONLY on security implications newly added by this PR. Do not comment on existing security concerns.

CRITICAL INSTRUCTIONS: 重要的指令-低误报、没有噪音、不要报告什么

SECURITY CATEGORIES TO EXAMINE: 需要关注的类型

ANALYSIS METHODOLOGY:
1. 用文件工具找文件内容
2. 比对代码修改
3. 评估漏洞

REQUIRED OUTPUT FORMAT: 必须、JSON

SEVERITY GUIDELINES: 级别
CONFIDENCE SCORING: 分数
FINAL REMINDER: 关注高级别

IMPORTANT EXCLUSIONS - DO NOT REPORT:再次强调

最后提示json

```

```
You MUST output your findings as structured JSON with this exact schema:

{{
  "findings": [
    {{
      "file": "path/to/file.py",
      "line": 42,
      "severity": "HIGH",
      "category": "sql_injection",
      "description": "User input passed to SQL query without parameterization",
      "exploit_scenario": "Attacker could extract database contents by manipulating the 'search' parameter with SQL injection payloads like '1; DROP TABLE users--'",
      "recommendation": "Replace string formatting with parameterized queries using SQLAlchemy or equivalent",
      "confidence": 0.95
    }}
  ],
  "analysis_summary": {{
    "files_reviewed": 8,
    "high_severity": 1,
    "medium_severity": 0,
    "low_severity": 0,
    "review_completed": true,
  }}
}}
```