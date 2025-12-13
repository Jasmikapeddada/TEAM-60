"""
Syllabus Understanding Agent - Parses and structures syllabus content
"""
import json
import os
import re
from typing import Dict, Any, List
from rag.retriever import RAGRetriever
from utils.llm_client import get_llm_client
from config.settings import SYLLABUS_DIR


class SyllabusAgent:
    """Agent for parsing and understanding syllabus content"""
    
    def __init__(self, llm_client=None, retriever=None):
        self.llm_client = llm_client or get_llm_client()
        self.retriever = retriever or RAGRetriever()
    
    def parse_syllabus(self, syllabus_path: str = None) -> Dict[str, Any]:
        """
        Parse syllabus and extract structured information.
        
        Args:
            syllabus_path: Path to syllabus file (optional, uses default if None)
        
        Returns:
            Structured syllabus dict
        """
        # Get syllabus context via RAG
        context = self._get_syllabus_context()
        
        if not context:
            raise ValueError("Could not retrieve syllabus context. Build RAG index first.")
        
        # Parse with LLM
        parsed = self._parse_with_llm(context)
        
        # Add raw context for reference
        parsed["raw_context"] = context[:5000]  # Store first 5000 chars
        
        return parsed
    
    def _get_syllabus_context(self) -> str:
        """Retrieve syllabus context using RAG."""
        if not self.retriever.is_ready():
            return ""
        
        # Retrieve comprehensive context
        query = "syllabus units topics learning outcomes objectives"
        chunks = self.retriever.retrieve(query, top_k=10)
        
        if not chunks:
            return ""
        
        # Combine chunks
        context_parts = [chunk["text"] for chunk in chunks]
        return "\n\n".join(context_parts)
    
    def _parse_with_llm(self, context: str) -> Dict[str, Any]:
        """Parse syllabus using LLM."""
        prompt = f"""
Extract structured information from the following syllabus content.

Syllabus Content:
{context[:4000]}

Extract and return a JSON object with:
{{
    "subject": "subject name",
    "course_code": "course code if mentioned",
    "credits": number or null,
    "total_hours": number or null,
    "units": [
        {{
            "unit_number": 1,
            "unit_name": "unit name",
            "topics": ["topic1", "topic2", ...],
            "hours": number or null,
            "learning_outcomes": ["outcome1", "outcome2", ...]
        }}
    ]
}}

Be accurate and only extract information that is clearly present in the syllabus.
"""
        
        try:
            response = self.llm_client.chat_completion([
                {"role": "system", "content": "You are a syllabus parsing agent. Extract structured data from academic syllabi. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ], temperature=0.2)
            
            # Parse JSON
            parsed = self._parse_json_response(response)
            
            # Validate structure
            if "units" not in parsed:
                parsed["units"] = []
            
            return parsed
            
        except Exception as e:
            print(f"[Syllabus Agent] Error parsing: {e}")
            return {
                "subject": "Unknown",
                "course_code": None,
                "credits": None,
                "total_hours": None,
                "units": [],
                "error": str(e)
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


def syllabus_agent(syllabus_path: str = None, llm_client=None, retriever=None) -> Dict[str, Any]:
    """
    Convenience function for syllabus parsing.
    
    Args:
        syllabus_path: Optional path to syllabus file
        llm_client: Optional LLM client
        retriever: Optional RAG retriever
    
    Returns:
        Parsed syllabus dict
    """
    agent = SyllabusAgent(llm_client=llm_client, retriever=retriever)
    return agent.parse_syllabus(syllabus_path)


if __name__ == "__main__":
    # Test
    try:
        parsed = syllabus_agent()
        print(json.dumps(parsed, indent=2))
    except Exception as e:
        print(f"Error: {e}")

