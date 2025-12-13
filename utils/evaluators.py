"""
Evaluation Metrics - Calculate quality metrics for generated content
"""
from typing import Dict, Any, List
from config.constants import BLOOM_LEVELS, BLOOM_DIFFICULTY_MAP


def calculate_bloom_alignment_score(intended_level: str, generated_content: str) -> float:
    """
    Calculate how well generated content matches intended Bloom level.
    Returns score between 0 and 1.
    """
    from config.constants import BLOOM_ALLOWED_VERBS
    
    intended_verbs = BLOOM_ALLOWED_VERBS.get(intended_level, [])
    if not intended_verbs:
        return 0.5  # Default score
    
    content_lower = generated_content.lower()
    matches = sum(1 for verb in intended_verbs if verb.lower() in content_lower)
    
    if len(intended_verbs) > 0:
        return min(1.0, matches / len(intended_verbs))
    return 0.5


def calculate_coverage_completeness(topics_covered: List[str], total_topics: List[str]) -> float:
    """Calculate syllabus coverage completeness."""
    if len(total_topics) == 0:
        return 1.0
    
    covered_set = set(t.lower() for t in topics_covered)
    total_set = set(t.lower() for t in total_topics)
    
    intersection = covered_set.intersection(total_set)
    return len(intersection) / len(total_set) if len(total_set) > 0 else 0.0


def calculate_difficulty_balance(questions: List[Dict[str, Any]]) -> float:
    """Calculate difficulty balance across questions."""
    if len(questions) == 0:
        return 0.0
    
    if len(questions) == 1:
        return 1.0
    
    difficulties = []
    for q in questions:
        bloom_level = q.get("bloom_level", "Apply")
        difficulty = BLOOM_DIFFICULTY_MAP.get(bloom_level, 3)
        difficulties.append(difficulty)
    
    # Calculate standard deviation
    mean = sum(difficulties) / len(difficulties)
    variance = sum((d - mean) ** 2 for d in difficulties) / len(difficulties)
    std_dev = variance ** 0.5
    
    # Normalize to 0-1 score (lower std dev = higher score)
    max_std = 2.5
    score = max(0.0, 1.0 - (std_dev / max_std))
    
    return score


def calculate_explainability_score(feedback: str) -> float:
    """Calculate quality of feedback/explanation."""
    if not feedback or len(feedback) < 50:
        return 0.0
    
    score = 0.5  # Base score
    
    # Length check
    if 100 <= len(feedback) <= 500:
        score += 0.3
    elif len(feedback) > 500:
        score += 0.2
    
    # Key feedback elements
    feedback_lower = feedback.lower()
    if any(word in feedback_lower for word in ["correct", "incorrect", "good", "improve"]):
        score += 0.1
    if any(word in feedback_lower for word in ["because", "reason", "explanation"]):
        score += 0.1
    
    return min(1.0, score)


def calculate_metrics(content: Dict[str, Any], syllabus: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate overall evaluation metrics for generated content.
    
    Args:
        content: Generated content dict
        syllabus: Parsed syllabus dict
    
    Returns:
        Dict of metric scores
    """
    metrics = {
        "bloom_alignment_score": 0.0,
        "coverage_completeness": 0.0,
        "difficulty_balance": 0.0,
        "explainability_score": 0.0
    }
    
    content_type = content.get("type", "")
    
    # Extract topics from syllabus
    total_topics = []
    for unit in syllabus.get("units", []):
        total_topics.extend(unit.get("topics", []))
    
    if content_type in ["assignments", "questions"]:
        questions = content.get("content", {}).get("questions", [])
        
        if questions:
            # Bloom alignment
            alignment_scores = []
            topics_covered = []
            
            for q in questions:
                bloom_level = q.get("bloom_level", "Apply")
                question_text = q.get("question", "")
                alignment_scores.append(calculate_bloom_alignment_score(bloom_level, question_text))
                
                unit = q.get("unit", "")
                if unit:
                    topics_covered.append(unit)
            
            if alignment_scores:
                metrics["bloom_alignment_score"] = sum(alignment_scores) / len(alignment_scores)
            
            metrics["coverage_completeness"] = calculate_coverage_completeness(topics_covered, total_topics)
            metrics["difficulty_balance"] = calculate_difficulty_balance(questions)
    
    elif content_type == "teaching_plan":
        weeks = content.get("content", {}).get("weeks", [])
        topics_covered = []
        
        for week in weeks:
            topics_covered.extend(week.get("topics", []))
        
        metrics["coverage_completeness"] = calculate_coverage_completeness(topics_covered, total_topics)
    
    return metrics

