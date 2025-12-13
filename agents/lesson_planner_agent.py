"""
Lesson Planner Agent - Creates teaching schedules
"""
import json
import re
from typing import Dict, Any, List
from utils.llm_client import get_llm_client
from config.settings import ACADEMIC_WEEKS, HOURS_PER_WEEK


class LessonPlannerAgent:
    """Agent for creating lesson plans and teaching schedules"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
    
    def create_lesson_plan(self, syllabus: Dict[str, Any], weeks: int = None) -> Dict[str, Any]:
        """
        Create a lesson plan from syllabus.
        
        Args:
            syllabus: Parsed syllabus dict
            weeks: Number of academic weeks (defaults to configured value)
        
        Returns:
            Lesson plan dict with weekly schedule
        """
        weeks = weeks or ACADEMIC_WEEKS
        units = syllabus.get("units", [])
        
        if not units:
            return {"error": "No units found in syllabus", "weeks": []}
        
        # Get context from syllabus
        context = self._prepare_syllabus_context(syllabus)
        
        # Generate lesson plan
        lesson_plan = self._generate_with_llm(context, units, weeks)
        
        return lesson_plan
    
    def _prepare_syllabus_context(self, syllabus: Dict[str, Any]) -> str:
        """Prepare syllabus context for LLM."""
        parts = []
        
        parts.append(f"Subject: {syllabus.get('subject', 'Unknown')}")
        
        if syllabus.get("total_hours"):
            parts.append(f"Total Hours: {syllabus.get('total_hours')}")
        
        parts.append("\nUnits:")
        for unit in syllabus.get("units", []):
            unit_info = f"\nUnit {unit.get('unit_number', '?')}: {unit.get('unit_name', 'Unknown')}"
            if unit.get('hours'):
                unit_info += f" ({unit.get('hours')} hours)"
            
            if unit.get('topics'):
                unit_info += "\n  Topics: " + ", ".join(unit.get('topics', [])[:10])
            
            if unit.get('learning_outcomes'):
                unit_info += "\n  Learning Outcomes: " + ", ".join(unit.get('learning_outcomes', [])[:5])
            
            parts.append(unit_info)
        
        return "\n".join(parts)
    
    def _generate_with_llm(self, context: str, units: List[Dict], weeks: int) -> Dict[str, Any]:
        """Generate lesson plan using LLM."""
        prompt = f"""
Create a detailed {weeks}-week lesson plan (teaching schedule) using ONLY the syllabus below.
Do NOT introduce topics that are not in the syllabus.
Balance the workload evenly across weeks.

Syllabus:
{context}

Requirements:
1. Allocate all topics across {weeks} weeks
2. Balance workload (approximately {HOURS_PER_WEEK} hours per week)
3. Include learning objectives for each week
4. Suggest appropriate teaching methods (lecture, discussion, lab, etc.)
5. Ensure full syllabus coverage

Respond with JSON:
{{
    "subject": "subject name",
    "total_weeks": {weeks},
    "weeks": [
        {{
            "week_number": 1,
            "topics": ["topic1", "topic2"],
            "hours": 3,
            "learning_objectives": ["obj1", "obj2"],
            "teaching_methods": ["lecture", "discussion"],
            "unit": "Unit-1"
        }}
    ]
}}
"""
        
        try:
            response = self.llm_client.chat_completion([
                {"role": "system", "content": "You are an expert at creating academic lesson plans. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ], temperature=0.3)
            
            # Parse JSON
            plan = self._parse_json_response(response)
            
            # Validate
            if "weeks" not in plan:
                plan["weeks"] = []
            
            return plan
            
        except Exception as e:
            print(f"[Lesson Planner] Error: {e}")
            return {
                "subject": "Unknown",
                "total_weeks": weeks,
                "weeks": [],
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


def lesson_planner_agent(syllabus: Dict[str, Any], weeks: int = None, llm_client=None) -> Dict[str, Any]:
    """
    Convenience function for lesson planning.
    
    Args:
        syllabus: Parsed syllabus dict
        weeks: Number of weeks
        llm_client: Optional LLM client
    
    Returns:
        Lesson plan dict
    """
    agent = LessonPlannerAgent(llm_client=llm_client)
    return agent.create_lesson_plan(syllabus, weeks)


if __name__ == "__main__":
    # Test
    test_syllabus = {
        "subject": "Data Structures",
        "units": [
            {"unit_number": 1, "unit_name": "Introduction", "topics": ["Arrays", "Linked Lists"]}
        ]
    }
    plan = lesson_planner_agent(test_syllabus, weeks=16)
    print(json.dumps(plan, indent=2))

