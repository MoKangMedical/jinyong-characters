#!/usr/bin/env python3
"""批量生成金庸人物角色图 via ComfyUI API (DreamShaper_8)"""

import json, os, time, sys, shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_PATH = os.path.join(os.path.dirname(__file__), "workflow_jinyong.json")
CHARS_JSON = os.path.join(BASE_DIR, "char_content_enriched.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "docs", "assets", "characters")
COMFY_OUTPUT = os.path.expanduser("~/ComfyUI/output")

# 已知缺图清单
MISSING_IDS = sorted([
    "afanti","ajiu","aman","aqing","axiu","baizizai","beihaishi","bingxueer",
    "changbozhi","changhezhi","chenglingsu","chenjialuo","dingdang","dingdian",
    "dingsan","diyun","fanli","fengtiannan","goujian","hetieshou","huahui_baima",
    "huatiegan","hufei","hufei_feihu","hufei_xueshan","huoqingtong","huyidao",
    "jilaoren","lingshuanghua","linyulong","liwenxiu","liyuanzhi","luobing",
    "machunhua","miao_renfeng_feihu","miaorenfeng","miaoruolan","murenqing",
    "nanlan","qianlong","qifang","renfeiyan","shangbaozhen","shipotian",
    "shiqing_minrou","shixiaocui","shizhongyu","shuisheng","supu","tianguinong",
    "waerlaqi","wanjue","wentailai","xiangxiang","xiaobanhe","xiaozhonghui",
    "xiaqingqing","xiaxueyi","xieyanke","xishi","xuedaolaozu","xutianhong",
    "yuanchengzhi","yuanguannan","yuanshixiao","yuanziyi","yushitong",
    "yuzhenzi","zhangsanlisi","zhangzhaozhong","zhaobanshan","zhaobanshan_feihu","zhuotianxiong"
])

# 加载人物数据 (name / novel / role)
chars_info = {}
try:
    with open(CHARS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for c in data if isinstance(data, list) else data.get("characters", []):
            cid = c.get("id", "")
            chars_info[cid] = {
                "name": c.get("name", cid),
                "novel": c.get("novel", ""),
                "role": c.get("role", "配角"),
                "title": c.get("title", ""),
            }
except Exception as e:
    print(f"Warning: 无法加载 {CHARS_JSON}: {e}")

# 小说英文→中文映射
NOVEL_CN = {
    "shediao": "射雕英雄传", "shendiao": "神雕侠侣", "yitian": "倚天屠龙记",
    "tianlong": "天龙八部", "xiaoao": "笑傲江湖", "lude": "鹿鼎记",
    "shujian": "书剑恩仇录", "bixue": "碧血剑", "feihu": "飞狐外传",
    "xueshan": "雪山飞狐", "liancheng": "连城诀", "xiake": "侠客行",
    "baima": "白马啸西风", "yuanyang": "鸳鸯刀", "yuenv": "越女剑",
}

def build_prompt(char_id, info):
    """根据角色信息构建生成提示词"""
    name = info.get("name", char_id)
    role = info.get("role", "配角")
    title = info.get("title", "")
    
    # 角色类型描述
    role_desc = {
        "主角": "heroic main character, confident pose, center of attention",
        "重要人物": "important character, dignified presence, detailed costume",
        "配角": "distinctive supporting character, unique appearance"
    }.get(role, "martial arts character")
    
    tag = f", {title}" if title else ""
    
    return (
        f"masterpiece, best quality, portrait of {name}, "
        f"Chinese martial arts fantasy, ancient Chinese warrior clothing, "
        f"wuxia novel character, {role_desc}{tag}, "
        f"traditional Chinese attire, dramatic lighting, cinematic, "
        f"highly detailed face, sharp focus, professional illustration, "
        f"chinese ink wash art style mixed with digital painting, 8k"
    )

def submit_to_comfyui(prompt_text, seed):
    """提交到ComfyUI并返回prompt_id"""
    import urllib.request
    
    with open(WORKFLOW_PATH, 'r') as f:
        workflow = json.load(f)
    
    # 注入prompt和seed
    workflow["2"]["inputs"]["text"] = prompt_text
    workflow["4"]["inputs"]["seed"] = seed
    
    payload = {"prompt": workflow, "client_id": "jinyong-batch"}
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(
        "http://127.0.0.1:8188/prompt",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    return result.get("prompt_id")

def wait_for_result(prompt_id, timeout=300):
    """等待生成完成并返回输出文件名"""
    import urllib.request
    
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
            resp = urllib.request.urlopen(req)
            history = json.loads(resp.read())
            
            if prompt_id in history:
                h = history[prompt_id]
                outputs = h.get("outputs", {})
                for node_id, node_output in outputs.items():
                    images = node_output.get("images", [])
                    if images:
                        return images[0]["filename"]
            time.sleep(2)
        except Exception as e:
            time.sleep(3)
    return None

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 过滤已存在的
    todo = [mid for mid in MISSING_IDS if not os.path.exists(os.path.join(OUTPUT_DIR, f"{mid}.png"))]
    
    if not todo:
        print("全部图片已存在，无需生成！")
        return
    
    print(f"待生成: {len(todo)}/{len(MISSING_IDS)}")
    
    success, failed = 0, 0
    
    for i, char_id in enumerate(todo):
        info = chars_info.get(char_id, {"name": char_id, "role": "配角"})
        name = info.get("name", char_id)
        
        prompt = build_prompt(char_id, info)
        seed = hash(char_id) % 2147483647
        
        print(f"[{i+1}/{len(todo)}] {char_id} ({name})...", end=" ", flush=True)
        
        try:
            prompt_id = submit_to_comfyui(prompt, seed)
            filename = wait_for_result(prompt_id, timeout=300)
            
            if filename:
                src = os.path.join(COMFY_OUTPUT, filename)
                dst = os.path.join(OUTPUT_DIR, f"{char_id}.png")
                shutil.move(src, dst)
                print(f"OK ({os.path.getsize(dst)//1024}KB)")
                success += 1
            else:
                print("TIMEOUT")
                failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1
        
        # 短暂休息避免过载
        time.sleep(1)
    
    print(f"\n完成: {success} 成功, {failed} 失败")

if __name__ == "__main__":
    main()
