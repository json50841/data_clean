import os
import re

def clean_text(input_file, output_file):
    # 不需要的行内容
    unwanted_lines = {
        "English (USA)",
        "arrow right",
        "delete history element",
        "add to bookmark",
        "",
    }

    # 日期格式识别
    date_pattern = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

    # 如果输出文件已存在则删除
    if os.path.exists(output_file):
        os.remove(output_file)

    # 读取输入文件
    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    cleaned_lines = []
    for line in lines:
        # 跳过不需要的行
        if line in unwanted_lines:
            continue

        # 去除日期
        line = date_pattern.sub("", line).strip()

        # 跳过清空后的行
        if not line:
            continue

        cleaned_lines.append(line)

    # 删除重复行，保持原有顺序
    seen = set()
    unique_lines = []
    for line in cleaned_lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    # 输出结果，一行一个单词或句子
    with open(output_file, "w", encoding="utf-8") as f:
        for line in unique_lines:
            f.write(line + "\n")

    print("✅ 清理完成！")
    print(f"已生成: {output_file}")

# 示例运行
clean_text("input copy.txt", "cleaned2.txt")
