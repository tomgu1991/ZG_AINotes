import json
import os
import sys
import argparse
from openai import OpenAI

# https://cloud.tencent.com/document/product/1729/104753
client = OpenAI(api_key=os.getenv("HUNYUAN_AI_KEY"), base_url="https://api.hunyuan.cloud.tencent.com/v1")
model = "hunyuan-2.0-thinking-20251109"


def explain_concept(concept):
    print(f"Explaining concept: {concept}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant to explain all concepts."},
            {"role": "user", "content": f"What is {concept}?"},
        ],
        extra_body={"enable_enhancement": True,  # <- 自定义参数
        },
        stream=False
    )
    print("Response:")
    result = response.choices[0].message.content
    with open(f"result/hunyuan_explanation_of_{concept.replace(' ', '_')}.md", "w") as f:
        f.write(result)
    print(result)
    pass

def multi_turn():
    print(f"Mult-turn reasoning example:")
    messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        extra_body={"enable_enhancement": True,  # <- 自定义参数
        },
    )

    content = response.choices[0].message.content
    print(f"Final Content:\n {content}")
    print("\n\n\n")

    messages.append({"role": "assistant", "content": content})
    messages.append({"role": "user", "content": "What about 11.23?"})
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        extra_body={"enable_enhancement": True,  # <- 自定义参数
        },
    )

    content = response.choices[0].message.content
    print(f"Final Content:\n {content}")
    pass

def get_weather(latitude, longitude):
    import requests
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()
    print("Weather API response:", data)
    return data['current']['temperature_2m']

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current temperature for provided coordinates in celsius.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"}
            },
            "required": ["latitude", "longitude"]
        }
    }
}]

def tool_use():
    print(f"Tool use example:")
    messages = [{"role": "user", "content": "What's the weather like in Paris today?"}]

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
    )

    print(completion.to_json())

    ## 在第一次响应的基础上 第二次发送请求
    tool_call = completion.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)

    result = get_weather(args["latitude"], args["longitude"])
 
    messages.append(completion.choices[0].message)  # append model's function call message
    messages.append({                               # append result message
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": str(result)
    })

    completion_2 = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
    )

    print(completion_2.to_json())
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Explain a concept using DeepSeek AI.")
    parser.add_argument("--concept", type=str, help="The concept to explain.", default="")
    parser.add_argument("--list-model", type=bool, help="List avaliable models.", default=False)
    parser.add_argument("--multi", type=bool, help="The multi mode.", default=False)
    parser.add_argument("--tool", type=bool, help="The multi mode.", default=False)
    args = parser.parse_args()
    
    if args.list_model:
        print("Models:")
        print(client.models.list())
        sys.exit(0)
    
    if args.concept != "":
        explain_concept(args.concept)

    if args.multi:
        multi_turn()

    if args.tool:
        tool_use()
    
    sys.exit(0)