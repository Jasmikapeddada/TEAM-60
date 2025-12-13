# config/constants.py

# Bloom's Taxonomy Levels (ordered)
BLOOM_LEVELS = [
    "Remember",
    "Understand",
    "Apply",
    "Analyze",
    "Evaluate",
    "Create"
]

# Mapping Bloom levels to difficulty weight (for evals)
BLOOM_DIFFICULTY_MAP = {
    "Remember": 1,
    "Understand": 2,
    "Apply": 3,
    "Analyze": 4,
    "Evaluate": 5,
    "Create": 6
}

# Allowed academic verbs per Bloom level
BLOOM_ALLOWED_VERBS = {
    "Remember": ["define", "list", "recall", "identify", "state"],
    "Understand": ["explain", "describe", "summarize", "interpret"],
    "Apply": ["apply", "solve", "demonstrate", "use", "implement"],
    "Analyze": ["analyze", "compare", "differentiate", "examine"],
    "Evaluate": ["evaluate", "justify", "critique", "assess"],
    "Create": ["design", "develop", "formulate", "construct"]
}

# Exam type identifiers
EXAM_TYPES = ["mid", "end", "quiz", "assignment"]