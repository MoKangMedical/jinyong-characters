#!/usr/bin/env python3
"""One-shot sync: copy all completed ComfyUI character images now."""
import subprocess, json, os, re, shutil, glob, sys

COURSES_DIR = os.path.expanduser("~/Desktop/OPC/jinyong-characters/docs/courses")
CHARS_DIR = os.path.expanduser("~/Desktop/OPC/jinyong-characters/docs/assets/characters")
COMFY_OUTPUT = os.path.expanduser("~/ComfyUI/output")

# Build Chinese name -> pinyin char_id mapping
name_to_id = {}
for fpath in glob.glob(os.path.join(COURSES_DIR, '*.html')):
    fname = os.path.basename(fpath)
    char_id = fname.replace('.html', '')
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read(3000)
        m = re.search(r'<title>([^—]+)', content)
        if m:
            cn = m.group(1).strip()
            if re.search(r'[\u4e00-\u9fff]', cn):
                name_to_id[cn] = char_id

# Query ComfyUI
r = subprocess.run(['curl', '-s', 'http://127.0.0.1:8188/history?max_items=300'],
    capture_output=True, text=True, timeout=30)
history = json.loads(r.stdout)

existing = set(f.replace('.png', '') for f in os.listdir(CHARS_DIR) if f.endswith('.png'))
copied = 0

for pid, info in history.items():
    if not info.get('status', {}).get('completed', False):
        continue
    p = info.get('prompt', [])
    if len(p) < 3:
        continue
    wf = p[2]
    prompt_text = ''
    for nid, nd in wf.items():
        if isinstance(nd, dict) and 'inputs' in nd:
            t = nd['inputs'].get('text', '')
            if 'portrait of' in t.lower():
                prompt_text = t
                break
    if not prompt_text:
        continue
    m = re.search(r'portrait of (.+?)(?:,|$)', prompt_text)
    if not m:
        continue
    char_name = m.group(1).strip()
    char_id = name_to_id.get(char_name)
    if not char_id or char_id in existing:
        continue
    outputs = info.get('outputs', {})
    for node_id, node_data in outputs.items():
        images = node_data.get('images', [])
        if images:
            fn = images[0].get('filename', '')
            src = os.path.join(COMFY_OUTPUT, fn)
            if os.path.exists(src):
                dst = os.path.join(CHARS_DIR, f'{char_id}.png')
                shutil.copy2(src, dst)
                existing.add(char_id)
                copied += 1
            break

all_courses = set(f.replace('.html', '') for f in os.listdir(COURSES_DIR) if f.endswith('.html'))
still = len(all_courses - existing)
print(f"Sync: copied={copied}, total={len(existing)}/{len(all_courses)}, missing={still}")

# Show queue status
r2 = subprocess.run(['curl', '-s', 'http://127.0.0.1:8188/queue'],
    capture_output=True, text=True, timeout=5)
qd = json.loads(r2.stdout)
print(f"Queue: {len(qd.get('queue_running',[]))}R/{len(qd.get('queue_pending',[]))}P")
