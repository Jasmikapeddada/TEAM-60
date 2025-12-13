"""
Constants - Academic rules and taxonomy
"""
import json
import os
from config.settings import BLOOM_TAXONOMY_PATH, EXAM_PATTERN_PATH, RUBRICS_PATH

# Bloom's Taxonomy Levels (ordered from lower to higher order thinking)
BLOOM_LEVELS = [
    "Remember",
    "Understand",
    "Apply",
    "Analyze",
    "Evaluate",
    "Create"
]

# Mapping Bloom levels to difficulty weight (for evaluation)
BLOOM_DIFFICULTY_MAP = {
    "Remember": 1,
    "Understand": 2,
    "Apply": 3,
    "Analyze": 4,
    "Evaluate": 5,
    "Create": 6
}

# Load Bloom's taxonomy from JSON file
try:
    if os.path.exists(BLOOM_TAXONOMY_PATH):
        with open(BLOOM_TAXONOMY_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:  # Check if file is not empty
                bloom_data = json.loads(content)
                BLOOM_ALLOWED_VERBS = {level: bloom_data.get(level, {}).get("verbs", []) for level in BLOOM_LEVELS}
            else:
                raise ValueError("File is empty")
    else:
        raise FileNotFoundError("File not found")
except (FileNotFoundError, json.JSONDecodeError, ValueError):
    # Fallback if file doesn't exist or is invalid
    BLOOM_ALLOWED_VERBS = {
        "Remember": ["define", "list", "recall", "identify", "state"],
        "Understand": ["explain", "describe", "summarize", "interpret"],
        "Apply": ["apply", "solve", "demonstrate", "use", "implement"],
        "Analyze": ["analyze", "compare", "differentiate", "examine"],
        "Evaluate": ["evaluate", "justify", "critique", "assess"],
        "Create": ["design", "develop", "formulate", "construct"]
    }

# Exam types
EXAM_TYPES = ["mid", "end", "quiz", "assignment"]

# Load exam pattern if available
try:
    if os.path.exists(EXAM_PATTERN_PATH):
        with open(EXAM_PATTERN_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:  # Check if file is not empty
                EXAM_PATTERN = json.loads(content)
            else:
                EXAM_PATTERN = None
    else:
        EXAM_PATTERN = None
except (FileNotFoundError, json.JSONDecodeError, ValueError):
    EXAM_PATTERN = None

# Load rubrics if available
try:
    if os.path.exists(RUBRICS_PATH):
        with open(RUBRICS_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:  # Check if file is not empty
                RUBRICS = json.loads(content)
            else:
                RUBRICS = None
    else:
        RUBRICS = None
except (FileNotFoundError, json.JSONDecodeError, ValueError):
    RUBRICS = None

