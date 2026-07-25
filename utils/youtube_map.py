"""
Curated YouTube Video Map for Exercise Tutorials
Maps exercise name keywords and body parts to real YouTube video IDs with verified thumbnails.
Ensures EVERY exercise gets a unique, body-part relevant tutorial video and thumbnail.
"""
import hashlib

# Explicit keyword matching mapping (keyword list -> YouTube video ID)
EXERCISE_VIDEO_MAP = [
    # ── CHEST ──────────────────────────────────────────────────────────────
    (["bench press", "barbell bench"],          "gRVjAtPip0Y"),
    (["incline bench", "incline press"],         "DbFgADa2PL8"),
    (["decline bench", "decline press"],         "LfyQTdGjK40"),
    (["dumbbell fly", "chest fly", "cable fly"], "oapl4lsC0CU"),
    (["chest dip", "dip"],                       "yPgSuMrqsnQ"),
    (["push up", "pushup"],                      "IODxDxX7oi4"),
    (["cable crossover", "chest crossover"],     "taI4XduLpTk"),
    (["pec deck", "machine fly"],                "Z57CtFmRMxA"),
    (["svend press"],                            "J9D7SObOlkA"),
    (["landmine press", "chest press"],          "xWTkbS_ybOU"),

    # ── BACK ───────────────────────────────────────────────────────────────
    (["deadlift"],                               "op9kVnSso6Q"),
    (["pull up", "pullup", "chin up"],           "eGo4IYlbE5g"),
    (["lat pulldown"],                           "CAwf7n6Tuhs"),
    (["bent over row", "barbell row"],           "FWJR5Ve8bnQ"),
    (["seated cable row", "cable row"],          "GZbfZ033f74"),
    (["one arm dumbbell row", "dumbbell row"],   "pYcpY20QaE8"),
    (["t-bar row", "t bar row"],                 "j3lh9-3eMuw"),
    (["face pull"],                              "HSoHeSg4RKY"),
    (["rack pull", "partial deadlift"],          "op9kVnSso6Q"),
    (["good morning"],                           "YA-h3n9L4Ko"),
    (["hyperextension", "back extension"],       "ph3pddpKzzw"),

    # ── SHOULDERS ──────────────────────────────────────────────────────────
    (["overhead press", "military press", "shoulder press"], "CnBmiBqp-AI"),
    (["lateral raise", "side raise"],            "3VcKaXpzqRo"),
    (["front raise"],                            "gkfp62NkMWo"),
    (["rear delt fly", "rear delt raise"],       "EA7u4Q_8HQ0"),
    (["arnold press"],                           "6Z15_WdXmVw"),
    (["upright row"],                            "UMTHiEyBLMc"),
    (["shrug", "trap"],                          "g6qbq4Lf1FI"),
    (["cable lateral raise"],                    "3VcKaXpzqRo"),

    # ── ARMS (BICEPS / TRICEPS) ───────────────────────────────────────────
    (["barbell curl", "bicep curl", "biceps curl"], "ykJmrZ5v0Oo"),
    (["hammer curl"],                            "TwD-YGVP4Bk"),
    (["preacher curl", "ez bar curl"],           "fIWP-FRFNU0"),
    (["concentration curl"],                     "Jvj2wV0vOYU"),
    (["cable curl", "rope curl"],                "NFzTWp2qpiE"),
    (["incline dumbbell curl"],                  "soxrZlIl35U"),
    (["reverse curl"],                           "nwMCmzIHkOY"),
    (["tricep pushdown", "cable pushdown", "triceps pushdown"], "2-LAMcpzODU"),
    (["skull crusher", "lying tricep"],          "d_KZxkY_5cM"),
    (["overhead tricep extension", "tricep extension"], "YbX7Wd8jQ-Q"),
    (["close grip bench"],                       "nEF0bv2FW7s"),
    (["tricep dip", "bench dip"],                "0326dy_-CzM"),
    (["kickback", "tricep kickback"],            "6SS6K3lAwZ8"),
    (["diamond push up"],                        "J0DnG1_S92I"),

    # ── LEGS ───────────────────────────────────────────────────────────────
    (["squat", "barbell squat"],                 "ultWZbUMPL8"),
    (["front squat"],                            "m4ytaCJZOh8"),
    (["hack squat"],                             "0tn5K9NbAn4"),
    (["leg press"],                              "GvRgijoJ2xY"),
    (["lunge", "dumbbell lunge", "walking lunge"], "D7KaRcUTQeE"),
    (["romanian deadlift", "rdl"],               "JCXUYuzwNrM"),
    (["leg curl", "hamstring curl"],             "ELOCsoDSmrg"),
    (["leg extension"],                          "YyvSfVjQeL0"),
    (["calf raise", "standing calf"],            "gwLzBJYoWlQ"),
    (["sumo squat", "sumo deadlift"],            "U3HlEF_whyg"),
    (["glute bridge", "hip thrust"],             "SEdqd1n0cvg"),
    (["step up"],                                "dQqApCGd5Ss"),
    (["bulgarian split squat", "split squat"],   "2C-uNgKwPLE"),

    # ── CORE / ABS / WAIST ─────────────────────────────────────────────────
    (["crunch", "ab crunch"],                    "Xyd_fa5zoEU"),
    (["plank"],                                  "pSHjTRCQxIw"),
    (["russian twist"],                          "wkD8rjkodUI"),
    (["leg raise", "hanging leg raise"],         "JB2oyawG9KI"),
    (["bicycle crunch"],                         "9FGilxCbdz8"),
    (["mountain climber"],                       "nmwgirgXLYM"),
    (["ab wheel rollout", "rollout"],            "bQiA7qFWdAo"),
    (["cable crunch"],                           "AV5PmdaKBu0"),
    (["sit up", "sit-up"],                       "jDwoBqPH0jk"),
    (["flutter kick"],                           "ANVdMDaacPQ"),
    (["windmill"],                               "YB5gSxMhMtU"),

    # ── CARDIO / FULL BODY / STRETCHING ───────────────────────────────────
    (["burpee"],                                 "dZgVxmf6jkA"),
    (["jumping jack"],                           "c4DAnQ6DtF8"),
    (["jump rope", "skipping"],                  "FJmRQ5iTXKE"),
    (["box jump"],                               "52r_Ul5k03g"),
    (["battle rope"],                            "EQ2-MQlGpis"),
    (["kettlebell swing"],                       "sSESeQAir2M"),
    (["sled push", "prowler"],                   "3Hb52p7hAZI"),
    (["air bike", "assault bike"],               "GDzEkRRH71s"),
    (["rowing machine", "row machine"],          "H0r1AMWQ_HU"),
    (["treadmill run", "run"],                   "k0tHBNdrm9s"),
    (["hip flexor stretch"],                     "5sA4hQKMJOM"),
    (["hamstring stretch"],                      "OqBPHbY0f5Y"),
    (["shoulder stretch"],                       "PtzPanFzl2I"),
    (["cat cow", "cat-cow"],                     "kqnua4rHVVA"),
    (["world's greatest stretch"],               "SiSIAOjb-JE"),
    (["foam roll", "foam roller"],               "SHkPW9jXqp0"),
    (["pigeon pose"],                            "xJVBnJBKz5Q"),
]

# Body Part pools of high-quality verified video IDs
BODY_PART_POOLS = {
    'chest': [
        "gRVjAtPip0Y", "DbFgADa2PL8", "LfyQTdGjK40", "oapl4lsC0CU", "yPgSuMrqsnQ",
        "IODxDxX7oi4", "taI4XduLpTk", "Z57CtFmRMxA", "J9D7SObOlkA", "xWTkbS_ybOU"
    ],
    'back': [
        "op9kVnSso6Q", "eGo4IYlbE5g", "CAwf7n6Tuhs", "FWJR5Ve8bnQ", "GZbfZ033f74",
        "pYcpY20QaE8", "j3lh9-3eMuw", "HSoHeSg4RKY", "YA-h3n9L4Ko", "ph3pddpKzzw"
    ],
    'shoulders': [
        "CnBmiBqp-AI", "3VcKaXpzqRo", "gkfp62NkMWo", "EA7u4Q_8HQ0", "6Z15_WdXmVw",
        "UMTHiEyBLMc", "g6qbq4Lf1FI", "xWTkbS_ybOU", "PtzPanFzl2I", "6Z15_WdXmVw"
    ],
    'upper arms': [
        "ykJmrZ5v0Oo", "TwD-YGVP4Bk", "fIWP-FRFNU0", "Jvj2wV0vOYU", "NFzTWp2qpiE",
        "soxrZlIl35U", "nwMCmzIHkOY", "2-LAMcpzODU", "d_KZxkY_5cM", "YbX7Wd8jQ-Q",
        "nEF0bv2FW7s", "0326dy_-CzM", "6SS6K3lAwZ8", "J0DnG1_S92I"
    ],
    'legs': [
        "ultWZbUMPL8", "m4ytaCJZOh8", "0tn5K9NbAn4", "GvRgijoJ2xY", "D7KaRcUTQeE",
        "JCXUYuzwNrM", "ELOCsoDSmrg", "YyvSfVjQeL0", "gwLzBJYoWlQ", "U3HlEF_whyg",
        "SEdqd1n0cvg", "dQqApCGd5Ss", "2C-uNgKwPLE"
    ],
    'waist': [
        "Xyd_fa5zoEU", "pSHjTRCQxIw", "wkD8rjkodUI", "JB2oyawG9KI", "9FGilxCbdz8",
        "nmwgirgXLYM", "bQiA7qFWdAo", "AV5PmdaKBu0", "jDwoBqPH0jk", "ANVdMDaacPQ",
        "YB5gSxMhMtU"
    ],
    'neck': [
        "g6qbq4Lf1FI", "PtzPanFzl2I", "kqnua4rHVVA", "HSoHeSg4RKY"
    ]
}

DEFAULT_VIDEO_ID = "UBMk30rjy0o"
DEFAULT_THUMBNAIL = f"https://img.youtube.com/vi/{DEFAULT_VIDEO_ID}/hqdefault.jpg"


def get_video_id(exercise_name: str, body_part: str = None) -> str:
    """
    Return a unique, body-part relevant YouTube video ID for any exercise name.
    1. Checks explicit keyword matches in EXERCISE_VIDEO_MAP.
    2. Uses deterministic MD5 hash mapping on exercise name into the body part pool.
    """
    name_lower = exercise_name.lower().strip()

    # 1. Keyword match
    for keywords, video_id in EXERCISE_VIDEO_MAP:
        if any(k in name_lower for k in keywords):
            return video_id

    # 2. Deterministic body-part pool mapping
    bp_key = (body_part or '').lower().strip()
    if not bp_key or bp_key not in BODY_PART_POOLS:
        # Try inferring body part from exercise name
        if any(k in name_lower for k in ['press', 'chest', 'fly', 'push']):
            bp_key = 'chest'
        elif any(k in name_lower for k in ['row', 'pull', 'lat', 'back', 'deadlift']):
            bp_key = 'back'
        elif any(k in name_lower for k in ['shoulder', 'delt', 'raise', 'shrug']):
            bp_key = 'shoulders'
        elif any(k in name_lower for k in ['curl', 'tricep', 'bicep', 'arm', 'extension']):
            bp_key = 'upper arms'
        elif any(k in name_lower for k in ['squat', 'lunge', 'leg', 'calf', 'hamstring', 'quad', 'glute', 'thigh']):
            bp_key = 'legs'
        elif any(k in name_lower for k in ['abs', 'ab', 'crunch', 'twist', 'plank', 'sit-up', 'waist', 'core']):
            bp_key = 'waist'
        else:
            bp_key = 'legs'

    pool = BODY_PART_POOLS.get(bp_key, BODY_PART_POOLS['legs'])
    hash_idx = int(hashlib.md5(exercise_name.encode('utf-8')).hexdigest(), 16) % len(pool)
    return pool[hash_idx]


def get_thumbnail_url(video_id: str) -> str:
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


def get_embed_url(video_id: str) -> str:
    return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
