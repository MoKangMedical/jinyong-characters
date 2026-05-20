#!/usr/bin/env python3
"""
金庸人物志研究院 — 课程页面批量生成器
用法: python3 generate_courses.py [novel_key]
      不传参数则重新生成所有课程
"""

import json, os, sys, re
from pathlib import Path

BASE = Path("/Users/apple/Desktop/OPC/jinyong-characters/docs")
COURSES = BASE / "courses"
TEMPLATE = COURSES / "template.html"
DATA_FILE = COURSES / "characters_data.json"
ASSETS = BASE / "assets"

# ─── 角色元素类型映射 ───
ELEMENT_MAP = {
    "剑": "sword", "刀": "dagger", "掌": "palm", "拳": "palm",
    "棍": "staff", "杖": "staff", "棒": "staff",
    "扇": "fan", "针": "needle", "鞭": "whip",
    "琴": "flute", "箫": "flute", "笛": "flute",
    "书": "book", "笔": "book",
    "拂尘": "staff", "暗器": "needle",
    "毒": "medicine", "药": "medicine",
    "龙": "dragon", "箭": "arrow",
    "内力": "palm", "轻功": "palm",
    "佛": "lotus", "道": "lotus",
}

def infer_elements(weapons_str, role_type):
    """根据武器和角色类型推断3D元素"""
    elements = []
    if weapons_str:
        for key, elem in ELEMENT_MAP.items():
            if key in weapons_str and elem not in elements:
                elements.append(elem)
    # 根据角色类型补充
    if role_type == "主角" and "sword" not in elements:
        elements.append("sword")
    if not elements:
        elements.append("palm")
    return elements[:4]  # 最多4个


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"{r},{g},{b}"


def fill_template(char, asset_prefix="../../"):
    """用角色数据填充模板"""
    with open(TEMPLATE, 'r', encoding='utf-8') as f:
        html = f.read()
    
    theme_color = char.get("theme_color", "#d4a574")
    theme_rgb = hex_to_rgb(theme_color)
    weapons = char.get("weapons", "")
    role = char.get("role_type", "重要人物")
    elements = infer_elements(weapons, role)
    
    replaces = {
        "__NAME__": char["name"],
        "__TITLE__": char.get("title", "江湖人物"),
        "__BRIEF__": char.get("brief", ""),
        "__NOVEL__": char.get("novel", ""),
        "__ROLE__": role,
        "__THEME_COLOR__": theme_color,
        "__THEME_RGB__": theme_rgb,
        "__THEME_GLOW__": f"rgba({theme_rgb}, 0.4)",
        "__PARTICLE_COLOR__": char.get("particle_color", theme_color),
        "__ELEMENTS__": json.dumps(elements),
        "__ASSET_PREFIX__": asset_prefix,
        "__SECTIONS__": build_sections(char),
        "__PREV_LINK__": build_nav_link(char, "prev"),
        "__NEXT_LINK__": build_nav_link(char, "next"),
    }
    
    for key, val in replaces.items():
        html = html.replace(key, str(val))
    
    return html


def build_sections(char):
    """构建课程内容区块"""
    sections = []
    
    # Section 01: 人物档案
    table_rows = []
    info_fields = [
        ("姓名", "name"), ("别名", "alias"), ("出身", "origin"),
        ("门派", "sect"), ("师父", "master"), ("配偶", "spouse"),
        ("子女", "children"), ("结义", "sworn"), ("武功", "weapons"),
        ("兵器", "weapon_specific"), ("结局", "ending"),
    ]
    for label, key in info_fields:
        val = char.get(key, "")
        if val:
            table_rows.append(f"      <tr><td>{label}</td><td>{val}</td></tr>")
    
    sections.append(f'''<!-- 01 人物档案 -->
<section class="section">
  <div class="section-header">
    <div class="en">Chapter 01</div>
    <h2>人物档案</h2>
  </div>
  <div class="content-block">
    <table class="info-table">
{chr(10).join(table_rows)}
    </table>
  </div>
  {build_highlight(char, "one_liner")}
</section>''')

    # Sections 02-08
    section_configs = [
        ("02", "性格解析", "personality"),
        ("03", "成长轨迹", "growth"),
        ("04", "奇遇经历", "adventures"),
        ("05", "武功绝学", "skills"),
        ("06", "情感世界", "emotions"),
        ("07", "趣事典故", "anecdotes"),
        ("08", "江湖地位与启示", "legacy"),
    ]
    
    for num, title, key in section_configs:
        content = char.get(key, "")
        if not content:
            continue
        blocks_html = build_content_blocks(content)
        sections.append(f'''<!-- {num} {title} -->
<section class="section">
  <div class="section-header">
    <div class="en">Chapter {num}</div>
    <h2>{title}</h2>
  </div>
  {blocks_html}
</section>''')
    
    return "\n".join(sections)


def build_content_blocks(content):
    """将内容文本转为HTML块"""
    if isinstance(content, str):
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    else:
        paragraphs = content
    
    blocks = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # 检查是否是引用
        if p.startswith(">"):
            quote_text = p[1:].strip()
            blocks.append(f'''  <div class="quote-block">
    <div class="quote-text">{quote_text}</div>
  </div>''')
        # 检查是否是高亮
        elif p.startswith("!"):
            inner = p[1:].strip()
            if "|" in inner:
                title_part, body = inner.split("|", 1)
                blocks.append(f'''  <div class="highlight-box">
    <div class="hl-title">{title_part.strip()}</div>
    <p>{body.strip()}</p>
  </div>''')
            else:
                blocks.append(f'''  <div class="highlight-box">
    <p>{inner}</p>
  </div>''')
        elif p.startswith("##") and "|" in p:
            parts = p[2:].strip().split("|", 1)
            blocks.append(f'''  <div class="content-block">
    <h3>{parts[0].strip()}</h3>
    <p>{parts[1].strip()}</p>
  </div>''')
        else:
            blocks.append(f'''  <div class="content-block">
    <p>{p}</p>
  </div>''')
    
    return "\n".join(blocks)


def build_highlight(char, key):
    val = char.get(key, "")
    if not val:
        return ""
    return f'''  <div class="highlight-box">
    <div class="hl-title">一句话定位</div>
    <p>{val}</p>
  </div>'''


def build_nav_link(char, direction):
    """构建上/下一篇导航"""
    prev_name = char.get("prev_char", "")
    prev_url = char.get("prev_url", "")
    next_name = char.get("next_char", "")
    next_url = char.get("next_url", "")
    
    if direction == "prev" and prev_name:
        return f'<a href="{prev_url}" class="nav-prev">← {prev_name}</a>'
    elif direction == "prev":
        return '<span></span>'
    elif direction == "next" and next_name:
        return f'<a href="{next_url}" class="nav-next">{next_name} →</a>'
    else:
        return '<span></span>'


def generate_all():
    """生成所有课程 — 从三个独立的JSON数据文件中读取"""
    DATA_FILES = [
        (COURSES / "tlbb_chars.json", "tlbb"),
        (COURSES / "xajh_chars.json", "xajh"),
        (COURSES / "ldj_chars.json", "ldj"),
    ]
    
    generated = 0
    for data_file, novel_key in DATA_FILES:
        if not data_file.exists():
            print(f"  ⚠ 跳过 {data_file}（文件不存在）")
            continue
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        novel_data = data.get("novels", {}).get(novel_key, {})
        if not novel_data:
            # 兼容嵌套格式: {"novels":{"tlbb":{...}}} 和 {"novel_name":"...","characters":[...]}
            novel_data = data
        
        novel_dir = COURSES / novel_key
        novel_dir.mkdir(parents=True, exist_ok=True)
        
        characters = novel_data.get("characters", [])
        total = len(characters)
        
        for i, char in enumerate(characters):
            # 设置前后导航
            char["novel"] = novel_data.get("novel_name", "")
            if i > 0:
                char["prev_char"] = characters[i-1]["name"]
                char["prev_url"] = f"{characters[i-1]['slug']}.html"
            if i < total - 1:
                char["next_char"] = characters[i+1]["name"]
                char["next_url"] = f"{characters[i+1]['slug']}.html"
            
            html = fill_template(char, asset_prefix="../../")
            out_path = novel_dir / f"{char['slug']}.html"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html)
            generated += 1
            print(f"  ✓ {novel_data.get('novel_name', novel_key)} / {char['name']} → {out_path}")
    
    print(f"\n✅ 共生成 {generated} 个课程页面")


if __name__ == "__main__":
    generate_all()
