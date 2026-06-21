#!/usr/bin/env python3
"""ComfyUI batch: submit all, poll periodically, copy to characters/"""

import json, os, sys, time, urllib.request, shutil

COMFY = "http://127.0.0.1:8188"
BASE = os.path.expanduser("~/Desktop/OPC/jinyong-characters")
CHARS_JSON = os.path.join(BASE, "char_content_enriched.json")
OUTPUT_DIR = os.path.join(BASE, "docs", "assets", "characters")
COMFY_OUT = os.path.expanduser("~/ComfyUI/output")

with open(os.path.join(BASE, "scripts", "workflow_jinyong.json")) as f:
    WF = json.load(f)

with open(CHARS_JSON) as f:
    CHAR_DATA = json.load(f)

existing = {fn.replace('.png', '') for fn in os.listdir(OUTPUT_DIR) if fn.endswith('.png') and not fn.endswith('_done.png')}

# Build generate list
to_gen = []
for html_fn in sorted(os.listdir(os.path.join(BASE, "docs", "courses"))):
    cid = html_fn.replace('.html', '')
    if cid not in existing:
        info = CHAR_DATA.get(cid, {})
        name = info.get('name', cid)
        novel = info.get('novel', '')
        role = info.get('role_type', '')
        to_gen.append((cid, name, novel, role))

print(f"Need {len(to_gen)} images. Submitting all to ComfyUI...")

prompt_ids = {}

for i, (cid, name, novel, role) in enumerate(to_gen):
    wf = json.loads(json.dumps(WF))  # deep copy
    
    # Build prompt
    if role == '主角':
        prompt = f"(masterpiece, best quality:1.2), portrait of {name}, {novel} main character, Chinese martial arts fantasy, heroic posture, traditional Chinese warrior clothing, dramatic lighting, cinematic, detailed face, sharp focus, professional illustration, 8k, ink wash style"
    else:
        prompt = f"(masterpiece, best quality:1.2), portrait of {name}, character from {novel}, Chinese martial arts fantasy, distinctive appearance, traditional Chinese attire, dramatic lighting, cinematic, detailed face, sharp focus, professional illustration, 8k, ink wash style"
    
    wf['2']['inputs']['text'] = prompt
    wf['4']['inputs']['seed'] = int(time.time() * 1000 + i) % (2**31)
    
    payload = {"prompt": wf, "client_id": "jinyong-batch-v2"}
    data = json.dumps(payload).encode()
    
    try:
        req = urllib.request.Request(f"{COMFY}/prompt", data=data,
            headers={'Content-Type': 'application/json'})
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read())
        pid = result.get('prompt_id')
        if pid:
            prompt_ids[pid] = (cid, name)
            if (i+1) % 20 == 0:
                print(f"  submitted {i+1}/{len(to_gen)}")
    except Exception as e:
        print(f"  ERROR submitting {cid}: {e}")

print(f"Submitted {len(prompt_ids)}/{len(to_gen)} jobs. Waiting...")

# Poll and collect
collected = {}
pids_left = set(prompt_ids.keys())
timeout = time.time() + 600  # 10 minutes max

while pids_left and time.time() < timeout:
    time.sleep(15)
    
    # Check history
    try:
        req = urllib.request.Request(f"{COMFY}/history")
        resp = urllib.request.urlopen(req, timeout=5)
        history = json.loads(resp.read())
    except:
        continue
    
    done_pids = set()
    for pid in pids_left:
        pid_str = str(pid) if isinstance(pid, int) else pid
        if pid_str in history:
            entry = history[pid_str]
            status = entry.get('status', {})
            if status.get('completed', False):
                for nid, out in entry.get('outputs', {}).items():
                    for img in out.get('images', []):
                        img_path = os.path.join(COMFY_OUT, img['filename'])
                        cid, name = prompt_ids[pid]
                        dest = os.path.join(OUTPUT_DIR, f"{cid}.png")
                        if os.path.exists(img_path):
                            shutil.copy2(img_path, dest)
                            collected[cid] = True
                            done_pids.add(pid)
    
    pids_left -= done_pids
    if done_pids:
        print(f"  collected {len(collected)}/{len(prompt_ids)} ({len(pids_left)} remaining)")
    
    # Also check running/pending
    try:
        req = urllib.request.Request(f"{COMFY}/queue")
        resp = urllib.request.urlopen(req, timeout=5)
        queue = json.loads(resp.read())
        running = len(queue.get('queue_running', []))
        pending = len(queue.get('queue_pending', []))
        if not done_pids:
            print(f"  queue: {running} running, {pending} pending")
    except:
        pass

print(f"\nDone! Collected {len(collected)}/{len(prompt_ids)} images")
remaining = [prompt_ids[pid][0] for pid in pids_left]
if remaining:
    print(f"Still missing ({len(remaining)}): {remaining[:10]}...")
