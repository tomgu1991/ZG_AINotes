import json
import os
import requests
from openai import OpenAI

def get_weather(latitude, longitude):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()
    return data['current']['temperature_2m']

# 构造 client
client = OpenAI(
    api_key=os.environ.get("AI_KEY"),  # 混元 APIKey
    base_url="https://api.hunyuan.cloud.tencent.com/v1",  # 混元 endpoint
)

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

messages = [{"role": "user", "content": "What's the weather like in Shanghai today? Using the get_weather tool, please provide the temperature in celsius."}]

completion = client.chat.completions.create(
    model="hunyuan-turbos-latest",
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
    model="hunyuan-turbos-latest",
    messages=messages,
    tools=tools,
)

print(completion_2.to_json())