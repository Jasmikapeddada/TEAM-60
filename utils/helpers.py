"""
Helper Utility Functions
"""
import json
import os
from typing import Dict, Any, List


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return {}


def save_json_file(data: Dict[str, Any], file_path: str) -> None:
    """Save data to JSON file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}")


def ensure_dir(directory: str) -> None:
    """Ensure directory exists."""
    os.makedirs(directory, exist_ok=True)


def format_syllabus_for_display(syllabus: Dict[str, Any]) -> str:
    """Format syllabus data for display."""
    lines = []
    lines.append(f"Subject: {syllabus.get('subject', 'Unknown')}")
    
    if syllabus.get('course_code'):
        lines.append(f"Course Code: {syllabus.get('course_code')}")
    if syllabus.get('credits'):
        lines.append(f"Credits: {syllabus.get('credits')}")
    if syllabus.get('total_hours'):
        lines.append(f"Total Hours: {syllabus.get('total_hours')}")
    
    lines.append("\nUnits:")
    for unit in syllabus.get("units", []):
        unit_num = unit.get('unit_number', '?')
        unit_name = unit.get('unit_name', 'Unknown')
        lines.append(f"\nUnit {unit_num}: {unit_name}")
        
        if unit.get('topics'):
            for topic in unit.get("topics", []):
                lines.append(f"  - {topic}")
    
    return "\n".join(lines)


def calculate_bloom_distribution(questions: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate Bloom's taxonomy distribution from questions."""
    distribution = {level: 0 for level in ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]}
    
    for q in questions:
        bloom_level = q.get("bloom_level", "").capitalize()
        if bloom_level in distribution:
            distribution[bloom_level] += 1
    
    return distribution

