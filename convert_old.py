#!/usr/bin/env python3
"""
Extract rich content from old Jin Yong character HTMLs and rebuild as Kangbo courses.
"""

import os, re, sys

BASE = "/Users/apple/Desktop/OPC/jinyong-characters/docs"
COURSES_DIR = os.path.join(BASE, "courses")
KANGBO_CSS = "../assets/kangbo.css"

KANGBO_HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{char_name} - {title} | 金典人物学院</title>
<meta name="description" content="{meta_desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css_path}">
</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <a href="{home_path}" class="nav-brand">
      <svg width="22" height="22" viewBox="0 0 28 28"><circle cx="14" cy="14" r="12" stroke="#e2b64f" stroke-width="1.5" fill="none"/><path d="M6 18c2-6 4-8 8-10s6 2 8 6" stroke="#e2b64f" stroke-width="1.5" fill="none"/><circle cx="14" cy="12" r="2.5" fill="#e2b64f"/></svg>
      金典人物学院
    </a>
    <span style="font-size:.78rem;color:var(--text3);background:var(--card2);padding:4px 14px;border-radius:20px">{novel_name} | 第{lesson_num}课</span>
  </div>
</nav>
<div class="progress-bar"><div class="progress-fill" id="pf"></div></div>

<main class="main">

  <div class="page-header">
    <div class="page-phase">{novel_name} · {role_label}</div>
    <h1>{char_name} -- {page_title}</h1>
    <p class="subtitle">{subtitle}</p>
    <div class="page-meta">
      <span><span class="badge" style="background:var(--gold-bg);color:var(--gold)">{role_label}</span></span>
      <span>阅读约{read_time}分钟</span>
      <span>8个深度维度</span>
      <span>{word_count}字精读</span>
    </div>
  </div>

  <div class="audio-player">
    <svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="#e2b64f" stroke-width="1.5" fill="none"/><path d="M8 9v6M12 7v10M16 8v8" stroke="#e2b64f" stroke-width="1.5" stroke-linecap="round"/></svg>
    <div style="flex:1"><div class="audio-label">课程音频 / 口播精讲</div><audio controls preload="none"><source src="{audio_path}" type="audio/mpeg"></audio></div>
  </div>

  <div class="content">

{body_content}

  </div>

  <div class="bottom-nav">
    <a href="{novel_index}" class="prev">{novel_name}人物</a>
    <a href="{home_path}" class="center">返回人物总览</a>
    {next_nav}
  </div>

</main>

<script>
addEventListener('scroll',()=>{{document.getElementById('pf').style.width=(scrollY/(document.documentElement.scrollHeight-innerHeight)*100)+'%'}});
</script>
</body>
</html>'''

def extract_text_from_old_html(filepath):
    """Extract meaningful text blocks from old format HTML"""
    with open(filepath) as f:
        html = f.read()
    
    # Find the main content area - text between body start and scripts
    body_start = html.find('<body>')
    script_start = html.find('<script>')
    if body_start == -1:
        return ""
    if script_start == -1:
        script_start = len(html)
    
    body = html[body_start:script_start]
    
    # Remove all style tags and inline styles
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    body = re.sub(r'<svg[^>]*>.*?</svg>', '', body, flags=re.DOTALL)
    
    # Extract text from paragraphs, table cells, headers, list items
    # We want structured content - h2, h3, p, table, li elements
    # Remove the 3D hero, bamboo layer, nav
    body = re.sub(r'<div class="bamboo-layer[^"]*">.*?</div>', '', body, flags=re.DOTALL)
    body = re.sub(r'<div id="hero-3d".*?</div>', '', body, flags=re.DOTALL)
    body = re.sub(r'<nav[^>]*>.*?</nav>', '', body, flags=re.DOTALL)
    body = re.sub(r'<div class="hero-3d-container".*?</div>', '', body, flags=re.DOTALL)
    body = re.sub(r'<div class="character-portrait".*?</div>', '', body, flags=re.DOTALL)
    
    # Remove HTML comments
    body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
    
    # Remove emoji chars
    body = re.sub(r'[\U0001F300-\U0001F9FF\u2600-\u27BF\u2B50\u231A\u231B\u23CF\u23E9-\u23F3\u23F8-\u23FA\u25AA\u25AB\u25B6\u25C0\u25FB-\u25FE\u2693\u2694\u26A0\u26A1\u26AA\u26AB\u26BD\u26BE\u26C4\u26C5\u26C8\u26CE\u26CF\u26D1\u26D3\u26D4\u26E9\u26EA\u26F0-\u26F5\u26F7-\u26FA\u26FD\u2702\u2705\u2708-\u270D\u270F\u2712\u2714\u2716\u271D\u2721\u2728\u2733\u2734\u2744\u2747\u274C\u274E\u2753-\u2755\u2757\u2763\u2764\u2795-\u2797\u27A1\u27B0\u27BF\u2934\u2935]', '', body)
    body = re.sub(r'[\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F]', '', body)
    
    # Clean the remaining HTML: strip attributes we don't want
    body = re.sub(r'<div class="en">.*?</div>', '', body)
    body = re.sub(r' +class="[^"]*"', '', body)
    body = re.sub(r' +id="[^"]*"', '', body)
    
    # Simplify class names for our template
    body = body.replace('<table>', '<table class="data-table">')
    body = body.replace('<div class="highlight-box">', '<div class="callout gold">')
    body = body.replace('<div class="hl-title">', '<div class="callout-label">')
    
    return body.strip()

def extract_main_text(filepath):
    """Extract just the Chinese text paragraphs, ignoring nav/3D/scripts"""
    with open(filepath) as f:
        html = f.read()
    
    # Strip scripts, styles, SVG
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<svg[^>]*>.*?</svg>', '', html, flags=re.DOTALL)
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Remove emoji
    html = re.sub(r'[\U0001F300-\U0001FFFF\u2600-\u27BF\u2B50\u231A\u231B\u23CF\u23E9-\u23F3\u23F8-\u23FA\u25AA\u25AB\u25B6\u25C0\u25FB-\u25FE\u2693\u2694\u26A0\u26A1\u26AA\u26AB\u26BD\u26BE\u26C4\u26C5\u26C8\u26CE\u26CF\u26D1\u26D3\u26D4\u26E9\u26EA\u26F0-\u26F5\u26F7-\u26FA\u26FD\u2702\u2705\u2708-\u270D\u270F\u2712\u2714\u2716\u271D\u2721\u2728\u2733\u2734\u2744\u2747\u274C\u274E\u2753-\u2755\u2757\u2763\u2764\u2795-\u2797\u27A1\u27B0\u27BF\u2934\u2935]', '', html)
    html = re.sub(r'[\U0001FA00-\U0001FAFF]', '', html)
    
    # Find body content position
    body_start = html.find('main-content') 
    if body_start == -1:
        body_start = html.find('<body>')
    
    # Take text after the course hero section
    # Look for content blocks
    text = html[body_start:]
    
    # Strip all tags to count Chinese characters
    text_only = re.sub(r'<[^>]+>', '', text)
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', text_only))
    return cn_chars, text_only[:500]  # Return count and preview

def generate_narration(char_name, role_info, personality, keywords):
    """Generate a simple narration script based on character data"""
    templates = [
        f"今天我们来聊聊{char_name}，{role_info}。{personality}。{char_name}的故事，是一部关于成长、抉择与命运的传奇。",
        f"提起{char_name}，金庸迷们总有说不完的话。{role_info}。{personality}。今天，让我们一起走进{char_name}的世界。",
    ]
    return templates[0]  # Always use the first template for consistency

# ── Main: Convert a specific old file ──
def convert_file(input_path, output_path, char_name, novel_name, title, 
                 role_label, subtitle, lesson_num, css_path, home_path,
                 novel_index, next_nav, audio_path):
    """Convert an old HTML file to Kangbo format"""
    body = extract_text_from_old_html(input_path)
    
    # Count Chinese chars
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', body))
    read_time = max(5, cn_chars // 150)
    
    meta_desc = f"深度解读{char_name}：{subtitle[:80]}。金典人物学院 · 151堂江湖人生课。"
    
    html = KANGBO_HTML_TEMPLATE.format(
        char_name=char_name,
        title=title,
        meta_desc=meta_desc,
        css_path=css_path,
        home_path=home_path,
        novel_name=novel_name,
        lesson_num=lesson_num,
        role_label=role_label,
        page_title=title,
        subtitle=subtitle,
        read_time=read_time,
        word_count=f"约{cn_chars}",
        audio_path=audio_path,
        body_content=body,
        novel_index=novel_index,
        next_nav=next_nav,
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)
    return cn_chars

# ── Run conversions ──
conversions = [
    {
        "slug": "huangrong", "char_name": "黄蓉", "novel_name": "射雕英雄传",
        "dir": "shediao", "title": "女诸葛 · 丐帮帮主",
        "role_label": "主角", "lesson_num": 2,
        "subtitle": "桃花岛上长大的精灵少女，美貌与智慧并重。她用一桌叫花鸡俘获了傻小子郭靖，用绝世才智辅佐他成为一代大侠。",
        "next": '<a href="guojing.html" class="next">上一位: 郭靖</a>',
    },
    {
        "slug": "yangguo", "char_name": "杨过", "novel_name": "神雕侠侣",
        "dir": "shendiao", "title": "西狂 · 神雕大侠",
        "role_label": "主角", "lesson_num": 1,
        "subtitle": "杨康之子，自小流落江湖，被郭靖黄蓉收留。断右臂、遇神雕、创黯然销魂掌。一生执着一人，十六年等一回。",
        "next": '<a href="xiaolongnv.html" class="next">下一位: 小龙女</a>',
    },
    {
        "slug": "xiaolongnv", "char_name": "小龙女", "novel_name": "神雕侠侣",
        "dir": "shendiao", "title": "古墓仙子",
        "role_label": "主角", "lesson_num": 2,
        "subtitle": "古墓派传人，清冷如冰雪，容颜绝世。她与杨过的师徒之恋超越了世俗礼教，是金庸笔下最凄美动人的爱情。",
        "next": '<a href="yangguo.html" class="next">上一位: 杨过</a>',
    },
    {
        "slug": "zhangwuji", "char_name": "张无忌", "novel_name": "倚天屠龙记",
        "dir": "yitian", "title": "明教教主",
        "role_label": "主角", "lesson_num": 1,
        "subtitle": "武当张翠山之子，身中玄冥神掌，历经九死一生。习得九阳神功与乾坤大挪移，二十岁便成为明教第三十四代教主。",
        "next": '<a href="zhaomin.html" class="next">下一位: 赵敏</a>',
    },
    {
        "slug": "qiaofeng", "char_name": "乔峰", "novel_name": "天龙八部",
        "dir": "tlbb", "title": "北乔峰 · 南院大王",
        "role_label": "主角", "lesson_num": 1,
        "subtitle": "天下第一大帮丐帮帮主，武功盖世，义薄云天。真实身份却是契丹人萧峰。一生在忠义与民族间挣扎，最终以死明志。",
        "next": '<a href="duanyu.html" class="next">下一位: 段誉</a>',
    },
    {
        "slug": "duanyu", "char_name": "段誉", "novel_name": "天龙八部",
        "dir": "tlbb", "title": "大理世子",
        "role_label": "主角", "lesson_num": 2,
        "subtitle": "大理国镇南王世子，不愿学武却屡得奇遇。六脉神剑、凌波微步、北冥神功集于一身，痴恋王语嫣。",
        "next": '<a href="xuzhu.html" class="next">下一位: 虚竹</a>',
    },
    {
        "slug": "xuzhu", "char_name": "虚竹", "novel_name": "天龙八部",
        "dir": "tlbb", "title": "灵鹫宫主 · 西夏驸马",
        "role_label": "主角", "lesson_num": 3,
        "subtitle": "少林寺小僧，面貌丑陋，天真迂腐。破珍珑棋局、得无崖子传功、娶西夏公主——金庸笔下奇遇最多的主角。",
        "next": '<a href="qiaofeng.html" class="next">上一位: 乔峰</a>',
    },
]

print(f"Converting {len(conversions)} rich content files to Kangbo format...\n")

for conv in conversions:
    slug = conv["slug"]
    dr = conv["dir"]
    input_path = os.path.join(COURSES_DIR, dr, f"{slug}.html")
    output_path = os.path.join(COURSES_DIR, dr, f"{slug}.html")
    
    # Determine CSS path depth
    depth = "../../" if dr != "xueshan" else "../"  # Adjust based on actual nesting
    
    if dr in ("tlbb", "xajh", "ldj", "shujian", "bixue", "xueshan", 
              "feihu", "liancheng", "xiake", "baima", "yuanyang", "yuenv"):
        css_path = "../../assets/kangbo.css"
        home_path = "../../index.html"
        novel_index = f"../../index.html#{dr}"
    else:
        css_path = "../assets/kangbo.css"
        home_path = "../index.html"
        novel_index = f"../index.html#{dr}"
    
    audio_path = f"{css_path.replace('kangbo.css', 'audio/')}{slug}.mp3"
    
    if not os.path.exists(input_path):
        print(f"  SKIP {conv['char_name']}: input not found at {input_path}")
        continue
    
    cn = convert_file(
        input_path, output_path,
        conv["char_name"], conv["novel_name"], conv["title"],
        conv["role_label"], conv["subtitle"], conv["lesson_num"],
        css_path, home_path, novel_index, conv["next"], audio_path
    )
    
    print(f"  DONE {conv['char_name']}: {cn} Chinese chars written to {output_path}")

print("\nConversion complete!")
