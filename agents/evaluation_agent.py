"""
Evaluation Agent - Evaluates student answers
"""
import json
import re
from typing import Dict, Any, List
from utils.llm_client import get_llm_client
from config.constants import RUBRICS, BLOOM_LEVELS


class EvaluationAgent:
    """Agent for evaluating student answers"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.rubrics = RUBRICS
    
    def evaluate_answer(
        self,
        question: str,
        student_answer: str,
        model_answer: str = None,
        bloom_level: str = "Apply",
        max_marks: int = 10
    ) -> Dict[str, Any]:
        """
        Evaluate student answer against question and rubric.
        
        Args:
            question: The question text
            student_answer: Student's answer
            model_answer: Model/reference answer (optional)
            bloom_level: Expected Bloom's taxonomy level
            max_marks: Maximum marks for the question
        
        Returns:
            Evaluation result with score and feedback
        """
        # Get rubric criteria
        criteria = self._get_rubric_criteria()
        
        # Evaluate with LLM
        evaluation = self._evaluate_with_llm(
            question, student_answer, model_answer, bloom_level, max_marks, criteria
        )
        
        return evaluation
    
    def _get_rubric_criteria(self) -> List[Dict]:
        """Get rubric criteria."""
        if self.rubrics and "answer_evaluation" in self.rubrics:
            return self.rubrics["answer_evaluation"].get("criteria", [])
        
        # Default rubric
        return [
            {"name": "Conceptual Accuracy", "weight": 0.4, "description": "Correctness of concepts"},
            {"name": "Clarity of Explanation", "weight": 0.2, "description": "Logical flow and clarity"},
            {"name": "Bloom Level Match", "weight": 0.2, "description": "Matches expected Bloom level"},
            {"name": "Examples/Application", "weight": 0.2, "description": "Use of examples or applications"}
        ]
    
    def _evaluate_with_llm(
        self,
        question: str,
        student_answer: str,
        model_answer: str,
        bloom_level: str,
        max_marks: int,
        criteria: List[Dict]
    ) -> Dict[str, Any]:
        """Evaluate answer using LLM."""
        # Format criteria
        criteria_text = "\n".join([
            f"- {c['name']}: {c['description']} (weight: {c['weight']})"
            for c in criteria
        ])
        
        model_answer_section = ""
        if model_answer:
            model_answer_section = f"\n\nModel Answer:\n{model_answer}"
        
        prompt = f"""
Evaluate the following student answer against the question and rubric.

Question:
{question}

Expected Bloom Level: {bloom_level}
Maximum Marks: {max_marks}

Student Answer:
{student_answer}
{model_answer_section}

Rubric Criteria:
{criteria_text}

Provide a detailed evaluation with:
1. Score (out of {max_marks})
2. Detailed feedback
3. Strengths
4. Areas for improvement
5. Missing concepts or points

Respond with JSON:
{{
    "score": number (0 to {max_marks}),
    "percentage": number (0 to 100),
    "feedback": "detailed feedback text",
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"],
    "missing_concepts": ["concept1", "concept2"],
    "criterion_scores": {{
        "Conceptual Accuracy": number,
        "Clarity of Explanation": number,
        "Bloom Level Match": number,
        "Examples/Application": number
    }}
}}
"""
        
        try:
            response = self.llm_client.chat_completion([
                {"role": "system", "content": "You are an expert academic evaluator. Evaluate answers fairly and provide constructive feedback. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ], temperature=0.2)
            
            # Parse JSON
            evaluation = self._parse_json_response(response)
            
            # Validate and normalize
            evaluation.setdefault("score", 0)
            evaluation.setdefault("percentage", 0)
            evaluation.setdefault("feedback", "")
            evaluation.setdefault("strengths", [])
            evaluation.setdefault("improvements", [])
            evaluation.setdefault("missing_concepts", [])
            
            # Ensure score is within bounds
            evaluation["score"] = min(max_marks, max(0, evaluation["score"]))
            evaluation["percentage"] = (evaluation["score"] / max_marks) * 100
            
            return evaluation
            
        except Exception as e:
            print(f"[Evaluation Agent] Error: {e}")
            return {
                "score": 0,
                "percentage": 0,
                "feedback": f"Error during evaluation: {str(e)}",
                "strengths": [],
                "improvements": [],
                "missing_concepts": [],
                "error": str(e)
            }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        try:
            return json.loads(response)
        except:
            return {}


def evaluation_agent(
    question: str,
    student_answer: str,
    model_answer: str = None,
    bloom_level: str = "Apply",
    max_marks: int = 10,
    llm_client=None
) -> Dict[str, Any]:
    """
    Convenience function for answer evaluation.
    
    Args:
        question: Question text
        student_answer: Student's answer
        model_answer: Optional model answer
        bloom_level: Expected Bloom level
        max_marks: Maximum marks
        llm_client: Optional LLM client
    
    Returns:
        Evaluation result dict
    """
    agent = EvaluationAgent(llm_client=llm_client)
    return agent.evaluate_answer(question, student_answer, model_answer, bloom_level, max_marks)

