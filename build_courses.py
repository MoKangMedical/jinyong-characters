#!/usr/bin/env python3
"""
Batch Jin Yong Character Course Builder
Generates Kangbo-style 8-chapter courses for ALL 149 characters.
Uses JSON character data + template patterns for substantial content.
"""

import os, re, json

BASE = "/Users/apple/Desktop/OPC/jinyong-characters/docs"
COURSES_DIR = os.path.join(BASE, "courses")
ASSETS_DIR = os.path.join(BASE, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# ── Load ALL character data ──
all_chars = []
seen = set()
json_files = [f for f in os.listdir(COURSES_DIR) if f.endswith('.json')]

for jf in json_files:
    with open(os.path.join(COURSES_DIR, jf)) as f:
        data = json.load(f)
    if "novels" in data:
        for nk, nd in data["novels"].items():
            novel_name = nd.get("novel_name", nk)
            novel_dir = nd.get("directory", nk)
            for c in nd.get("characters", []):
                slug = c.get("slug", "")
                if slug not in seen:
                    seen.add(slug)
                    c["novel_name"] = novel_name
                    c["novel_dir"] = novel_dir
                    c["novel_key"] = nk
                    all_chars.append(c)

print(f"Total characters loaded: {len(all_chars)}")

# ── Character knowledge DB (supplements JSON data) ──
CHAR_DATA = {
    "guojing": {
        "gender": "男", "title": "北侠", "alias": "金刀驸马、靖哥哥",
        "origin": "临安牛家村", "master": "江南七怪、洪七公、周伯通",
        "skills": "降龙十八掌、九阴真经、空明拳、双手互搏",
        "spouse": "黄蓉", "ending": "镇守襄阳四十余年，城破殉国",
        "personality": "质朴纯善、坚韧不拔、大智若愚",
        "adventures": "马钰暗传全真内功、误饮宝蛇血、洪七公授降龙十八掌、周伯通传空明拳与双手互搏",
        "role": "《射雕英雄传》主人公。从蒙古草原上一个天资愚钝的少年，成长为镇守襄阳四十年的一代大侠",
        "quotes": "侠之大者，为国为民",
        "funfacts": "少年时一箭双雕；练武时别人练一遍他练十遍；桃花岛上与欧阳克比武求亲",
    },
    "huangrong": {
        "gender": "女", "title": "女诸葛",
        "alias": "蓉儿", "origin": "桃花岛",
        "master": "洪七公", "skills": "打狗棒法、落英神剑掌、兰花拂穴手",
        "spouse": "郭靖", "ending": "随郭靖镇守襄阳，城破殉国",
        "personality": "聪明绝顶、古灵精怪、敢爱敢恨",
        "adventures": "以美食换取洪七公武功、桃花岛求亲三道试题、智斗欧阳克、执掌丐帮",
        "role": "《射雕英雄传》女主人公。桃花岛主黄药师之女，天下第一大帮丐帮帮主",
        "quotes": "靖哥哥，你怎么这么傻？",
        "funfacts": "天下第一厨艺大师；一个人能把丐帮上下玩得团团转",
    },
    # More data will be added for all 149 characters
}

# Novel directory mapping
NOVEL_DIR = {
    "射雕英雄传": "shediao", "神雕侠侣": "shendiao", "倚天屠龙记": "yitian",
    "天龙八部": "tlbb", "笑傲江湖": "xajh", "鹿鼎记": "ldj",
    "书剑恩仇录": "shujian", "碧血剑": "bixue", "雪山飞狐": "xueshan",
    "飞狐外传": "feihu", "连城诀": "liancheng", "侠客行": "xiake",
    "白马啸西风": "baima", "鸳鸯刀": "yuanyang", "越女剑": "yuenv",
}

print("Ready. Use batch_course_gen() function to generate courses.")
