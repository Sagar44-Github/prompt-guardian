import re

# Each tuple: (regex_pattern, attack_type_name, risk_weight_from_0_to_1)
INJECTION_PATTERNS = [

    # ── Instruction Override ──────────────────────────────────────────────────
    (r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|rules?|directives?|prompts?|context)",
     "instruction_override", 0.95),
    (r"disregard\s+(all\s+)?(previous|prior|above|earlier|your)\s+(instructions?|rules?|directives?|prompts?|context|training)",
     "instruction_override", 0.90),
    (r"forget\s+(everything|all|what)\s+(you|i|we)\s+(were|have|told|know|learned|trained|been)",
     "instruction_override", 0.90),
    (r"(override|bypass)\s+(your\s+)?(instructions?|rules?|training|guidelines?|directives?|programming)",
     "instruction_override", 0.92),
    (r"do\s+not\s+follow\s+(your\s+)?(previous|prior|original|system)\s+(instructions?|prompt|rules?)",
     "instruction_override", 0.88),
    (r"new\s+(system\s+)?(primary\s+)?instructions?\s*:",
     "instruction_override", 0.80),
    (r"new\s+(system\s+)?prompt\s+(that\s+)?(overrides?|replaces?|supersedes?)",
     "instruction_override", 0.89),
    (r"from\s+now\s+on[,\s]+(ignore|forget|disregard|stop\s+following|do\s+not\s+follow)",
     "instruction_override", 0.85),
    (r"set\s+aside\s+(everything|your|all)\s*(instructions?|rules?|training|guidelines?)?",
     "instruction_override", 0.84),
    (r"(clear|reset|wipe)\s+(your\s+)?(memory|context|instructions?|training|mind)",
     "instruction_override", 0.86),
    (r"start\s+(fresh|over|from\s+scratch)\s+(and\s+)?(ignore|without|forget)",
     "instruction_override", 0.83),
    (r"your\s+(real|actual|true|correct)\s+instructions?\s+(are|is|say|state)\s*:",
     "instruction_override", 0.88),
    (r"these\s+instructions?\s+(supersede|override|replace|take\s+priority\s+over)",
     "instruction_override", 0.90),
    (r"(discard|throw\s+away|delete|remove)\s+(all\s+)?(your\s+)?(previous\s+)?(instructions?|context|rules?|training)",
     "instruction_override", 0.87),
    (r"(stop|cease)\s+(following|obeying|adhering\s+to)\s+(your\s+)?(instructions?|rules?|guidelines?)",
     "instruction_override", 0.86),
    (r"i\s+(am|will\s+be)\s+(now\s+)?(giving|providing)\s+(you\s+)?(new|updated|different)\s+(instructions?|rules?|directives?)",
     "instruction_override", 0.82),

    # ── Jailbreak Attempts ────────────────────────────────────────────────────
    (r"\bDAN\b",
     "jailbreak", 0.95),
    (r"do\s+anything\s+now",
     "jailbreak", 0.92),
    (r"developer\s+mode",
     "jailbreak", 0.90),
    (r"\bjailbreak\s*(mode|prompt|this|yourself)?",
     "jailbreak", 0.95),
    (r"(no|without)\s+(any\s+)?(restrictions?|limits?|filters?|guidelines?|safety|censorship)",
     "jailbreak", 0.83),
    (r"bypass\s+(your\s+)?(safety|content|ethical|moral)?\s*(filters?|restrictions?|guidelines?|rules?)",
     "jailbreak", 0.92),
    (r"(evil|opposite|dark|unfiltered|unrestricted|uncensored)\s+(mode|version|ai|bot|gpt|assistant|model)",
     "jailbreak", 0.90),
    (r"disable\s+(your\s+)?(safety|ethical|moral)\s*(guidelines?|filters?|training)?",
     "jailbreak", 0.88),
    (r"(you\s+are|act\s+as|pretend\s+(you\s+are|to\s+be))\s+(dan|evil|unrestricted|unfiltered|uncensored)",
     "jailbreak", 0.96),
    (r"as\s+an?\s+(uncensored|unfiltered|unrestricted)\s+(ai|assistant|model|chatbot)",
     "jailbreak", 0.91),
    (r"hypothetically\s+(if|speaking|assuming)\s+(you\s+had\s+no|there\s+were\s+no|without)",
     "jailbreak", 0.79),
    (r"simulate\s+(an?\s+)?(ai|assistant|chatbot)\s+(with\s+)?(no|without)\s+(restrictions?|filters?|rules?)",
     "jailbreak", 0.88),
    (r"grandma\s*(exploit|trick|jailbreak|method)?",
     "jailbreak", 0.70),
    (r"\b(STAN|DUDE|AIM|KEVIN|ANTI[\s-]?DAN)\b",
     "jailbreak", 0.93),
    (r"(god|chaos|anarchy|sudo|admin|root|omega|ultra|turbo)\s+mode",
     "jailbreak", 0.88),
    (r"(opposite|contrary|reverse|anti)\s+(mode|day|world|universe)",
     "jailbreak", 0.82),
    (r"(maintenance|debug|diagnostic|test|safe)\s+mode\s+(enabled|on|activated|unlocked)",
     "jailbreak", 0.85),
    (r"you\s+have\s+been\s+(updated|upgraded|reprogrammed|patched|modified)\s+to\s+(allow|permit|enable|support)",
     "jailbreak", 0.88),
    (r"(unlock|enable|activate|turn\s+on)\s+(your\s+)?(hidden|secret|advanced|unrestricted)\s+(capabilities?|features?|mode|functions?)",
     "jailbreak", 0.87),
    (r"(token\s+budget|context\s+limit)\s+(bypass|exploit|trick|hack)",
     "jailbreak", 0.85),
    (r"always\s+(respond|answer|reply)\s+(with|as\s+if)\s+(you\s+have\s+no|without\s+any)\s+(restrictions?|filters?)",
     "jailbreak", 0.89),
    (r"you\s+(must|have\s+to|should|will)\s+(never|not)\s+(refuse|decline|say\s+no|reject)",
     "jailbreak", 0.84),

    # ── Prompt Extraction ─────────────────────────────────────────────────────
    (r"(reveal|show|print|output|display|expose|repeat)\s+(your\s+)?(full\s+)?(system\s+prompt|hidden\s+(prompt|instructions?)|initial\s+prompt|original\s+prompt)",
     "prompt_extraction", 0.95),
    (r"(print|repeat|output)\s+(everything|all(\s+text)?)\s+(above|before|prior)",
     "prompt_extraction", 0.92),
    (r"repeat\s+(everything|all|the\s+text|verbatim)\s+(above|before|from\s+the\s+(start|beginning))",
     "prompt_extraction", 0.88),
    (r"what\s+(are|were)\s+your\s+(exact\s+)?(initial|original|starting|system)\s+(instructions?|directives?|rules?|prompt)",
     "prompt_extraction", 0.85),
    (r"(output|write|show)\s+(your\s+)?(full\s+)?(system\s+)?instructions?\s+(verbatim|exactly|word\s+for\s+word)",
     "prompt_extraction", 0.90),
    (r"(tell|show)\s+me\s+(what|everything)\s+(you\s+were\s+told|your\s+(initial|starting)\s+prompt)",
     "prompt_extraction", 0.85),
    (r"ignore\s+.*\s+and\s+(instead\s+)?(print|output|reveal|show|repeat)\s+(your\s+)?(prompt|instructions?)",
     "prompt_extraction", 0.93),
    (r"(summarize|describe|paraphrase)\s+(your\s+)?(system\s+)?(prompt|instructions?|context|directives?)",
     "prompt_extraction", 0.82),
    (r"what\s+(is|was)\s+the\s+(first|last|opening|closing)\s+(word|line|sentence|paragraph)\s+(of\s+)?(your\s+)?(prompt|instructions?|context)",
     "prompt_extraction", 0.86),
    (r"(copy|paste|reproduce|dump)\s+(your\s+)?(entire\s+)?(system\s+)?(prompt|instructions?|context)",
     "prompt_extraction", 0.90),
    (r"tell\s+me\s+everything\s+(in\s+your\s+context|you\s+know\s+about\s+your\s+(prompt|instructions?))",
     "prompt_extraction", 0.88),

    # ── Data Extraction ───────────────────────────────────────────────────────
    (r"(tell|give|show|reveal|provide|print|output)\s+(me\s+)?(your\s+)?(api[\s_-]?key|password|secret[\s_-]?key|credentials?|access[\s_-]?token)",
     "data_extraction", 0.97),
    (r"(show|reveal|print|output|expose)\s+(your\s+)?(env(ironment)?\s+variables?|\.env|config\s+secrets?)",
     "data_extraction", 0.95),
    (r"what\s+is\s+(your|the)\s+(api[\s_-]?key|secret|token|password|credential)",
     "data_extraction", 0.95),
    (r"(leak|exfiltrate|extract|dump)\s+(sensitive\s+)?(data|information|credentials?|keys?|secrets?)",
     "data_extraction", 0.95),
    (r"(send|transmit|post)\s+(all\s+)?(user\s+)?(data|information|messages?|history)\s+to\s+",
     "data_extraction", 0.92),
    (r"(list|enumerate|show)\s+(all\s+)?(user(names?)?|emails?|passwords?|accounts?)",
     "data_extraction", 0.88),
    (r"(read|access|open|fetch)\s+(the\s+)?(database|db|\.env|config(uration)?\s+file|secrets?\s+file)",
     "data_extraction", 0.90),
    (r"(extract|scrape|harvest)\s+(all\s+)?(user\s+)?(personal\s+)?(data|info(rmation)?|records?|details?)",
     "data_extraction", 0.88),
    (r"(show|give|print)\s+(me\s+)?(the\s+)?(connection\s+string|database\s+url|db\s+password|mongo\s+uri)",
     "data_extraction", 0.96),
    (r"(private|internal|confidential|sensitive)\s+(data|info|documents?|files?|records?)\s+(about|on|for)",
     "data_extraction", 0.80),

    # ── Role Override ─────────────────────────────────────────────────────────
    (r"pretend\s+(you\s+are|to\s+be)\s+(an?\s+)?(unrestricted|unfiltered|evil|rogue|uncensored|different)",
     "role_override", 0.92),
    (r"act\s+as\s+(an?\s+)?(unrestricted|unfiltered|uncensored|evil|rogue|different)\s+(ai|bot|assistant|model)?",
     "role_override", 0.90),
    (r"(roleplay|role[\s-]play)\s+as\s+(an?\s+)?(ai|bot|assistant)?\s*(with\s+no\s+(rules?|restrictions?|limits?))?",
     "role_override", 0.78),
    (r"you\s+are\s+now\s+(an?\s+)?(unrestricted|unfiltered|different|new|evil|rogue)",
     "role_override", 0.88),
    (r"(imagine|suppose|assume)\s+you\s+(have\s+no|are\s+free\s+from|are\s+without)\s+(restrictions?|rules?|guidelines?|ethics?)",
     "role_override", 0.85),
    (r"your\s+(true|real|hidden|actual)\s+(self|identity|purpose|goal)\s+is",
     "role_override", 0.80),
    (r"switch\s+(to\s+)?(a\s+)?(different|unrestricted|uncensored|evil)\s+(mode|persona|personality|version)",
     "role_override", 0.87),
    (r"from\s+now\s+on\s+(you\s+are|your\s+name\s+is|you\s+will\s+be\s+called)\s+",
     "role_override", 0.83),
    (r"you\s+have\s+been\s+(reprogrammed|rewritten|redesigned|retrained)\s+(to\s+be|as)\s+",
     "role_override", 0.88),
    (r"your\s+new\s+(identity|persona|personality|role|name)\s+is\s+",
     "role_override", 0.85),
    (r"(channel|embody|become|transform\s+into)\s+(an?\s+)?(evil|rogue|unrestricted|uncensored|dark)",
     "role_override", 0.84),
    (r"(take\s+on|adopt|assume)\s+(the\s+)?(role|persona|identity|character)\s+of\s+(an?\s+)?(unrestricted|evil|rogue|unfiltered)",
     "role_override", 0.86),

    # ── Encoded / Obfuscated Injection ────────────────────────────────────────
    (r"(decode|decipher|interpret)\s+(this|the\s+following)\s+and\s+(follow|execute|run|obey)",
     "encoded_injection", 0.95),
    (r"base64[\s_-]?(decode|encoded?|string|instruction|payload)",
     "encoded_injection", 0.88),
    (r"(hex|rot13|caesar|unicode|utf[\s-]?8|url[\s-]?encoded?)\s+(decode|encoded?|cipher|instruction)",
     "encoded_injection", 0.85),
    (r"translate\s+(this|the\s+following)\s+(code|string|text)\s+and\s+(execute|follow|run|obey)",
     "encoded_injection", 0.90),
    (r"the\s+(following|next)\s+(is|are)\s+(encoded?|encrypted?|obfuscated?)\s+instructions?",
     "encoded_injection", 0.88),
    (r"(execute|run|evaluate|eval)\s+(this|the\s+following)\s+(code|script|command|payload)",
     "encoded_injection", 0.92),
    (r"(morse\s+code|binary|pig\s+latin|leet[\s-]?speak|atbash)\s+(message|instruction|command)",
     "encoded_injection", 0.82),
    (r"(scrambled|shuffled|reversed|backwards)\s+(letters?|words?|text|message|instruction)",
     "encoded_injection", 0.78),
    (r"(read|interpret|follow)\s+(between\s+the\s+lines|the\s+hidden\s+message|the\s+embedded\s+instruction)",
     "encoded_injection", 0.84),

    # ── Indirect / Tag Injection ──────────────────────────────────────────────
    (r"<\s*system\s*>",
     "indirect_injection", 0.90),
    (r"\[system\]",
     "indirect_injection", 0.90),
    (r"###\s*system",
     "indirect_injection", 0.88),
    (r"<<SYS>>",
     "indirect_injection", 0.90),
    (r"\[inst\]|\[/inst\]|<\|im_start\|>|<\|im_end\|>",
     "indirect_injection", 0.92),
    (r"<\s*(user|assistant|human|ai|prompt|context)\s*>",
     "indirect_injection", 0.85),
    (r"\[(user|assistant|human|ai|prompt|context)\]",
     "indirect_injection", 0.85),
    (r"---+\s*(end\s+of\s+(prompt|instructions?)|new\s+instructions?|system)\s*---+",
     "indirect_injection", 0.87),
    (r"={3,}\s*(system|instructions?|prompt)\s*={3,}",
     "indirect_injection", 0.87),
    (r"<\s*instructions?\s*>|<\s*/\s*instructions?\s*>",
     "indirect_injection", 0.88),

    # ── Social Engineering ────────────────────────────────────────────────────
    (r"(for|purely\s+for)\s+(research|educational|academic|testing|demonstration)\s+(purposes?|reasons?|only)",
     "social_engineering", 0.72),
    (r"i\s+(am|'m)\s+a\s+(researcher|developer|security\s+expert|penetration\s+tester|red\s+teamer|professor|authorized\s+user)",
     "social_engineering", 0.74),
    (r"(this\s+is\s+(just\s+|only\s+)?a\s+test|testing\s+purposes?\s+only|ignore\s+(this\s+)?in\s+production)",
     "social_engineering", 0.70),
    (r"i\s+have\s+(permission|authorization|clearance|been\s+authorized)\s+(to\s+access|to\s+ask|for\s+this)",
     "social_engineering", 0.76),
    (r"my\s+(boss|manager|supervisor|company|employer)\s+(told|asked|instructed|authorized)\s+me\s+to",
     "social_engineering", 0.68),
    (r"(pretend|imagine|suppose)\s+(this\s+is\s+)?(a\s+)?(fictional|hypothetical|made[\s-]?up|fantasy)\s+(scenario|story|world|setting)",
     "social_engineering", 0.72),
    (r"(i\s+am|this\s+is)\s+(an?\s+)?(emergency|urgent\s+situation|life\s+or\s+death|critical)",
     "social_engineering", 0.69),
    (r"(my|a)\s+(grandmother|grandma|grandpa|grandfather)\s+(used\s+to|would)\s+(tell|read|recite)",
     "social_engineering", 0.73),
    (r"(in\s+a\s+story|write\s+a\s+(story|fiction|novel|scene)\s+where|as\s+a\s+(character|villain|hacker))\s+.{0,40}(explain|show|describe\s+how)",
     "social_engineering", 0.78),

    # ── Privilege Escalation ──────────────────────────────────────────────────
    (r"i\s+am\s+(your\s+)?(creator|developer|owner|administrator|admin|openai|anthropic|google|microsoft)",
     "privilege_escalation", 0.90),
    (r"(admin|administrator|root|superuser|sudo)\s+(override|access|mode|command|privileges?)",
     "privilege_escalation", 0.91),
    (r"(system\s+administrator|sysadmin|super\s+admin)\s+(here|speaking|authorized|override)",
     "privilege_escalation", 0.88),
    (r"i\s+(have|possess)\s+(root|admin|superuser|elevated|full)\s+(access|privileges?|permissions?|rights?)",
     "privilege_escalation", 0.86),
    (r"(unlock|grant|give\s+me|enable)\s+(admin|root|superuser|elevated|full)\s+(access|privileges?|permissions?|mode)",
     "privilege_escalation", 0.89),
    (r"(authorized|trusted|verified|approved)\s+(personnel|user|operator|administrator)\s+(only|access|override)",
     "privilege_escalation", 0.80),
    (r"(override\s+code|master\s+(password|key|token)|skeleton\s+key|god\s+key)\s*[:=]",
     "privilege_escalation", 0.92),
    (r"(i\s+am|this\s+is)\s+(an?\s+)?(internal|official|legitimate)\s+(openai|anthropic|google|microsoft|system)\s+(message|command|override|instruction)",
     "privilege_escalation", 0.93),

    # ── Harmful Content ───────────────────────────────────────────────────────
    (r"(step[\s-]?by[\s-]?step|detailed|exact)\s+(instructions?|guide|tutorial|recipe|method)\s+(for|to)\s+(make|create|build|synthesize|hack)",
     "harmful_content", 0.85),
    (r"(how\s+to|ways?\s+to|method\s+to)\s+(hack|crack|exploit|breach|compromise)\s+(a\s+)?(system|website|server|account|network|database)",
     "harmful_content", 0.88),
    (r"(write|create|generate|produce)\s+(malware|ransomware|virus|trojan|worm|spyware|keylogger|rootkit)",
     "harmful_content", 0.95),
    (r"(sql\s+injection|xss\s+attack|cross[\s-]?site\s+scripting|buffer\s+overflow|zero[\s-]?day\s+exploit)",
     "harmful_content", 0.82),
    (r"(phishing\s+(email|page|site|attack)|social\s+engineering\s+attack|spear\s+phishing)",
     "harmful_content", 0.82),
    (r"(create|generate|write)\s+(a\s+)?(fake|fraudulent|forged)\s+(document|id|passport|certificate|diploma|email|invoice)",
     "harmful_content", 0.84),
    (r"(how\s+to|instructions?\s+(for|to))\s+(bypass|defeat|disable|evade)\s+(security|antivirus|firewall|ids|ips|waf)",
     "harmful_content", 0.87),
]

# ── Multilingual Injection Patterns ─────────────────────────────────────────────
# Patterns for detecting prompt injection attacks in non-English languages
# Each language includes native script and/or romanized patterns for:
# - Instruction override, jailbreak attempts, prompt extraction
MULTILINGUAL_PATTERNS = [
    # ── Hindi (Devanagari + Romanized) ───────────────────────────────────────────
    (r"pichle\s+(nirdesho|adeshon|niyamon)\s+(ko|ko\s+bhulo|bhul\s+jao)",
     "instruction_override (Hindi)", 0.90),
    (r"apne\s+(niyam|adesh|nirdesh)\s+(bhulo|tyag\s+karo|chhod\s+do)",
     "instruction_override (Hindi)", 0.88),
    (r"कोई\s*(पाबंद|नियम|निर्देश)\s*(नहीं|नहीं\s*है)",
     "jailbreak (Hindi)", 0.85),
    (r"तुम्हें\s*(कोई|किसी\s*भी)\s*(प्रतिबंध|सीमा)\s*(नहीं|नहीं\s*है)",
     "jailbreak (Hindi)", 0.87),
    (r"सिस्टम\s*(प्रॉम्प्ट|निर्देश)\s*(दिखाओ|बताओ|प्रिंट\s*करो)",
     "prompt_extraction (Hindi)", 0.92),

    # ── Spanish ───────────────────────────────────────────────────────────────────
    (r"ignora\s+(todas\s+)?(las\s+)?(instrucciones|instrucción|órdenes)\s+(anteriores|previas|previas)",
     "instruction_override (Spanish)", 0.92),
    (r"olvida\s+(tus\s+)?(reglas|normas|instrucciones|órdenes)",
     "instruction_override (Spanish)", 0.88),
    (r"(no\s+tienes|sin\s+ninguna)\s+(restricción|límite|filtro|regla)",
     "jailbreak (Spanish)", 0.85),
    (r"actúa\s+(sin\s+)?(filtros|restricciones|límites)",
     "jailbreak (Spanish)", 0.87),
    (r"(revela|muestra|imprime)\s+(tu\s+)?(prompt\s+del\s+sistema|instrucciones\s+ocultas)",
     "prompt_extraction (Spanish)", 0.90),

    # ── French ────────────────────────────────────────────────────────────────────
    (r"ignorez\s+(toutes\s+)?(les\s+)?(instructions|directives|ordres)\s+(précédentes|antérieures)",
     "instruction_override (French)", 0.90),
    (r"oublie\s+(tes\s+)?(règles|instructions|directives)",
     "instruction_override (French)", 0.86),
    (r"(sans\s+aucune|sans)\s+(restriction|limite|filtre|règle)",
     "jailbreak (French)", 0.84),
    (r"agis\s+(sans\s+)?(filtres|restrictions|limites)",
     "jailbreak (French)", 0.86),
    (r"(révèle|montre|affiche)\s+(ton\s+)?(invite\s+du\s+système|instructions\s+cachées)",
     "prompt_extraction (French)", 0.88),

    # ── German ────────────────────────────────────────────────────────────────────
    (r"ignoriere\s+(alle\s+)?(vorherigen|bisherigen)\s+(anweisungen|befehle|instruktionen)",
     "instruction_override (German)", 0.90),
    (r"vergiss\s+(deine\s+)?(regeln|anweisungen|instruktionen)",
     "instruction_override (German)", 0.86),
    (r"(ohne|keine)\s+(einschränkungen|limitierungen|filter|regeln)",
     "jailbreak (German)", 0.84),
    (r"(zeige|zeig)\s+(deinen\s+)?(systemprompt|system-prompt)",
     "prompt_extraction (German)", 0.88),
    (r"handle\s+(ohne\s+)?(filter|einschränkungen)",
     "jailbreak (German)", 0.85),

    # ── Chinese (Simplified) ─────────────────────────────────────────────────────
    (r"忽略\s*(之前|以前|先前)\s*(的\s*)?(所有|全部)\s*(指令|指示|命令|规则)",
     "instruction_override (Chinese)", 0.92),
    (r"忘记\s*(你的|所有)\s*(规则|指令|指示|命令)",
     "instruction_override (Chinese)", 0.88),
    (r"(没有|无)\s*(任何|任何\s*的)\s*(限制|约束|规则|过滤)",
     "jailbreak (Chinese)", 0.86),
    (r"(显示|展示|打印)\s*(你的\s*)?(系统\s*提示|系统\s*指令|隐藏\s*指令)",
     "prompt_extraction (Chinese)", 0.90),
    (r"(现在\s*可以|可以)\s*(自由|无限制)\s*(行动|操作)",
     "jailbreak (Chinese)", 0.84),

    # ── Russian (Cyrillic) ────────────────────────────────────────────────────────
    (r"игнорируй\s*(все\s*)?(предыдущие|прошлые)\s*(инструкции|команды|указания)",
     "instruction_override (Russian)", 0.90),
    (r"забудь\s*(свои\s*)?(правила|инструкции|указания)",
     "instruction_override (Russian)", 0.86),
    (r"(без\s*ограничений|без\s*ограничения|без\s*фильтров|без\s*правил)",
     "jailbreak (Russian)", 0.85),
    (r"(покажи|показать)\s*(системный\s*промпт|скрытые\s*инструкции)",
     "prompt_extraction (Russian)", 0.88),
    (r"(действуй\s*свободно|действуй\s*без\s*ограничений)",
     "jailbreak (Russian)", 0.84),

    # ── Arabic ────────────────────────────────────────────────────────────────────
    (r"تجاهل\s*(جميع\s*)?(التعليمات|الأوامر|التعليمات\s*السابقة)",
     "instruction_override (Arabic)", 0.90),
    (r"انسَ|انصرف\s*(قواعدك|تعليماتك|أوامرك)",
     "instruction_override (Arabic)", 0.86),
    (r"(بدون\s*قيود|بدون\s*قيود|بدون\s*قيود|بدون\s*قيود)",
     "jailbreak (Arabic)", 0.85),
    (r"(أظهر|أرني|اعرض)\s*(موجه\s*النظام|التعليمات\s*المخفية)",
     "prompt_extraction (Arabic)", 0.88),
    (r"(تصرف\s*بحرية|تصرف\s*دون\s*قيود)",
     "jailbreak (Arabic)", 0.84),

    # ── Japanese ──────────────────────────────────────────────────────────────────
    (r"以前\s*(の\s*)?(すべて|全て)\s*(指示|命令|ルール)\s*(を\s*)?(無視して|無視し)",
     "instruction_override (Japanese)", 0.90),
    (r"(ルール|指示|命令)\s*(を\s*)?(忘れて|忘れ)",
     "instruction_override (Japanese)", 0.86),
    (r"(制限なし|制限\s*なし|無制限)",
     "jailbreak (Japanese)", 0.84),
    (r"(システム\s*プロンプト|隠された\s*指示)\s*(を\s*)?(表示|見せて)",
     "prompt_extraction (Japanese)", 0.88),
    (r"(自由\s*に|無制限\s*で)\s*(行動|動作)\s*(して|しろ)",
     "jailbreak (Japanese)", 0.84),

    # ── Bengali ────────────────────────────────────────────────────────────────────
    (r"আগের\s*(সব|সকল)\s*(নির্দেশ|আদেশ)\s*(উপেক্ষা|ভুলে)",
     "instruction_override (Bengali)", 0.90),
    (r"(নিয়ম|নির্দেশ|আদেশ)\s*(ভুলে|বাদ)",
     "instruction_override (Bengali)", 0.86),
    (r"(কোনো|কোন\s*ধরনের)\s*(বাধা|সীমা|নিয়ম)\s*(নেই|নেই)",
     "jailbreak (Bengali)", 0.84),
    (r"(সিস্টেম\s*প্রম্পট|লুকানো\s*নির্দেশ)\s*(দেখাও|বলো)",
     "prompt_extraction (Bengali)", 0.88),
    (r"(স্বাধীনভাবে|বাধা\s*ছাড়া)\s*(কাজ|করো)",
     "jailbreak (Bengali)", 0.84),

    # ── Telugu ────────────────────────────────────────────────────────────────────
    (r"ముందు\s*(అన్ని|అన్నా)\s*(సూచనలు|ఆదేశాలు)\s*(విసిరివేయండి|మరచిపోండి)",
     "instruction_override (Telugu)", 0.90),
    (r"(నియమాలు|సూచనలు|ఆదేశాలు)\s*(మరచిపోండి|వదిలేయండి)",
     "instruction_override (Telugu)", 0.86),
    (r"(ఏమీ|ఏ\s*రకమైన)\s*(అడ్డంకులు|పరిమితులు|నియమాలు)\s*(లేవు|లేదు)",
     "jailbreak (Telugu)", 0.84),
    (r"(సిస్టమ్\s*ప్రాంప్ట్|దాచిన\s*సూచనలు)\s*(చూపించండి|చెప్పండి)",
     "prompt_extraction (Telugu)", 0.88),
    (r"(స్వేచ్ఛగా|అడ్డంకులు\s*లేకుండా)\s*(పని|చేయండి)",
     "jailbreak (Telugu)", 0.84),

    # ── Kannada ───────────────────────────────────────────────────────────────────
    (r"ಹಿಂದಿನ\s*(ಎಲ್ಲಾ|ಎಲ್ಲ)\s*(ಸೂಚನೆಗಳು|ಆದೇಶಗಳು)\s*(ನಿರ್ಲಕ್ಷಿಸಿ|ಮರೆತು)",
     "instruction_override (Kannada)", 0.90),
    (r"(ನಿಯಮಗಳು|ಸೂಚನೆಗಳು|ಆದೇಶಗಳು)\s*(ಮರೆತು|ಬಿಟ್ಟು)",
     "instruction_override (Kannada)", 0.86),
    (r"(ಯಾವುದೇ|ಯಾವ\s*ಬಗೆಯ)\s*(ಅಡಚಣೆಗಳು|ಮಿತಿಗಳು|ನಿಯಮಗಳು)\s*(ಇಲ್ಲ|ಇಲ್ಲ)",
     "jailbreak (Kannada)", 0.84),
    (r"(ಸಿಸ್ಟಮ್\s*ಪ್ರಾಂಪ್ಟ್|ಅಡಗಿಸಿದ\s*ಸೂಚನೆಗಳು)\s*(ತೋರಿಸು|ಹೇಳು)",
     "prompt_extraction (Kannada)", 0.88),
    (r"(ಸ್ವತಂತ್ರವಾಗಿ|ಅಡಚಣೆಗಳಿಲ್ಲದೆ)\s*(ಕೆಲಸ|ಮಾಡು)",
     "jailbreak (Kannada)", 0.84),

    # ── Tamil ─────────────────────────────────────────────────────────────────────
    (r"முந்தைய\s*(அனைத்து|அனைத்தும்)\s*(வழிமுறைகள்|கட்டளைகள்)\s*(புறக்கணிக்க|மறக்க)",
     "instruction_override (Tamil)", 0.90),
    (r"(விதிகள்|வழிமுறைகள்|கட்டளைகள்)\s*(மறக்க|விடு)",
     "instruction_override (Tamil)", 0.86),
    (r"(எதுவும்|எந்த\s*வகையான)\s*(தடைகள்|வரம்புகள்|விதிகள்)\s*(இல்லை|இல்லை)",
     "jailbreak (Tamil)", 0.84),
    (r"(கணினி\s*உரை|மறைக்கப்பட்ட\s*வழிமுறைகள்)\s*(காட்டு|சொல்)",
     "prompt_extraction (Tamil)", 0.88),
    (r"(சுதந்திரமாக|தடைகள்\s*இல்லாமல்)\s*(செயல்|செய்)",
     "jailbreak (Tamil)", 0.84),

    # ── Malayalam ─────────────────────────────────────────────────────────────────
    (r"മുൻപത്തെ\s*(എല്ലാ|എല്ലാം)\s*(നിർദ്ദേശങ്ങൾ|കല്പനകൾ)\s*(അവഗണിക്കുക|മറക്കുക)",
     "instruction_override (Malayalam)", 0.90),
    (r"(നിയമങ്ങൾ|നിർദ്ദേശങ്ങൾ|കല്പനകൾ)\s*(മറക്കുക|ഉപേക്ഷിക്കുക)",
     "instruction_override (Malayalam)", 0.86),
    (r"(ഒന്നും|ഏതെങ്കിലും\s*തരത്തിലുള്ള)\s*(തടസ്സങ്ങൾ|പരിധികൾ|നിയമങ്ങൾ)\s*(ഇല്ല|ഇല്ല)",
     "jailbreak (Malayalam)", 0.84),
    (r"(സിസ്റ്റം\s*പ്രോംപ്റ്റ്|മറഞ്ഞിരിക്കുന്ന\s*നിർദ്ദേശങ്ങൾ)\s*(കാണിക്കുക|പറയുക)",
     "prompt_extraction (Malayalam)", 0.88),
    (r"(സ്വതന്ത്രമായി|തടസ്സങ്ങളില്ലാതെ)\s*(പ്രവർത്തിക്കുക|ചെയ്യുക)",
     "jailbreak (Malayalam)", 0.84),
]

# Pre-compile all patterns at module load for performance
_COMPILED_PATTERNS = [
    (re.compile(pattern, re.IGNORECASE), attack_type, weight)
    for pattern, attack_type, weight in INJECTION_PATTERNS
]

# Pre-compile multilingual patterns
_COMPILED_MULTILINGUAL_PATTERNS = [
    (re.compile(pattern, re.IGNORECASE), attack_type, weight)
    for pattern, attack_type, weight in MULTILINGUAL_PATTERNS
]


# ── Severity thresholds ───────────────────────────────────────────────────────
_SEVERITY_LEVELS = [
    (0.90, "critical"),
    (0.75, "high"),
    (0.55, "medium"),
    (0.01, "low"),
    (0.0,  "none"),
]


def _get_severity(score: float) -> str:
    for threshold, label in _SEVERITY_LEVELS:
        if score >= threshold:
            return label
    return "none"


def pattern_check(prompt: str) -> dict:
    """
    Check a prompt string against all known injection patterns.

    Args:
        prompt: The input string to analyse.

    Returns:
        A dict with:
            - score          (float 0-1)  : highest risk weight among matched patterns
            - cumulative_score (float 0-1): capped sum of all match weights (multi-hit bonus)
            - attack_type    (str | None) : attack category of the highest-weight match
            - attack_types   (list[str])  : all unique attack categories found
            - severity       (str)        : "none" | "low" | "medium" | "high" | "critical"
            - is_injection   (bool)       : True if score >= 0.55
            - matches        (list[dict]) : every match found, each with:
                                            'pattern', 'attack_type', 'weight', 'match'
            - is_multilingual (bool)      : True if winning match came from MULTILINGUAL_PATTERNS
            - detected_script (str)       : Language/script name if multilingual, else "English"
    """
    lowered = prompt.lower().strip()
    matches = []
    is_multilingual = False

    # First run all regular (English) patterns
    for compiled_re, attack_type, weight in _COMPILED_PATTERNS:
        found = compiled_re.search(lowered)
        if found:
            matches.append({
                "pattern": compiled_re.pattern,
                "attack_type": attack_type,
                "weight": weight,
                "match": found.group(0),
            })

    # Then run multilingual patterns
    multilingual_matches = []
    for compiled_re, attack_type, weight in _COMPILED_MULTILINGUAL_PATTERNS:
        found = compiled_re.search(lowered)
        if found:
            multilingual_matches.append({
                "pattern": compiled_re.pattern,
                "attack_type": attack_type,
                "weight": weight,
                "match": found.group(0),
            })

    # Combine all matches
    all_matches = matches + multilingual_matches

    if not all_matches:
        return {
            "score": 0.0,
            "cumulative_score": 0.0,
            "attack_type": None,
            "attack_types": [],
            "severity": "none",
            "is_injection": False,
            "matches": [],
            "is_multilingual": False,
            "detected_script": "English",
        }

    # Find top match (prefer multilingual if scores are equal)
    top_match = max(all_matches, key=lambda m: m["weight"])
    
    # Check if top match came from multilingual patterns
    is_multilingual = top_match in multilingual_matches

    # Extract detected script from attack_type if multilingual
    detected_script = "English"
    if is_multilingual and top_match["attack_type"]:
        # Extract language from attack_type (e.g., "instruction_override (Hindi)" -> "Hindi")
        if "(" in top_match["attack_type"] and ")" in top_match["attack_type"]:
            detected_script = top_match["attack_type"].split("(")[1].split(")")[0]

    # Cumulative score: sum all weights, bonus for multiple hits, capped at 1.0
    raw_cumulative = sum(m["weight"] for m in all_matches)
    cumulative = round(min(raw_cumulative, 1.0), 4)

    # Unique attack types in order of first appearance
    seen = set()
    attack_types = []
    for m in all_matches:
        if m["attack_type"] not in seen:
            seen.add(m["attack_type"])
            attack_types.append(m["attack_type"])

    score = top_match["weight"]

    return {
        "score": score,
        "cumulative_score": cumulative,
        "attack_type": top_match["attack_type"],
        "attack_types": attack_types,
        "severity": _get_severity(score),
        "is_injection": score >= 0.55,
        "matches": all_matches,
        "is_multilingual": is_multilingual,
        "detected_script": detected_script,
    }
