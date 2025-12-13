"""
Assessment Generator Agent - Creates questions and assignments
"""
import json
import re
from typing import Dict, Any, List
from utils.llm_client import get_llm_client
from config.constants import BLOOM_LEVELS, BLOOM_ALLOWED_VERBS
from rag.retriever import RAGRetriever


class AssessmentAgent:
    """Agent for generating questions and assignments"""
    
    def __init__(self, llm_client=None, retriever=None):
        self.llm_client = llm_client or get_llm_client()
        self.retriever = retriever or RAGRetriever()
    
    def generate_questions(
        self,
        syllabus: Dict[str, Any],
        exam_type: str = "mid",
        units: List[str] = None,
        bloom_distribution: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """
        Generate questions based on syllabus and exam pattern.
        
        Args:
            syllabus: Parsed syllabus dict
            exam_type: Type of exam (mid/end/quiz/assignment)
            units: List of unit names to focus on (None for all)
            bloom_distribution: Desired Bloom level distribution
        
        Returns:
            Generated questions dict
        """
        # Get syllabus context via RAG
        context = self._get_relevant_context(syllabus, units)
        
        # Set default Bloom distribution
        if bloom_distribution is None:
            bloom_distribution = self._get_default_bloom_distribution(exam_type)
        
        # Generate questions
        questions = self._generate_with_llm(context, syllabus, exam_type, bloom_distribution, units)
        
        return questions
    
    def _get_relevant_context(self, syllabus: Dict[str, Any], units: List[str] = None) -> str:
        """Get relevant syllabus context via RAG."""
        if not self.retriever.is_ready():
            return ""
        
        # Build query
        query_parts = []
        if units:
            query_parts.extend(units)
        else:
            # Get all units
            for unit in syllabus.get("units", []):
                query_parts.append(unit.get("unit_name", ""))
                query_parts.extend(unit.get("topics", [])[:3])
        
        query = " ".join(query_parts[:10])  # Limit query length
        
        # Retrieve context
        chunks = self.retriever.retrieve(query, top_k=8)
        context_parts = [chunk["text"] for chunk in chunks]
        
        return "\n\n".join(context_parts)
    
    def _get_default_bloom_distribution(self, exam_type: str) -> Dict[str, int]:
        """Get default Bloom distribution based on exam type."""
        if exam_type == "quiz":
            return {"Remember": 3, "Understand": 2, "Apply": 1}
        elif exam_type == "assignment":
            return {"Apply": 2, "Analyze": 2, "Evaluate": 1}
        elif exam_type == "end":
            return {
                "Remember": 2, "Understand": 2, "Apply": 3,
                "Analyze": 2, "Evaluate": 1, "Create": 0
            }
        else:  # mid
            return {
                "Remember": 2, "Understand": 3, "Apply": 3,
                "Analyze": 2, "Evaluate": 0, "Create": 0
            }
    
    def _generate_with_llm(
        self,
        context: str,
        syllabus: Dict[str, Any],
        exam_type: str,
        bloom_distribution: Dict[str, int],
        units: List[str]
    ) -> Dict[str, Any]:
        """Generate questions using LLM."""
        # Build Bloom requirements
        bloom_req = []
        total_questions = 0
        for level, count in bloom_distribution.items():
            if count > 0:
                verbs = ", ".join(BLOOM_ALLOWED_VERBS.get(level, [])[:3])
                bloom_req.append(f"- {level}: {count} questions (use verbs: {verbs})")
                total_questions += count
        
        bloom_requirements = "\n".join(bloom_req)
        
        # Build unit filter
        unit_filter = ""
        if units:
            unit_filter = f"Focus on units: {', '.join(units)}"
        else:
            unit_filter = "Cover all units from syllabus"
        
        prompt = f"""
Generate exam questions using ONLY the syllabus content below.
Follow Bloom's taxonomy distribution strictly.
Do NOT introduce topics outside the syllabus.

Syllabus Context:
{context[:3000]}

Exam Type: {exam_type}
{unit_filter}

Bloom's Taxonomy Distribution (Total: {total_questions} questions):
{bloom_requirements}

Requirements:
1. Each question must be from syllabus topics only
2. Match the specified Bloom level using appropriate verbs
3. Include marks allocation
4. Cover different topics/units (avoid repetition)
5. Balance difficulty appropriately

Respond with JSON:
{{
    "exam_type": "{exam_type}",
    "total_questions": {total_questions},
    "questions": [
        {{
            "question_number": 1,
            "question": "question text",
            "bloom_level": "Remember",
            "marks": 2,
            "unit": "Unit-1",
            "topic": "topic name"
        }}
    ]
}}
"""
        
        try:
            response = self.llm_client.chat_completion([
                {"role": "system", "content": "You are an expert at creating academic exam questions following Bloom's taxonomy. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ], temperature=0.4)
            
            # Parse JSON
            questions = self._parse_json_response(response)
            
            # Validate
            if "questions" not in questions:
                questions["questions"] = []
            
            return questions
            
        except Exception as e:
            print(f"[Assessment Agent] Error: {e}")
            return {
                "exam_type": exam_type,
                "total_questions": 0,
                "questions": [],
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


def assessment_agent(
    syllabus: Dict[str, Any],
    exam_type: str = "mid",
    units: List[str] = None,
    bloom_distribution: Dict[str, int] = None,
    llm_client=None,
    retriever=None
) -> Dict[str, Any]:
    """
    Convenience function for question generation.
    
    Args:
        syllabus: Parsed syllabus dict
        exam_type: Exam type
        units: Optional unit filter
        bloom_distribution: Optional Bloom distribution
        llm_client: Optional LLM client
        retriever: Optional RAG retriever
    
    Returns:
        Generated questions dict
    """
    agent = AssessmentAgent(llm_client=llm_client, retriever=retriever)
    return agent.generate_questions(syllabus, exam_type, units, bloom_distribution)

