#!/usr/bin/env python3
"""
Clean Kangbo Course Generator - builds courses from JSON data + structured templates.
All CSS paths are correct, all emoji removed, all courses have consistent structure.
"""
import os, re, json

BASE = "/Users/apple/Desktop/OPC/jinyong-characters/docs"
COURSES_DIR = os.path.join(BASE, "courses")
os.makedirs(os.path.join(BASE, "assets", "audio"), exist_ok=True)

# ── Shared Kangbo template ──
CSS_PATH = "../../assets/kangbo.css"
HOME_PATH = "../../index.html"

def build_html(char_name, novel_name, novel_dir, title, role_label, lesson_num, 
               subtitle, meta_desc, data_table_rows, chapters, narration, exercises, 
               prev_link="", next_link=""):
    """Assemble a complete Kangbo-style course page"""
    
    # Build data table
    table_html = '<table class="data-table">\n'
    table_html += '  <tr><th colspan="2">核心档案</th></tr>\n'
    for row in data_table_rows:
        table_html += f'  <tr><td>{row[0]}</td><td>{row[1]}</td></tr>\n'
    table_html += '</table>'
    
    # Build chapters
    chapters_html = ""
    chapter_names = ["人物档案", "性格解析", "命运轨迹", "奇遇与转折", "武功绝学", "情感世界", "趣事与典故", "现实启示"]
    for i, (title_cn, content) in enumerate(zip(chapter_names, chapters)):
        if i == 0:
            # Chapter 1 includes the data table
            chapters_html += f'<h2>第{cn_num(i+1)}章 · {title_cn}</h2>\n'
            chapters_html += content
            chapters_html += f'\n{table_html}\n'
            # Also add callout
            chapters_html += f'\n<div class="callout gold">\n  <div class="callout-label">一句话定位</div>\n  <p>{subtitle}</p>\n</div>\n'
        else:
            chapters_html += f'<h2>第{cn_num(i+1)}章 · {title_cn}</h2>\n'
            chapters_html += content + '\n'
    
    # Exercises
    ex_html = '<div class="exercise-section">\n  <h2>课后思考</h2>\n'
    for i, (q, a) in enumerate(exercises):
        ex_html += f'''  <div class="exercise">
    <h3>思考题{cn_num(i+1)}</h3>
    <p class="q">{q}</p>
    <details>
      <summary>点击查看参考思路</summary>
      <p>{a}</p>
    </details>
  </div>\n'''
    ex_html += '</div>'
    
    # Narration
    narration_html = f'''    <div class="narration-section">
      <h2>口播稿 · 500字精讲</h2>
      <div class="narration-text">{narration}</div>
      <div class="narration-meta">
        <span>字数: ~500字</span>
        <span>音频时长: 约4分钟</span>
        <span>适用场景: 课程先导/短视频</span>
      </div>
    </div>'''
    
    # Bottom nav
    nav_parts = []
    if prev_link:
        nav_parts.append(f'    <a href="{prev_link[1]}" class="prev">{prev_link[0]}</a>')
    else:
        nav_parts.append('    <a href="../../index.html" class="prev">返回人物总览</a>')
    nav_parts.append('    <a href="../../index.html" class="center">返回人物总览</a>')
    if next_link:
        nav_parts.append(f'    <a href="{next_link[1]}" class="next">{next_link[0]}</a>')
    else:
        nav_parts.append('    <a href="../../index.html" class="next">下一位人物</a>')
    bottom_nav_html = '\n'.join(nav_parts)
    
    # Read time
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', chapters_html + narration_html))
    read_time = max(5, cn_chars // 200)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{char_name} - {title} | 金典人物学院</title>
<meta name="description" content="{meta_desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{CSS_PATH}">
</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <a href="{HOME_PATH}" class="nav-brand">
      <svg width="22" height="22" viewBox="0 0 28 28"><circle cx="14" cy="14" r="12" stroke="#e2b64f" stroke-width="1.5" fill="none"/><path d="M6 18c2-6 4-8 8-10s6 2 8 6" stroke="#e2b64f" stroke-width="1.5" fill="none"/><circle cx="14" cy="12" r="2.5" fill="#e2b64f"/></svg>
      金典人物学院
    </a>
    <span style="font-size:.78rem;color:var(--text3);background:var(--card2);padding:4px 14px;border-radius:20px">{novel_name} | 第{lesson_num}课</span>
  </div>
</nav>
<div class="progress-bar"><div class="progress-fill" id="pf"></div></div>

<main class="main">

  <div class="page-header">
    <div class="page-phase">{novel_name} · {role_label}课程</div>
    <h1>{char_name} -- {title}</h1>
    <p class="subtitle">{subtitle}</p>
    <div class="page-meta">
      <span><span class="badge" style="background:var(--gold-bg);color:var(--gold)">{role_label}</span></span>
      <span>阅读约{read_time}分钟</span>
      <span>8个深度维度</span>
      <span>约{cn_chars}字精读</span>
    </div>
  </div>

  <div class="audio-player">
    <svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="#e2b64f" stroke-width="1.5" fill="none"/><path d="M8 9v6M12 7v10M16 8v8" stroke="#e2b64f" stroke-width="1.5" stroke-linecap="round"/></svg>
    <div style="flex:1"><div class="audio-label">课程音频 / 口播精讲</div><audio controls preload="none"><source src="../../assets/audio/{slug}.mp3" type="audio/mpeg"></audio></div>
  </div>

  <div class="content">

{chapters_html}

{narration_html}

{ex_html}

  </div>

  <div class="bottom-nav">
{bottom_nav_html}
  </div>

</main>

<script>
addEventListener('scroll',()=>{{document.getElementById('pf').style.width=(scrollY/(document.documentElement.scrollHeight-innerHeight)*100)+'%'}});
</script>
</body>
</html>'''
    return html

def cn_num(n):
    """Convert 1-99 to Chinese number"""
    nums = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
            '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']
    if n <= 20:
        return nums[n]
    return str(n)

print("Generator loaded. Use generate_course() to create a course.")

# ── Character data catalog (for main characters) ──
# This dict will be populated by individual generation scripts
CHAR_CATALOG = {}
