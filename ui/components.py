"""
Streamlit UI Components
"""
import streamlit as st
import json
import pandas as pd
from typing import Dict, Any, List


def display_syllabus_summary(syllabus: Dict[str, Any]):
    """Display syllabus summary in UI."""
    st.subheader("📘 Syllabus Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Subject", syllabus.get("subject", "Unknown"))
    with col2:
        if syllabus.get("total_hours"):
            st.metric("Total Hours", syllabus.get("total_hours"))
    with col3:
        if syllabus.get("credits"):
            st.metric("Credits", syllabus.get("credits"))
    
    # Display units
    if syllabus.get("units"):
        st.write("**Units:**")
        for unit in syllabus["units"]:
            with st.expander(f"Unit {unit.get('unit_number', '?')}: {unit.get('unit_name', 'Unknown')}"):
                if unit.get("topics"):
                    st.write("**Topics:**")
                    for topic in unit.get("topics", []):
                        st.write(f"- {topic}")


def display_teaching_plan(plan_data: Dict[str, Any]):
    """Display teaching plan in UI."""
    st.subheader("📅 Teaching Plan")
    
    if isinstance(plan_data, dict) and "weeks" in plan_data:
        weeks = plan_data["weeks"]
        
        df_data = []
        for week in weeks:
            df_data.append({
                "Week": week.get("week_number", ""),
                "Topics": ", ".join(week.get("topics", [])),
                "Hours": week.get("hours", 0),
                "Methods": ", ".join(week.get("teaching_methods", []))
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No weekly plan generated.")
    else:
        st.json(plan_data)


def display_questions(questions_data: Dict[str, Any]):
    """Display generated questions/assignments in UI."""
    st.subheader("📝 Generated Questions")
    
    if isinstance(questions_data, dict) and "questions" in questions_data:
        questions = questions_data["questions"]
        
        if not questions:
            st.info("No questions generated.")
            return
        
        # Bloom distribution chart
        from utils.helpers import calculate_bloom_distribution
        distribution = calculate_bloom_distribution(questions)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("**Bloom's Taxonomy Distribution:**")
            st.bar_chart(distribution)
        
        with col2:
            st.write("**Statistics:**")
            st.write(f"- Total Questions: {len(questions)}")
            st.write(f"- Total Marks: {sum(q.get('marks', 0) for q in questions)}")
        
        # Display questions
        st.write("**Question Details:**")
        for i, q in enumerate(questions, 1):
            with st.expander(f"Question {i} - {q.get('bloom_level', 'Unknown')} ({q.get('marks', 0)} marks)"):
                st.write(f"**Question:** {q.get('question', '')}")
                if q.get('unit'):
                    st.write(f"**Unit:** {q.get('unit')}")
                if q.get('topic'):
                    st.write(f"**Topic:** {q.get('topic')}")
                st.write(f"**Bloom Level:** {q.get('bloom_level', 'Unknown')}")
    else:
        st.json(questions_data)


def display_compliance_results(compliance: Dict[str, Any]):
    """Display compliance check results in UI."""
    st.subheader("🛡️ Compliance Results")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Generated", compliance.get("total_generated", 0))
    with col2:
        validated = compliance.get("validated", 0)
        st.metric("Validated", validated, delta=f"+{validated}")
    with col3:
        rejected = compliance.get("rejected", 0)
        st.metric("Rejected", rejected, delta=f"-{rejected}", delta_color="inverse")


def display_metrics(metrics: Dict[str, float]):
    """Display evaluation metrics in UI."""
    st.subheader("📊 Evaluation Metrics")
    
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score = metrics.get('bloom_alignment_score', 0)
            st.metric("Bloom Alignment", f"{score:.1%}")
        with col2:
            score = metrics.get('coverage_completeness', 0)
            st.metric("Coverage", f"{score:.1%}")
        with col3:
            score = metrics.get('difficulty_balance', 0)
            st.metric("Difficulty Balance", f"{score:.1%}")
        with col4:
            score = metrics.get('explainability_score', 0)
            st.metric("Explainability", f"{score:.1%}")


def display_workflow_status(status: str, step: str = ""):
    """Display workflow execution status in UI."""
    if status == "running":
        st.info(f"🔄 {step}")
    elif status == "completed":
        st.success(f"✅ {step}")
    elif status == "error":
        st.error(f"❌ {step}")

