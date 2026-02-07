1. 环境准备：
```
uv add torch
uv add torchvision
uv add d2l # 最新的版本pytorch的版本有些问题。有一些函数没有了。
# 参考https://github.com/d2l-ai/d2l-pytorch-sagemaker-classic
将classic里面的d2l/torch.py 替换 tutorial/d2l_notes/.venv/lib/python3.11/site-packages/d2l/torch_103_bk.py
```