const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// 1. async function：只能返回一个最终结果
async function getFinalData() {
  await delay(2000); // 停在这里
  return "完成"; // 只能 return 一次
}

const result = getFinalData()
result.then((val) => console.log(val))

// 2. async function*：可以随着时间推移，不断产生结果
async function* getStreamData() {
  await delay(1000);
  yield "正在加载第 1 步..."; // 吐出第一个数据，函数暂停
  
  await delay(2000);
  yield "正在加载第 2 步..."; // 吐出第二个数据，函数暂停
  
  await delay(1000);
  yield "全部加载完成！";      // 吐出最后一个数据
}

const iter = getStreamData()
for await (const value of iter) {
  console.log(value)
}

// 3. 定义生成器函数（带星号 *）
function* lotteryBox() {
  console.log("--- 开始摸奖 ---");
  yield "一等奖：iPhone"; // 吐出奖品，程序在这里“卡住”
  
  console.log("--- 再次把手伸进箱子 ---");
  yield "二等奖：iPad";   // 吐出奖品，程序再次“卡住”
  
  return "奖品抽光啦";     // 彻底结束; 这个不会被处理。循环结束了
}


function blockSleep(ms) {
  // 利用原子操作在共享内存上进行同步等待，实现硬件级别的真阻塞
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}
const box = lotteryBox(); 
for (const value of box) {
    console.log(value)
    blockSleep(5000)
}
