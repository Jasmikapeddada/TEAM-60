"""Agents package"""
# Import agents for convenience
from agents.intent_agent import IntentAgent, intent_agent
from agents.syllabus_agent import SyllabusAgent, syllabus_agent
from agents.lesson_planner_agent import LessonPlannerAgent, lesson_planner_agent
from agents.assessment_agent import AssessmentAgent, assessment_agent
from agents.evaluation_agent import EvaluationAgent, evaluation_agent
from agents.compliance_agent import ComplianceAgent, compliance_agent

__all__ = [
    'IntentAgent', 'intent_agent',
    'SyllabusAgent', 'syllabus_agent',
    'LessonPlannerAgent', 'lesson_planner_agent',
    'AssessmentAgent', 'assessment_agent',
    'EvaluationAgent', 'evaluation_agent',
    'ComplianceAgent', 'compliance_agent'
]

