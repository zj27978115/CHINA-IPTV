import requests
import re

def load_categories_from_moban():
    categories = {}
    current_category = None
    try:
        with open("TV/moban.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if ",#genre#" in line:
                    current_category = line.split(",")[0].strip()
                    categories[current_category] = []
                elif current_category:
                    channel = line.strip()
                    if channel:
                        categories[current_category].append(channel)
    except FileNotFoundError:
        print("错误：未找到 moban.txt 文件")
    return categories

# ✅ 两个源地址
urls = [
    "https://chinaiptv.pages.dev/txt?url=https://sub.ottiptv.cc/iptv.m3u",
    "https://fanmingming.com/txt?url=https://live.fanmingming.com/tv/m3u/ipv6.m3u"
]

content = ""
for url in urls:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content += response.text + "\n"
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

categories = load_categories_from_moban()
if not categories:
    print("分类数据为空，请检查 moban.txt 格式")
    exit()

lines = content.splitlines()
sorted_content = []
all_lines = [line.strip() for line in lines if line.strip() and "#genre#" not in line]

# ✅ 记录已匹配行
matched_lines = set()

for category, channels in categories.items():
    sorted_content.append(f"{category},#genre#")
    for channel in channels:
        for line in all_lines:
            if re.match(rf"^\s*{re.escape(channel)}\s*,", line, re.IGNORECASE):
                sorted_content.append(line)
                matched_lines.add(line)
    sorted_content.append("")

# ✅ 剩余未匹配的归入“其它”
other_lines = [line for line in all_lines if line not in matched_lines]
if other_lines:
    sorted_content.append("其它,#genre#")
    sorted_content.extend(other_lines)

with open("TV/live.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted_content))

print("✅ 多源合并完成，保留重复频道，已保存为 TV/live.txt")