#!/usr/bin/env python3
"""为所有151门课程页注入角色肖像图 + CSS"""

import os, re, sys

BASE = os.path.expanduser("~/Desktop/OPC/jinyong-characters")
COURSES_DIR = os.path.join(BASE, "docs", "courses")
CSS_INSERT = """
.char-portrait{width:160px;height:240px;border-radius:16px;object-fit:cover;border:2px solid var(--gold);box-shadow:0 4px 24px rgba(226,182,79,.15);margin-bottom:24px;transition:transform .3s,box-shadow .3s}
.char-portrait:hover{transform:scale(1.02);box-shadow:0 8px 32px rgba(226,182,79,.25)}
@media(max-width:640px){.char-portrait{width:120px;height:180px;margin-bottom:16px}}
</style>
"""

img_template = """
  <img class="char-portrait" src="../../assets/characters/{char_id}.png" alt="{char_name}" loading="lazy">
"""

def process_file(filepath):
    with open(filepath, 'r') as f:
        html = f.read()
    
    name_match = re.search(r'<h1>(\S+)<', html)
    if not name_match:
        print(f"  SKIP: no h1 found in {os.path.basename(filepath)}")
        return False
    name = name_match.group(1)
    
    char_id = os.path.splitext(os.path.basename(filepath))[0]
    
    img_tag = img_template.format(char_id=char_id, char_name=name)
    
    # 检查是否已有图片
    if 'char-portrait' in html:
        print(f"  SKIP: already has portrait in {os.path.basename(filepath)}")
        return False
    
    # 策略：在 </header> 的第一个 </style> 之前插入 CSS（即 style 标签关闭前）
    html = html.replace('</style>\n</head>', CSS_INSERT + '\n</head>', 1)
    
    # 在 lesson-phase 的 span 关闭后、h1 前插入 img
    # 匹配模式：</span>\n  <h1>
    pattern = r'(<span class="lesson-phase">[^<]*</span>)\n  <h1>'
    replacement = r'\1\n' + img_tag.strip() + '\n  <h1>'
    
    new_html = re.sub(pattern, replacement, html, count=1)
    
    if new_html == html:
        # 尝试另一种模式（可能有不同的空白）
        pattern2 = r'(class="lesson-phase">.*?</span>)\s*<h1>'
        new_html = re.sub(pattern2, r'\1\n' + img_tag.strip() + '\n  <h1>', html, count=1)
    
    if new_html == html:
        print(f"  WARN: pattern not matched in {os.path.basename(filepath)}")
        return False
    
    with open(filepath, 'w') as f:
        f.write(new_html)
    
    return True

success = 0
total = 0
for fn in sorted(os.listdir(COURSES_DIR)):
    if not fn.endswith('.html'):
        continue
    total += 1
    fp = os.path.join(COURSES_DIR, fn)
    if process_file(fp):
        success += 1
        print(f"  OK: {fn}")
    else:
        print(f"  --: {fn}")

print(f"\nDone: {success}/{total} pages updated")
