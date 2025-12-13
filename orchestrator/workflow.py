"""
Orchestrator - Main workflow controller
Coordinates all agents and manages execution flow
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import json
import os
from typing import Dict, Any, List
from datetime import datetime

from agents.intent_agent import IntentAgent
from agents.syllabus_agent import SyllabusAgent
from agents.lesson_planner_agent import LessonPlannerAgent
from agents.assessment_agent import AssessmentAgent
from agents.evaluation_agent import EvaluationAgent
from agents.compliance_agent import ComplianceAgent
from utils.llm_client import get_llm_client
from rag.retriever import RAGRetriever
from config.settings import OUTPUTS_DIR


class Orchestrator:
    """Main orchestrator for multi-agent workflow"""
    
    def __init__(self, llm_client=None, retriever=None):
        """
        Initialize orchestrator with agents.
        
        Args:
            llm_client: LLM client instance
            retriever: RAG retriever instance
        """
        self.llm_client = llm_client or get_llm_client()
        self.retriever = retriever or RAGRetriever()
        
        # Initialize agents
        self.intent_agent = IntentAgent(self.llm_client)
        self.syllabus_agent = SyllabusAgent(self.llm_client, self.retriever)
        self.lesson_planner_agent = LessonPlannerAgent(self.llm_client)
        self.assessment_agent = AssessmentAgent(self.llm_client, self.retriever)
        self.evaluation_agent = EvaluationAgent(self.llm_client)
        self.compliance_agent = ComplianceAgent(self.llm_client, self.retriever)
    
    def execute_workflow(self, user_input: str, syllabus_path: str = None) -> Dict[str, Any]:
        """
        Execute complete workflow from user input to final results.
        
        Args:
            user_input: User's request/query
            syllabus_path: Optional path to syllabus file
        
        Returns:
            Complete workflow results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "intent": {},
            "syllabus": {},
            "generated_content": [],
            "compliance": {},
            "metrics": {},
            "status": "in_progress",
            "errors": []
        }
        
        try:
            # Step 1: Extract Intent
            print("[Orchestrator] Step 1: Extracting intent...")
            intent = self.intent_agent.extract_intent(user_input)
            results["intent"] = intent
            print(f"[Orchestrator] Intent: {intent.get('tasks', [])}")
            
            # Step 2: Parse Syllabus
            print("[Orchestrator] Step 2: Parsing syllabus...")
            syllabus = self.syllabus_agent.parse_syllabus(syllabus_path)
            results["syllabus"] = syllabus
            syllabus_context = syllabus.get("raw_context", "")
            print(f"[Orchestrator] Syllabus parsed: {len(syllabus.get('units', []))} units")
            
            # Step 3: Generate Content based on Intent
            print("[Orchestrator] Step 3: Generating content...")
            tasks = intent.get("tasks", [])
            if not tasks:
                tasks = ["teaching_plan"]  # Default
            
            generated_results = []
            
            for task in tasks:
                print(f"[Orchestrator] Processing task: {task}")
                
                if task in ["teaching_plan", "lesson_plan"]:
                    # Generate lesson plan
                    weeks = intent.get("weeks") or 16
                    lesson_plan = self.lesson_planner_agent.create_lesson_plan(syllabus, weeks)
                    generated_results.append({
                        "type": "teaching_plan",
                        "content": lesson_plan,
                        "bloom_level": "Apply"
                    })
                
                elif task in ["assignments", "questions", "question_paper"]:
                    # Generate questions
                    exam_type = intent.get("exam_type") or "mid"
                    units = intent.get("units") or None
                    questions = self.assessment_agent.generate_questions(syllabus, exam_type, units)
                    generated_results.append({
                        "type": "questions",
                        "content": questions,
                        "bloom_level": "Apply"
                    })
            
            results["generated_content"] = generated_results
            
            # Step 4: Compliance Checking
            print("[Orchestrator] Step 4: Running compliance checks...")
            validated_results = self.compliance_agent.validate_batch(
                generated_results,
                syllabus_context
            )
            
            results["compliance"] = {
                "total_generated": len(generated_results),
                "validated": len(validated_results),
                "rejected": len(generated_results) - len(validated_results)
            }
            
            # Keep validated results, but also store all generated for display
            results["generated_content"] = validated_results if validated_results else generated_results
            results["all_generated_content"] = generated_results  # Keep original for reference
            
            # Step 5: Calculate Metrics (if evaluators available)
            print("[Orchestrator] Step 5: Calculating metrics...")
            try:
                from utils.evaluators import calculate_metrics
                if validated_results:
                    metrics = calculate_metrics(validated_results[0], syllabus)
                    results["metrics"] = metrics
            except Exception as e:
                print(f"[Orchestrator] Metrics calculation skipped: {e}")
            
            # Step 6: Save Results
            print("[Orchestrator] Step 6: Saving results...")
            self._save_results(results)
            
            results["status"] = "completed"
            print("[Orchestrator] Workflow completed successfully!")
            
        except Exception as e:
            print(f"[Orchestrator] Error in workflow: {e}")
            results["status"] = "error"
            results["errors"].append(str(e))
            import traceback
            results["traceback"] = traceback.format_exc()
        
        return results
    
    def _save_results(self, results: Dict[str, Any]):
        """Save workflow results to file."""
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        
        # Append to logs
        log_path = os.path.join(OUTPUTS_DIR, "logs.json")
        
        try:
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(results)
            
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Orchestrator] Warning: Could not save logs: {e}")


def run_workflow(user_input: str, syllabus_path: str = None, llm_client=None, retriever=None) -> Dict[str, Any]:
    """
    Convenience function to run workflow.
    
    Args:
        user_input: User's request
        syllabus_path: Optional syllabus file path
        llm_client: Optional LLM client
        retriever: Optional RAG retriever
    
    Returns:
        Workflow results
    """
    orchestrator = Orchestrator(llm_client=llm_client, retriever=retriever)
    return orchestrator.execute_workflow(user_input, syllabus_path)


if __name__ == "__main__":
    # Test workflow
    test_input = "Generate a 16-week teaching plan for Data Structures course"
    try:
        results = run_workflow(test_input)
        print(f"\nWorkflow Status: {results['status']}")
        print(f"Generated Content Types: {[c['type'] for c in results.get('generated_content', [])]}")
    except Exception as e:
        print(f"Error: {e}")

