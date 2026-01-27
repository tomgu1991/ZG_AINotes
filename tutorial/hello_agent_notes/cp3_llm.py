import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


def run_llm(input_text: str):
    print(f" [Zuxing] 开始测试 CP3 LLM 模型加载和推理")
    # Mac M3 Pro 使用 MPS，如果不支持则使用 CPU
    device = "mps" if torch.backends.mps.is_available() else "cpu"

    # https://huggingface.co/Qwen/Qwen1.5-0.5B-Chat
    model = AutoModelForCausalLM.from_pretrained(
        "Qwen/Qwen1.5-0.5B-Chat",
        dtype=torch.float16,  # MPS 上使用 float16,
        cache_dir="./model_cache"  # 可选：指定缓存目录
    )
    model = model.to(device)  # 移到指定设备（MPS 或 CPU）
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-0.5B-Chat", cache_dir="./model_cache")

    print(f" [Zuxing] device {device} 上模型加载完成，开始推理测试")

    prompt = input_text
    print(f" [Zuxing] 问题: {prompt}")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    print(f" [Zuxing] messages: {messages}")

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    print(f" [Zuxing] text: {text}")
    model_inputs = tokenizer([text], return_tensors="pt").to(device)
    print(f" [Zuxing] model_inputs: {model_inputs}")

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=512
    )
    # print(f" [Zuxing] generated_ids: {generated_ids}")
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    # print(f" [Zuxing] generated_ids after slicing: {generated_ids}")

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(f" [Zuxing] response\n: {response}")
    pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="Hello, world!")
    args = parser.parse_args()
    run_llm(args.input)  # 调用推理函数
    pass