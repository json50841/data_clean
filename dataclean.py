import re
import os

def clean_google_file(input_file, output_file, removed_file):
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        return

    # 如果输出文件已存在则删除
    for file in [output_file, removed_file]:
        if os.path.exists(file):
            os.remove(file)

    # 读取整个文件
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    kept_words = []     # 要保留的单词（如 disciplines、intonation）
    removed_items = []  # 被删除的内容

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 如果是“xxx - Google 搜索”这种格式
        match = re.match(r'^([A-Za-z]+)\s*-\s*Google\s*搜索', line)
        if match:
            kept_words.append(match.group(1))
            removed_items.append(line)
            continue

        # 其他行包含日期、网址、页码、数字的都跳过
        if re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', line) or \
           re.search(r'www\.google\.com', line) or \
           re.search(r'页', line) or \
           re.search(r'#\d+', line) or \
           re.fullmatch(r'\d+', line):
            removed_items.append(line)
            continue

    # 将保留的单词每个写一行
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in kept_words:
            f.write(word + '\n')

    # 被删除的内容保存为元组
    with open(removed_file, 'w', encoding='utf-8') as f:
        f.write(str(tuple(removed_items)))

    print("✅ 清理完成！")
    print(f"已保留单词数量: {len(kept_words)}")
    print(f"已生成: {output_file}")
    print(f"已生成: {removed_file}")

# 示例运行
clean_google_file('input.txt', 'cleaned.txt', 'removed.txt')
