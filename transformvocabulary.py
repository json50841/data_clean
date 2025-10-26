import asyncio
import aiohttp
from pathlib import Path
import time
import math
import argparse

# ----------------------------
# 参数解析
# ----------------------------
parser = argparse.ArgumentParser(description="异步翻译文件中的单词")
parser.add_argument("--start", "-s", type=int, default=129, help="从哪个数字开始计数行号")
args = parser.parse_args()
START_INDEX = args.start

# ----------------------------
# 配置
# ----------------------------
input_file = Path("cleaned2.txt")
output_file = input_file.parent / "final2.txt"

BATCH_SIZE = 1         # 每批单词数量
CONCURRENT = 1000      # 并发请求数
SLEEP_BETWEEN_BATCH = 0.5  # 每批请求间隔，防封

# ----------------------------
# 读取已翻译单词
# ----------------------------
translated_lines = {}
if output_file.exists():
    with open(output_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" - ", 1)
            if len(parts) == 2:
                translated_lines[parts[0]] = parts[1]

# ----------------------------
# 读取所有单词
# ----------------------------
with open(input_file, "r", encoding="utf-8") as f:
    all_words = [line.strip() for line in f if line.strip()]

# 过滤掉已翻译的单词
remaining_words = [w for w in all_words if w not in translated_lines]

total = len(all_words)
translated_count = len(all_words) - len(remaining_words)


# ----------------------------
# 异步翻译函数
# ----------------------------
async def fetch_translation(session, words_chunk):
    query = " ".join(words_chunk)
    url = "https://translate.googleapis.com/translate_a/single"
    params = {"client": "gtx", "sl": "en", "tl": "zh-CN", "dt": "t", "q": query}
    try:
        async with session.get(url, params=params, timeout=10) as resp:
            data = await resp.json()
            return [t[0] for t in data[0]]
    except Exception as e:
        return [f"翻译失败: {e}"] * len(words_chunk)


# ----------------------------
# 批量异步翻译
# ----------------------------
async def translate_all(words, batch_size=BATCH_SIZE, concurrent=CONCURRENT):
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(words), batch_size * concurrent):
            tasks = []
            chunks = [
                words[i + j : i + j + batch_size]
                for j in range(0, batch_size * concurrent, batch_size)
            ]
            for chunk in chunks:
                tasks.append(fetch_translation(session, chunk))
            results = await asyncio.gather(*tasks)

            # 写入文件并更新进度
            with open(output_file, "a", encoding="utf-8") as f:
                for chunk_words, chunk_translations in zip(chunks, results):
                    for w, t in zip(chunk_words, chunk_translations):
                        idx = all_words.index(w) + START_INDEX
                        f.write(f"{idx}. {w} - {t}\n")
                        translated_lines[w] = t
                        translated_count_local = len(translated_lines)
                        elapsed = time.time() - start_time
                        speed = translated_count_local / elapsed if elapsed > 0 else 0
                        percent = translated_count_local / total * 100
                        remaining = total - translated_count_local
                        eta = remaining / speed if speed > 0 else 0
                        print(
                            f"\r✅ 已翻译 {translated_count_local}/{total} 行 "
                            f"({percent:.2f}%) - ETA: {eta:.1f}s - Speed: {speed:.2f} 行/s",
                            end="",
                        )
            await asyncio.sleep(SLEEP_BETWEEN_BATCH)
    print("\n✅ 翻译完成!")


# ----------------------------
# 运行
# ----------------------------
if __name__ == "__main__":
    asyncio.run(translate_all(remaining_words))
