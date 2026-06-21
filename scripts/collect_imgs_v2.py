#!/usr/bin/env python3
"""Collect ComfyUI generated character images and copy to right filenames.
Matches prompt text (Chinese character name) to pinyin course IDs.
"""
import subprocess, json, os, re, shutil, glob, time, sys

COURSES_DIR = os.path.expanduser("~/Desktop/OPC/jinyong-characters/docs/courses")
CHARS_DIR = os.path.expanduser("~/Desktop/OPC/jinyong-characters/docs/assets/characters")
COMFY_OUTPUT = os.path.expanduser("~/ComfyUI/output")

def build_mapping():
    """Build Chinese name -> char_id mapping from HTML title tags."""
    name_to_id = {}
    for fpath in glob.glob(os.path.join(COURSES_DIR, '*.html')):
        fname = os.path.basename(fpath)
        char_id = fname.replace('.html', '')
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read(3000)
            m = re.search(r'<title>([^—]+)', content)
            if m:
                chinese_name = m.group(1).strip()
                # Only add if it contains Chinese characters
                if re.search(r'[\u4e00-\u9fff]', chinese_name):
                    name_to_id[chinese_name] = char_id
    return name_to_id

def sync_once(name_to_id):
    """Query ComfyUI history and copy completed images."""
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://127.0.0.1:8188/history?max_items=300'],
            capture_output=True, text=True, timeout=10
        )
        history = json.loads(result.stdout)
    except Exception as e:
        print(f"  [ERROR] history query failed: {e}")
        return 0

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

        # Extract: "portrait of <char_name>" - up to comma
        m = re.search(r'portrait of (.+?)(?:,|$)', prompt_text)
        if not m:
            continue

        char_name = m.group(1).strip()
        char_id = name_to_id.get(char_name)

        if not char_id:
            continue

        if char_id in existing:
            continue

        # Get output file
        outputs = info.get('outputs', {})
        for node_id, node_data in outputs.items():
            images = node_data.get('images', [])
            if images:
                filename = images[0].get('filename', '')
                src = os.path.join(COMFY_OUTPUT, filename)
                if os.path.exists(src):
                    dst = os.path.join(CHARS_DIR, f'{char_id}.png')
                    shutil.copy2(src, dst)
                    size_kb = os.path.getsize(dst) // 1024
                    existing.add(char_id)
                    copied += 1
                break

    return copied

def main():
    name_to_id = build_mapping()
    print(f"Mapping: {len(name_to_id)} Chinese names")

    all_courses = set(f.replace('.html', '') for f in os.listdir(COURSES_DIR) if f.endswith('.html'))
    
    iteration = 0
    while True:
        iteration += 1
        existing = set(f.replace('.png', '') for f in os.listdir(CHARS_DIR) if f.endswith('.png'))
        missing = all_courses - existing
        
        if not missing:
            print(f"\n{'='*60}")
            print(f"DONE! All {len(all_courses)} images collected.")
            print(f"{'='*60}")
            break

        copied = sync_once(name_to_id)

        # Check queue
        try:
            q = subprocess.run(['curl', '-s', 'http://127.0.0.1:8188/queue'],
                capture_output=True, text=True, timeout=5)
            qd = json.loads(q.stdout)
            running = len(qd.get('queue_running', []))
            pending = len(qd.get('queue_pending', []))
        except:
            running, pending = '?', '?'

        existing2 = set(f.replace('.png', '') for f in os.listdir(CHARS_DIR) if f.endswith('.png'))
        still_missing = len(all_courses - existing2)

        ts = time.strftime('%H:%M:%S')
        print(f"[{ts}] iter#{iteration} copied={copied} total={len(existing2)}/{len(all_courses)} "
              f"missing={still_missing} queue={running}r/{pending}p")

        time.sleep(30)

if __name__ == '__main__':
    main()
