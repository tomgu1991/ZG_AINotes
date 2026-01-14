import os
import argparse
import sys
import json
from openai import OpenAI

# https://api-docs.deepseek.com/
client = OpenAI(api_key=os.getenv("DEEPSEEK_AI_KEY"), base_url="https://api.deepseek.com")
# https://api-docs.deepseek.com/quick_start/pricing
model = "deepseek-chat"


def explain_concept(concept):
    print(f"Explaining concept: {concept}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant to explain all concepts."},
            {"role": "user", "content": f"What is {concept}?"},
        ],
        stream=False
    )
    print("Response:")
    result = response.choices[0].message.content
    with open(f"result/deepseek_explanation_of_{concept.replace(' ', '_')}.md", "w") as f:
        f.write(result)
    print(result)
    pass

def think(target):
    print(f"Thinking about: {target}")
    messages = [{"role": "user", "content": f"Think about ```{target}``` in detail."}]
    response = client.chat.completions.create(
       model="deepseek-reasoner",
        messages=messages
    )
    reasoning_content = response.choices[0].message.reasoning_content
    print(f"Reasoning Content: {reasoning_content}")
    content = response.choices[0].message.content
    print(f"Final Content: {content}")
    pass


def multi_turn():
    print(f"Mult-turn reasoning example:")
    messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages
    )

    reasoning_content = response.choices[0].message.reasoning_content
    content = response.choices[0].message.content
    print(f"Reasoning Content:\n {reasoning_content}")
    print(f"Final Content:\n {content}")
    print("\n\n\n")

    messages.append({"role": "assistant", "content": content, "reasoning_content": reasoning_content})
    messages.append({"role": "user", "content": "What about 11.23?"})
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages
    )
    reasoning_content = response.choices[0].message.reasoning_content
    content = response.choices[0].message.content
    print(f"Reasoning Content:\n {reasoning_content}")
    print(f"Final Content:\n {content}")
    print("\n\n\n")

    messages.append({"role": "assistant", "content": content, "reasoning_content": reasoning_content})
    messages.append({"role": "user", "content": "What is the sum of them?"})
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages
    )
    reasoning_content = response.choices[0].message.reasoning_content
    content = response.choices[0].message.content
    print(f"Reasoning Content:\n {reasoning_content}")
    print(f"Final Content:\n {content}")
    print("\n\n\n")
    pass

# The definition of the tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "Get the current date",
            "parameters": { "type": "object", "properties": {} },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply the location and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": { "type": "string", "description": "The city name" },
                    "date": { "type": "string", "description": "The date in format YYYY-mm-dd" },
                },
                "required": ["location", "date"]
            },
        }
    },
]

# The mocked version of the tool calls
def get_date_mock():
    return "2025-12-01"

def get_weather_mock(location, date):
    print("Mocked get_weather called with:", location, date)
    return "Cloudy 7~13°C"

TOOL_CALL_MAP = {
    "get_date": get_date_mock,
    "get_weather": get_weather_mock
}

def clear_reasoning_content(messages):
    for message in messages:
        if hasattr(message, 'reasoning_content'):
            message.reasoning_content = None

def run_turn(turn, messages):
    sub_turn = 1
    while True:
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            tools=tools,
            extra_body={ "thinking": { "type": "enabled" } }
        )
        messages.append(response.choices[0].message)
        reasoning_content = response.choices[0].message.reasoning_content
        content = response.choices[0].message.content
        tool_calls = response.choices[0].message.tool_calls
        print(f"Turn {turn}.{sub_turn}\n{reasoning_content=}\n{content=}\n{tool_calls=}")
        # If there is no tool calls, then the model should get a final answer and we need to stop the loop
        if tool_calls is None:
            break
        for tool in tool_calls:
            tool_function = TOOL_CALL_MAP[tool.function.name]
            tool_result = tool_function(**json.loads(tool.function.arguments))
            print(f"tool result for {tool.function.name}: {tool_result}\n")
            messages.append({
                "role": "tool",
                "tool_call_id": tool.id,
                "content": tool_result,
            })
        sub_turn += 1

def tool_use():
    print(f"Tool use example:")
    # The user starts a question
    turn = 1
    messages = [{
        "role": "user",
        "content": "How's the weather in Hangzhou Tomorrow"
    }]
    run_turn(turn, messages)

    # The user starts a new question
    turn = 2
    messages.append({
        "role": "user",
        "content": "How's the weather in Hangzhou Tomorrow"
    })
    # We recommended to clear the reasoning_content in history messages so as to save network bandwidth
    clear_reasoning_content(messages)
    run_turn(turn, messages)
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Explain a concept using DeepSeek AI.")
    parser.add_argument("--list-model", type=bool, help="List avaliable models.", default=False)
    parser.add_argument("--concept", type=str, help="The concept to explain.", default="")
    parser.add_argument("--think", type=str, help="The think mode.", default="")
    parser.add_argument("--multi", type=bool, help="The multi mode.", default=False)
    parser.add_argument("--tool", type=bool, help="The multi mode.", default=False)
    args = parser.parse_args()
    
    if args.list_model:
        print("Models:")
        print(client.models.list())
        sys.exit(0)
    
    if args.concept != "":
        explain_concept(args.concept)

    if args.think != "":
        think(args.think)

    if args.multi:
        multi_turn()

    if args.tool:
        tool_use()
    sys.exit(0)