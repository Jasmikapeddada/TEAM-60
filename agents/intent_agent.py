"""
Intent Agent - Extracts user intent and preferences
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import json
import re
from typing import Dict, Any, List
from utils.llm_client import get_llm_client


class IntentAgent:
    """Agent for understanding user intent and extracting preferences"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
    
    def extract_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Extract intent from user input.
        
        Args:
            user_input: User's natural language request
        
        Returns:
            Dict with extracted intent and preferences
        """
        prompt = f"""
Analyze the following user request and extract the intent and preferences.

User Input: "{user_input}"

Extract:
1. Tasks: What does the user want? (teaching_plan, assignments, questions, evaluation)
2. Subject: Subject name if mentioned
3. Exam Type: mid/end/quiz/assignment if mentioned
4. Units: Specific units mentioned
5. Time period: Number of weeks or duration if mentioned

Respond with a JSON object:
{{
    "tasks": ["task1", "task2"],
    "subject": "subject name or null",
    "exam_type": "mid/end/quiz/assignment or null",
    "units": ["unit1", "unit2"] or [],
    "weeks": number or null,
    "intent_summary": "brief summary"
}}
"""
        
        try:
            response = self.llm_client.chat_completion([
                {"role": "system", "content": "You are an intent extraction agent for academic tasks. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ], temperature=0.2)
            
            # Extract JSON from response
            intent = self._parse_json_response(response)
            
            # Normalize tasks
            if isinstance(intent.get("tasks"), str):
                intent["tasks"] = [intent["tasks"]]
            elif "tasks" not in intent:
                intent["tasks"] = ["teaching_plan"]  # Default
            
            # Validate and set defaults
            intent.setdefault("subject", None)
            intent.setdefault("exam_type", None)
            intent.setdefault("units", [])
            intent.setdefault("weeks", None)
            
            return intent
            
        except Exception as e:
            print(f"[Intent Agent] Error: {e}")
            # Return default intent
            return {
                "tasks": ["teaching_plan"],
                "subject": None,
                "exam_type": None,
                "units": [],
                "weeks": None,
                "intent_summary": "Error extracting intent, using defaults"
            }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # Try to find JSON object directly
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        # Try parsing entire response
        try:
            return json.loads(response)
        except:
            return {}


def intent_agent(user_input: str, llm_client=None) -> Dict[str, Any]:
    """
    Convenience function for intent extraction.
    
    Args:
        user_input: User's request
        llm_client: Optional LLM client
    
    Returns:
        Extracted intent dict
    """
    agent = IntentAgent(llm_client=llm_client)
    return agent.extract_intent(user_input)


if __name__ == "__main__":
    # Test
    test_input = "Generate a 16-week teaching plan for Data Structures and Algorithms course"
    intent = intent_agent(test_input)
    print(json.dumps(intent, indent=2))

