#!/usr/bin/env python3
"""Poll ComfyUI history, extract char names from prompts, copy images to docs/assets/characters/"""
import os, sys, time, shutil, json, re, urllib.request

CHAR_DIR = os.path.expanduser("~/Desktop/OPC/jinyong-characters/docs/assets/characters")
COMFY_OUT = os.path.expanduser("~/ComfyUI/output")
COMFY_URL = "http://127.0.0.1:8188"

def get_existing():
    return set(f.replace(".png", "") for f in os.listdir(CHAR_DIR) if f.endswith(".png"))

def get_history():
    try:
        resp = urllib.request.urlopen(f"{COMFY_URL}/history?max_items=200", timeout=10)
        return json.loads(resp.read())
    except Exception as e:
        print(f"  [ERR history] {e}")
        return {}

def get_queue():
    try:
        resp = urllib.request.urlopen(f"{COMFY_URL}/queue", timeout=5)
        return json.loads(resp.read())
    except:
        return {}

def extract_char_from_prompt(prompt_text):
    """Extract English pinyin char name from prompt"""
    # "portrait of 阿曼, character from 白马啸西风" -> "aman"
    m = re.search(r"portrait of ([^\n,]+)", prompt_text)
    if not m:
        return None
    name_cn = m.group(1).strip()
    # Could also extract from "character named X" format
    return name_cn

def chinese_to_pinyin_simple(name_cn):
    """Look up pinyin for known characters (simple mapping)"""
    # We'll get the pinyin from either the output filename or the course file
    return name_cn.lower().replace(" ", "")

existing = get_existing()
print(f"Starting collector. Existing images: {len(existing)}")
copied_total = 0
processed_pids = set()

while True:
    history = get_history()
    queue = get_queue()
    running = len(queue.get("queue_running", []))
    pending = len(queue.get("queue_pending", []))
    
    new_copies = 0
    for pid, entry in history.items():
        if pid in processed_pids:
            continue
        if not entry.get("status", {}).get("completed"):
            continue
        
        # Get prompt text
        prompt_text = ""
        for node in entry.get("prompt", []):
            if isinstance(node, dict) and node.get("class_type") == "CLIPTextEncode":
                txt = node.get("inputs", {}).get("text", "")
                if "portrait" in txt.lower():
                    prompt_text = txt
                    break
        
        if not prompt_text:
            processed_pids.add(pid)
            continue
        
        char_cn = extract_char_from_prompt(prompt_text)
        if not char_cn:
            # print(f"  [{pid[:8]}] WARN: can't extract char from: {prompt_text[:80]}...")
            processed_pids.add(pid)
            continue
        
        # Try to find the output file
        for nid, out in entry.get("outputs", {}).items():
            for img in out.get("images", []):
                src = os.path.join(COMFY_OUT, img["filename"])
                if not os.path.exists(src):
                    continue
                
                # Find matching char_id from course filenames
                # Map based on filename proximity
                char_id = None
                # The prompt has Chinese name, we need pinyin
                # Try to match by looking at existing course files
                # For now, use the name from the output filename if it has a name pattern
                basename = os.path.splitext(img["filename"])[0]
                # jinyong_aman_00001_ -> aman
                parts = basename.split("_")
                if len(parts) >= 2 and parts[1] not in ("00001", "00002", "00003", "00004", "00005"):
                    char_id = parts[1]
                
                if char_id and char_id in existing:
                    break  # already have it
                
                if char_id is None:
                    # Search course files for Chinese name match
                    courses_dir = os.path.join(os.path.dirname(CHAR_DIR), "../courses")
                    for course_fn in os.listdir(courses_dir):
                        if not course_fn.endswith(".html"):
                            continue
                        cid = course_fn.replace(".html", "")
                        # Read title from course to match
                        try:
                            with open(os.path.join(courses_dir, course_fn)) as f:
                                content = f.read(5000)
                            if char_cn in content:
                                char_id = cid
                                break
                        except:
                            pass
                
                if not char_id or char_id in existing or char_id == "test":
                    processed_pids.add(pid)
                    continue
                
                dst = os.path.join(CHAR_DIR, f"{char_id}.png")
                shutil.copy2(src, dst)
                print(f"  COPIED: {pid[:8]} -> {char_id}.png ({os.path.getsize(dst)} bytes)")
                existing.add(char_id)
                new_copies += 1
                copied_total += 1
        
        processed_pids.add(pid)
    
    if new_copies > 0:
        print(f"[{time.strftime('%H:%M:%S')}] +{new_copies} copied, total: {copied_total}, existing: {len(existing)}, queue: {running}R/{pending}P")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] idle, queue: {running}R/{pending}P, existing: {len(existing)}")
    
    if running == 0 and pending == 0:
        print("\n=== DONE! Queue empty. ===")
        break
    
    time.sleep(30)
