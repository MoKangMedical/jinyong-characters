#!/usr/bin/env python3
"""
Comprehensive Batch Course Generator for Jin Yong Characters
Generates all character courses with Kangbo template.
- 主角: 3000+ word rich courses
- 重要人物: 1500-2500 word courses
- 配角: 800-1200 word courses
"""
import json, os

COURSES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "courses")
CSS_PATH = "../../assets/kangbo.css"
HOME_PATH = "../../index.html"

# =========================================
# NOVEL KNOWLEDGE BASE
# =========================================
NOVEL_INFO = {
    "shediao": {"name": "射雕英雄传", "era": "南宋", "theme": "家国大义与侠之成长", "hero": "郭靖", "brief": "南宋末年，郭靖从草原少年成长为一代大侠，与黄蓉携手守护襄阳的故事。"},
    "shendiao": {"name": "神雕侠侣", "era": "南宋末", "theme": "至情至性与反叛精神", "hero": "杨过", "brief": "杨过与小龙女的旷世绝恋，以及对世俗礼法的挑战与超越。"},
    "yitian": {"name": "倚天屠龙记", "era": "元末明初", "theme": "正邪之辨与权力诱惑", "hero": "张无忌", "brief": "张无忌身负血海深仇，周旋于明教与六大派之间，最终看透权力本质。"},
    "tlbb": {"name": "天龙八部", "era": "北宋", "theme": "众生皆苦与命运无常", "hero": "乔峰/段誉/虚竹", "brief": "三位主角各自的人生悲剧，展现佛家「无人不冤，有情皆孽」的宏大主题。"},
    "xajh": {"name": "笑傲江湖", "era": "明朝", "theme": "权力腐蚀与自由追求", "hero": "令狐冲", "brief": "令狐冲在正邪派系斗争中保持本心，以洒脱不羁对抗权力的异化。"},
    "ldj": {"name": "鹿鼎记", "era": "清初", "theme": "反武侠与市井智慧", "hero": "韦小宝", "brief": "一个市井小混混凭借机智与运气周旋于朝廷与江湖之间，解构传统武侠神话。"},
    "shujian": {"name": "书剑恩仇录", "era": "清乾隆", "theme": "民族大义与儿女情长", "hero": "陈家洛", "brief": "红花会反清复明的故事，陈家洛在江山与美人之间的痛苦抉择。"},
    "bixue": {"name": "碧血剑", "era": "明末清初", "theme": "乱世忠义与个人命运", "hero": "袁承志", "brief": "袁承志继承父亲遗志，在明清交替的乱世中寻找自己的道路。"},
    "feihu": {"name": "飞狐外传", "era": "清乾隆", "theme": "复仇与成长", "hero": "胡斐", "brief": "胡斐为父报仇的成长历程，以及与程灵素、袁紫衣的情感纠葛。"},
    "xueshan": {"name": "雪山飞狐", "era": "清乾隆", "theme": "恩怨轮回与人性拷问", "hero": "胡斐", "brief": "一日之内，雪山之上，百年恩怨在一场决斗中集中爆发。"},
    "liancheng": {"name": "连城诀", "era": "清朝", "theme": "人性之恶与纯真坚守", "hero": "狄云", "brief": "狄云被陷害入狱，在人性最黑暗的角落里，仍有一丝纯真未曾泯灭。"},
    "xiake": {"name": "侠客行", "era": "明朝", "theme": "真伪之辨与返璞归真", "hero": "石破天", "brief": "一个不知自己是谁的少年，以赤子之心破解了武林至高武学。"},
    "yuanyang": {"name": "鸳鸯刀", "era": "清朝", "theme": "江湖谐趣与侠义精神", "hero": "袁冠南/萧中慧", "brief": "一对鸳鸯刀引发的江湖追逐，以诙谐笔法写出侠义精神的真谛。"},
    "baima": {"name": "白马啸西风", "era": "唐朝", "theme": "爱而不得与塞上情怀", "hero": "李文秀", "brief": "大漠中的一段刻骨铭心的单恋故事。"},
    "yuenv": {"name": "越女剑", "era": "春秋", "theme": "剑道真谛与家国情怀", "hero": "阿青", "brief": "越女阿青以无招胜有招的绝世剑法，助越王勾践复仇的故事。"},
}

# =========================================
# CHARACTER KNOWLEDGE (loaded from JSON)
# =========================================
CHAR_KNOWLEDGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'char_knowledge.json')
with open(CHAR_KNOWLEDGE_FILE) as f:
    CHAR_KNOWLEDGE = json.load(f)

# =========================================
# HTML TEMPLATES
# =========================================

# Kangbo-style course HTML template
TPL_COURSE = '''
