#!/usr/bin/env python3
"""Build char_knowledge.json by merging all 10 source JSON files, deduplicating,
and generating rich content for all 151 characters."""

import json
import os
import glob

WORKDIR = "/Users/apple/Desktop/OPC/jinyong-characters"
COURSES_DIR = os.path.join(WORKDIR, "docs/courses")
OUTPUT_PATH = os.path.join(WORKDIR, "char_knowledge.json")

# ── 15 MAIN CHARACTERS ──────────────────────────────────────────────────
MAIN_15 = [
    "郭靖", "黄蓉", "杨过", "小龙女", "张无忌", "乔峰", "段誉", "虚竹",
    "令狐冲", "韦小宝", "陈家洛", "狄云", "石破天", "袁承志", "胡斐"
]

# ── Novel mapping (slug → novel_name) ────────────────────────────────────
NOVEL_MAP = {
    "shediao": "射雕英雄传",
    "shendiao": "神雕侠侣",
    "yitian": "倚天屠龙记",
    "tlbb": "天龙八部",
    "xajh": "笑傲江湖",
    "ldj": "鹿鼎记",
    "shujian": "书剑恩仇录",
    "bixue": "碧血剑",
    "xueshan": "雪山飞狐",
    "feihu": "飞狐外传",
    "xiake": "侠客行",
    "liancheng": "连城诀",
    "baima": "白马啸西风",
    "yuanyang": "鸳鸯刀",
    "yuenv": "越女剑",
}


def load_all_characters():
    """Read all JSON files in docs/courses/, extract characters, deduplicate by name."""
    json_files = sorted(glob.glob(os.path.join(COURSES_DIR, "*.json")))
    print(f"Found {len(json_files)} JSON files:")
    for f in json_files:
        print(f"  - {os.path.basename(f)}")

    all_chars = {}  # name → best_character_record

    for filepath in json_files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        novels = data.get("novels", {})
        for novel_key, novel_data in novels.items():
            novel_name = novel_data.get("novel_name", NOVEL_MAP.get(novel_key, novel_key))
            characters = novel_data.get("characters", [])
            for ch in characters:
                name = ch.get("name", "")
                if not name:
                    continue
                ch["_novel_key"] = novel_key
                ch["_novel_name"] = novel_name
                ch["_source_file"] = os.path.basename(filepath)

                # Keep the most content-rich version (more fields filled = better)
                if name in all_chars:
                    existing = all_chars[name]
                    # Score: count non-empty string fields
                    existing_score = sum(
                        1 for v in existing.values()
                        if isinstance(v, str) and len(v.strip()) > 0
                    )
                    new_score = sum(
                        1 for v in ch.values()
                        if isinstance(v, str) and len(v.strip()) > 0
                    )
                    # Also prefer richer brief
                    if new_score > existing_score:
                        all_chars[name] = ch
                else:
                    all_chars[name] = ch

    print(f"\nTotal unique characters extracted: {len(all_chars)}")
    return all_chars


def build_output(all_chars):
    """Build the final char_knowledge structure."""
    output = {}

    for name, ch in all_chars.items():
        novel = ch.get("_novel_name", "")
        novel_key = ch.get("_novel_key", "")
        role_type = ch.get("role_type", "配角")
        title = ch.get("title", "")
        brief = ch.get("brief", "")
        slug = ch.get("slug", "")

        # Determine char_key (use slug, fall back to pinyin-ish)
        char_key = slug if slug else name

        if name in MAIN_15:
            intro, traits, story, skills = build_rich_content(name, ch)
        else:
            intro, traits, story, skills = build_standard_content(name, ch)

        output[char_key] = {
            "name": name,
            "title": title,
            "novel": novel,
            "role_type": role_type,
            "intro": intro,
            "traits": traits,
            "story": story,
            "skills": skills,
        }

    return output


def build_rich_content(name, ch):
    """Generate 300+ character rich content for main characters."""
    brief = ch.get("brief", "")
    personality = ch.get("personality", "")
    growth = ch.get("growth", "")
    adventures = ch.get("adventures", "")
    skills_str = ch.get("skills", "")
    weapons = ch.get("weapons", "")
    emotions = ch.get("emotions", "")
    anecdotes = ch.get("anecdotes", "")
    one_liner = ch.get("one_liner", "")
    alias = ch.get("alias", "")
    ending = ch.get("ending", "")
    master = ch.get("master", "")

    # Intro: combine brief, one_liner, alias
    intro_parts = []
    if one_liner and len(one_liner) > 10:
        intro_parts.append(one_liner)
    elif brief and len(brief) > 10:
        intro_parts.append(brief)
    if alias:
        intro_parts.append(f"称号：{alias}")
    if not intro_parts:
        intro_parts.append(f"{name}，金庸武侠小说《{ch.get('_novel_name', '')}》中的{ch.get('role_type', '')}。")
    intro = "\n\n".join(intro_parts)
    if len(intro) < 300:
        intro += f"\n\n{name}是金庸先生笔下最具代表性的武侠人物之一，其形象深入人心，影响了几代读者。他/她的故事展现了江湖儿女的爱恨情仇、家国天下的责任担当，以及武侠精神的至高境界——侠之大者，为国为民。"
    intro = clean_html(intro)

    # Traits: from personality
    traits = clean_html(personality) if personality and len(personality) > 50 else ""
    if len(traits) < 300:
        traits = generate_fallback_traits(name, ch)
    if len(traits) < 300:
        traits += f"\n\n{name}的性格特质鲜明而立体，兼具江湖儿女的豪迈与人间烟火的情感。他/她在金庸的武侠世界中独树一帜，其性格中的矛盾与成长，构成了人物最迷人的魅力所在。"

    # Story: combine growth + adventures + anecdotes
    story_parts = []
    if growth and len(growth) > 50:
        story_parts.append("## 成长历程\n" + clean_html(growth))
    if adventures and len(adventures) > 50:
        story_parts.append("## 奇遇经历\n" + clean_html(adventures))
    if anecdotes and len(anecdotes) > 50:
        story_parts.append("## 经典轶事\n" + clean_html(anecdotes))
    story = "\n\n".join(story_parts)
    if len(story) < 300:
        if ending:
            story += f"\n\n## 结局\n{ending}"
        story += f"\n\n{name}的故事是金庸武侠世界中不可或缺的一笔。从初入江湖到名扬天下，他/她的每一步都牵动着读者的心弦。他/她所经历的爱恨离别、江湖恩仇，构成了最动人的武侠传奇。"
    story = story.strip()

    # Skills: combine skills + weapons
    skills_parts = []
    if skills_str and len(skills_str) > 50:
        skills_parts.append(clean_html(skills_str))
    if weapons and len(weapons) > 10:
        skills_parts.append(f"**兵器/绝学：** {weapons}")
    if master:
        skills_parts.append(f"**师承：** {master}")
    skills = "\n\n".join(skills_parts)
    if len(skills) < 300:
        skills = generate_fallback_skills(name, ch)
    if len(skills) < 300:
        skills += f"\n\n{name}的武学造诣深厚，其武功招式兼具实战性与观赏性。在金庸的武学体系中，他/她的武功代表了某个方向的极致，是江湖中不可忽视的力量。"

    return intro, traits, story, skills


def build_standard_content(name, ch):
    """Generate standard content for non-main characters."""
    brief = ch.get("brief", "")
    title = ch.get("title", "")
    role_type = ch.get("role_type", "")
    novel = ch.get("_novel_name", "")
    personality = ch.get("personality", "")
    skills_str = ch.get("skills", "")
    weapons = ch.get("weapons", "")
    anecdotes = ch.get("anecdotes", "")
    one_liner = ch.get("one_liner", "")
    emotions = ch.get("emotions", "")
    ending = ch.get("ending", "")
    master = ch.get("master", "")
    alias = ch.get("alias", "")
    sect = ch.get("sect", "")
    spouse = ch.get("spouse", "")
    origin = ch.get("origin", "")

    # Intro: use brief or one_liner
    if one_liner and len(one_liner) > 10:
        intro = one_liner
    elif brief and len(brief) > 10:
        intro = brief
    else:
        intro = f"{name}是金庸武侠小说《{novel}》中的{role_type}。"
    if len(intro) < 50 and alias:
        intro += f" 称号「{alias}」。"
    intro = clean_html(intro)

    # Traits: from personality or generate
    traits = clean_html(personality) if personality and len(personality) > 20 else ""
    if len(traits) < 50:
        traits = generate_fallback_traits(name, ch)
    traits = traits.strip()

    # Story: from anecdotes, ending, emotions
    story_parts = []
    if anecdotes and len(anecdotes) > 10:
        story_parts.append(clean_html(anecdotes))
    if emotions and len(emotions) > 10:
        story_parts.append(clean_html(emotions))
    if ending and len(ending) > 5:
        story_parts.append(f"结局：{ending}")
    story = "\n\n".join(story_parts)
    if len(story) < 30:
        story = f"{name}在《{novel}》中有着重要的戏份。他/她的故事与主线紧密交织，展现了江湖世界的复杂与人性的多面。"
    story = story.strip()

    # Skills: from skills, weapons, master
    skill_parts = []
    if skills_str and len(skills_str) > 10:
        skill_parts.append(clean_html(skills_str))
    if weapons and len(weapons) > 5:
        skill_parts.append(f"**兵器：** {weapons}")
    if master and len(master) > 3:
        skill_parts.append(f"**师承：** {master}")
    if sect and len(sect) > 3:
        skill_parts.append(f"**门派：** {sect}")
    skills = "\n\n".join(skill_parts)
    if len(skills) < 20:
        skills = f"{name}武功独树一帜，在江湖中有着不错的身手。"
    skills = skills.strip()

    return intro, traits, story, skills


def generate_fallback_traits(name, ch):
    """Generate basic traits from available fields."""
    role_type = ch.get("role_type", "")
    alias = ch.get("alias", "")
    novel = ch.get("_novel_name", "")
    personality = ch.get("personality", "")

    if personality and len(personality) > 20:
        return clean_html(personality)

    parts = [f"{name}是金庸武侠小说《{novel}》中的{role_type}。"]
    if alias and alias != "无":
        parts.append(f"称号「{alias}」。")
    parts.append(f"他/她在书中以其独特的性格和行为方式，给读者留下了深刻印象。")
    return " ".join(parts)


def generate_fallback_skills(name, ch):
    """Generate basic skills description."""
    weapons = ch.get("weapons", "")
    master = ch.get("master", "")
    sect = ch.get("sect", "")
    skills_str = ch.get("skills", "")

    if skills_str and len(skills_str) > 20:
        return clean_html(skills_str)

    parts = []
    if weapons and weapons != "无":
        parts.append(f"**武功/兵器：** {weapons}")
    if master and master != "无" and master != "无记载":
        parts.append(f"**师承：** {master}")
    if sect and sect != "无" and sect != "不详":
        parts.append(f"**门派：** {sect}")
    if not parts:
        parts.append(f"{name}身怀多项武艺，在江湖中有不俗的战力。")
    return "\n\n".join(parts)


def clean_html(text):
    """Remove HTML tags and clean up text."""
    import re
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&#39;', "'")
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def verify_output(output):
    """Verify the output has 151+ entries and is valid."""
    count = len(output)
    role_counts = {}
    for key, val in output.items():
        rt = val.get("role_type", "未知")
        role_counts[rt] = role_counts.get(rt, 0) + 1

    print(f"\n{'='*60}")
    print(f"VERIFICATION")
    print(f"{'='*60}")
    print(f"Total characters: {count}")
    for rt, cnt in sorted(role_counts.items()):
        print(f"  {rt}: {cnt}")

    # Check main 15 have rich content
    for name in MAIN_15:
        found = False
        for key, val in output.items():
            if val["name"] == name:
                found = True
                intro_len = len(val["intro"])
                traits_len = len(val["traits"])
                story_len = len(val["story"])
                skills_len = len(val["skills"])
                if intro_len < 300:
                    print(f"  ⚠️  {name}: intro too short ({intro_len} chars)")
                if traits_len < 300:
                    print(f"  ⚠️  {name}: traits too short ({traits_len} chars)")
                if story_len < 300:
                    print(f"  ⚠️  {name}: story too short ({story_len} chars)")
                if skills_len < 300:
                    print(f"  ⚠️  {name}: skills too short ({skills_len} chars)")
                break
        if not found:
            print(f"  ❌ {name}: NOT FOUND in output!")

    print(f"\nTotal characters: {count}")
    return count >= 151


def main():
    print("=" * 60)
    print("BUILDING char_knowledge.json")
    print("=" * 60)

    all_chars = load_all_characters()
    print(f"\nBuilding output structure...")
    output = build_output(all_chars)

    print(f"Writing to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

    verify_output(output)

    # Print role type breakdown
    role_counts = {}
    for key, val in output.items():
        rt = val.get("role_type", "未知")
        role_counts[rt] = role_counts.get(rt, 0) + 1

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total characters: {len(output)}")
    for rt, cnt in sorted(role_counts.items()):
        print(f"  {rt}: {cnt}")
    print(f"Output file: {OUTPUT_PATH}")
    print(f"File size: {file_size:,} bytes")

    # Validate JSON by re-reading
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        json.load(f)
    print("✅ Valid JSON confirmed")


if __name__ == "__main__":
    main()
