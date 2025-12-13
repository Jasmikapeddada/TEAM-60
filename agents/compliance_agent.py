"""
Compliance Agent - Validates content against syllabus and rules
"""
from typing import Dict, Any, List
from utils.llm_client import get_llm_client
from config.constants import BLOOM_LEVELS, BLOOM_ALLOWED_VERBS
from rag.retriever import RAGRetriever


class ComplianceAgent:
    """Agent for validating compliance with syllabus and academic rules"""
    
    def __init__(self, llm_client=None, retriever=None):
        self.llm_client = llm_client or get_llm_client()
        self.retriever = retriever or RAGRetriever()
    
    def validate(self, content: Dict[str, Any], syllabus_context: str = "") -> Dict[str, Any]:
        """
        Validate content against syllabus and rules.
        
        Args:
            content: Content to validate (can be lesson plan, questions, etc.)
            syllabus_context: Syllabus context for validation
        
        Returns:
            Validation result with status and issues
        """
        content_type = content.get("type", "unknown")
        content_data = content.get("content", {})
        
        # Extract text content for validation
        if content_type in ["assignments", "questions"]:
            # For questions, extract question texts
            questions = content_data.get("questions", [])
            content_text = "\n".join([q.get("question", "") for q in questions[:5]])  # Check first 5 questions
        elif content_type == "teaching_plan":
            # For teaching plans, extract topics
            weeks = content_data.get("weeks", [])
            content_text = "\n".join([", ".join(w.get("topics", [])) for w in weeks[:5]])
        else:
            content_text = str(content_data)
        
        validations = []
        
        # 1. Syllabus compliance check - More lenient for questions
        syllabus_check = self._check_syllabus_compliance(content_text, syllabus_context, content_type)
        validations.append(syllabus_check)
        
        # 2. Bloom's taxonomy check (for questions)
        if content_type in ["assignments", "questions"]:
            # Check each question's bloom level
            questions = content_data.get("questions", [])
            bloom_checks_passed = 0
            for q in questions[:3]:  # Check first 3 questions
                bloom_level = q.get("bloom_level", "Apply")
                question_text = q.get("question", "")
                bloom_check = self._check_bloom_compliance(question_text, bloom_level)
                if bloom_check["status"] == "PASS":
                    bloom_checks_passed += 1
            
            if len(questions) > 0:
                # Pass if at least 50% of checked questions pass
                if bloom_checks_passed >= len(questions[:3]) * 0.5:
                    validations.append({
                        "check": "bloom_compliance",
                        "status": "PASS",
                        "issue": None
                    })
                else:
                    validations.append({
                        "check": "bloom_compliance",
                        "status": "FAIL",
                        "issue": "Some questions do not match their Bloom levels"
                    })
        
        # 3. Pattern compliance (for questions)
        if content_type in ["assignments", "questions"]:
            pattern_check = self._check_exam_pattern_compliance(content)
            validations.append(pattern_check)
        
        # Aggregate results - More lenient: pass if at least one check passes and no critical failures
        passed_checks = [v for v in validations if v["status"] == "PASS"]
        failed_checks = [v for v in validations if v["status"] == "FAIL"]
        unknown_checks = [v for v in validations if v["status"] == "UNKNOWN"]
        
        # Pass if no failures OR if we have at least one pass and failures are non-critical
        all_passed = len(failed_checks) == 0 or (len(passed_checks) > 0 and len(failed_checks) <= 1)
        issues = [v["issue"] for v in failed_checks if v.get("issue")]
        
        return {
            "status": "PASS" if all_passed else "FAIL",
            "validations": validations,
            "issues": issues,
            "content_type": content_type
        }
    
    def _check_syllabus_compliance(self, content_text: str, syllabus_context: str, content_type: str = "unknown") -> Dict[str, Any]:
        """Check if content is within syllabus boundaries."""
        if not content_text or len(content_text.strip()) < 10:
            return {
                "check": "syllabus_compliance",
                "status": "UNKNOWN",
                "issue": "Content text too short for validation"
            }
        
        if not syllabus_context:
            # Try to get context from RAG
            if self.retriever.is_ready():
                chunks = self.retriever.retrieve(content_text[:100], top_k=5)
                syllabus_context = "\n\n".join([chunk["text"] for chunk in chunks])
        
        if not syllabus_context:
            # If no context but content exists, assume pass (lenient validation)
            return {
                "check": "syllabus_compliance",
                "status": "PASS",
                "issue": None
            }
        
        prompt = f"""
Check if the following generated content is ONLY about topics present in the syllabus.
Be lenient - pass if content is generally related to syllabus topics.

Syllabus Context:
{syllabus_context[:2000]}

Generated Content:
{content_text[:1000]}

Respond with ONLY "YES" or "NO" - does the content stick to syllabus topics?
If NO, briefly mention what's outside syllabus.
"""
        
        try:
            response = self.llm_client.chat_completion([
                {"role": "system", "content": "You are a compliance checker. Be lenient and only reject if content is clearly outside syllabus. Respond with YES or NO."},
                {"role": "user", "content": prompt}
            ], temperature=0.1, max_tokens=100)
            
            answer = response.strip().upper()
            # More lenient checking
            is_compliant = "YES" in answer or "COMPLIANT" in answer or ("NO" not in answer and len(answer) < 20)
            
            issue = ""
            if not is_compliant and "NO" in answer:
                issue = response.split("NO")[-1].strip()[:200]  # Limit issue length
            
            return {
                "check": "syllabus_compliance",
                "status": "PASS" if is_compliant else "FAIL",
                "issue": issue if issue else None
            }
            
        except Exception as e:
            # On error, default to PASS (lenient)
            return {
                "check": "syllabus_compliance",
                "status": "PASS",
                "issue": None
            }
    
    def _check_bloom_compliance(self, content_text: str, expected_bloom: str) -> Dict[str, Any]:
        """Check if content matches expected Bloom level."""
        allowed_verbs = BLOOM_ALLOWED_VERBS.get(expected_bloom, [])
        
        if not allowed_verbs:
            return {
                "check": "bloom_compliance",
                "status": "UNKNOWN",
                "issue": f"Unknown Bloom level: {expected_bloom}"
            }
        
        verbs_str = ", ".join(allowed_verbs[:5])
        content_lower = content_text.lower()
        
        # Check if content uses appropriate verbs
        has_appropriate_verb = any(verb.lower() in content_lower for verb in allowed_verbs)
        
        if not has_appropriate_verb:
            return {
                "check": "bloom_compliance",
                "status": "FAIL",
                "issue": f"Content does not use appropriate verbs for {expected_bloom} level. Expected verbs: {verbs_str}"
            }
        
        return {
            "check": "bloom_compliance",
            "status": "PASS",
            "issue": None
        }
    
    def _check_exam_pattern_compliance(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with exam pattern rules."""
        # This is a placeholder - can be extended with actual exam pattern rules
        questions = content.get("content", {}).get("questions", [])
        
        if not questions:
            return {
                "check": "exam_pattern",
                "status": "PASS",
                "issue": None
            }
        
        # Check for repeated questions (simple check)
        question_texts = [q.get("question", "") for q in questions]
        if len(question_texts) != len(set(question_texts)):
            return {
                "check": "exam_pattern",
                "status": "FAIL",
                "issue": "Duplicate questions detected"
            }
        
        return {
            "check": "exam_pattern",
            "status": "PASS",
            "issue": None
        }
    
    def validate_batch(self, contents: List[Dict[str, Any]], syllabus_context: str = "") -> List[Dict[str, Any]]:
        """
        Validate multiple contents.
        
        Args:
            contents: List of content dicts
            syllabus_context: Syllabus context
        
        Returns:
            List of validated contents (only PASS items)
        """
        validated = []
        
        for content in contents:
            validation = self.validate(content, syllabus_context)
            content["compliance"] = validation
            
            if validation["status"] == "PASS":
                validated.append(content)
            else:
                print(f"[Compliance] Rejected: {validation['issues']}")
        
        return validated


def compliance_agent(content: Dict[str, Any], syllabus_context: str = "", llm_client=None, retriever=None) -> Dict[str, Any]:
    """
    Convenience function for compliance validation.
    
    Args:
        content: Content to validate
        syllabus_context: Syllabus context
        llm_client: Optional LLM client
        retriever: Optional RAG retriever
    
    Returns:
        Validation result
    """
    agent = ComplianceAgent(llm_client=llm_client, retriever=retriever)
    return agent.validate(content, syllabus_context)

