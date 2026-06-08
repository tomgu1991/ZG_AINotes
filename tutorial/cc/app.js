// 模拟一个延迟函数，用于制造打字机效果
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// ==========================================
// 1. 定义异步生成器（主循环）
// ==========================================
async function* dialogMainLoop() {
  // 模拟用户输入了指令
  const userInput = "帮我检查系统状态并生成报告";
  yield { type: 'status', data: `用户输入: "${userInput}"` };
  await delay(2000);

  // 模拟 AI 开始思考并流式输出文本
  yield { type: 'status', data: "AI 正在思考..." };
  await delay(5000);

  const words = ["收到", "，我", "现在", "为您", "检测", "系统", "设备", "..."];
  for (const word of words) {
    yield { type: 'text', data: word };
    await delay(150); // 每 150ms 吐出一个词
  }

  // 模拟 AI 决定调用本地工具（例如读取系统时钟）
  yield { type: 'status', data: "\n[AI 触发工具调用] 正在读取系统时间..." };
  await delay(1500); // 模拟工具执行耗时
  const systemTime = new Date().toLocaleTimeString();

  // 模拟 AI 拿到工具结果后，继续输出回答
  yield { type: 'status', data: `[工具返回结果] 当前时间是 ${systemTime}` };
  yield { type: 'status', data: "AI 正在总结报告..." };
  await delay(1000);

  const finalWords = ["检测", "完成", "。当", "前系统", "运行", "正常", "！"];
  for (const word of finalWords) {
    yield { type: 'text', data: word };
    await delay(150);
  }
  
  yield { type: 'status', data: "\n--- 对话结束 ---" };
}

// ==========================================
// 2. 外部消费（驱动主循环并渲染 UI）
// ==========================================
async function main() {
  console.log("=== 启动 Claude Code 模拟主循环 ===\n");

  // 获取迭代器实例
  const iterator = dialogMainLoop();

  // 使用 for await...of 持续消费异步生成器吐出的事件
  for await (const event of iterator) {
    if (event.type === 'text') {
      // 实时打印文本，不换行，形成打字机效果
      process.stdout.write(event.data);
    } else if (event.type === 'status') {
      // 状态改变时换行打印提示
      console.log(`\n\x1b[36m${event.data}\x1b[0m`); // \x1b[36m 是让终端显示青色文字
    }
  }
}

// 执行程序
main();
