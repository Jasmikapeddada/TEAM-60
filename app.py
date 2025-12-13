"""
Main Streamlit Application
AI Teaching Assistant for Faculty
"""
import streamlit as st
import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from orchestrator.workflow import run_workflow
from ui.components import (
    display_syllabus_summary,
    display_teaching_plan,
    display_questions,
    display_compliance_results,
    display_metrics,
    display_workflow_status
)
from utils.llm_client import get_llm_client, LLMClient
from config.settings import LLM_PROVIDER

# Page configuration
st.set_page_config(
    page_title="AI Teaching Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🎓 AI Teaching Assistant for Faculty")
st.markdown("### Agentic RAG-based Auto Planning & Auto Assessment System")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "llm_client" not in st.session_state:
    st.session_state.llm_client = None
if "workflow_results" not in st.session_state:
    st.session_state.workflow_results = None

# Initialize LLM client from environment
if "llm_client" not in st.session_state or st.session_state.llm_client is None:
    try:
        st.session_state.llm_client = get_llm_client()
    except Exception as e:
        st.session_state.llm_client = None

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Status
    if st.session_state.llm_client:
        st.success(f"✅ {LLM_PROVIDER.upper()} API ready (from environment)")
    else:
        st.error(f"❌ {LLM_PROVIDER.upper()} API key not found. Set {LLM_PROVIDER.upper()}_API_KEY environment variable.")
    
    st.divider()
    
    # Syllabus upload
    st.subheader("Syllabus Upload")
    syllabus_file = st.file_uploader(
        "Upload Syllabus (PDF or TXT)",
        type=["pdf", "txt"],
        help="Upload your syllabus file. Currently uses default sample if available."
    )
    
    syllabus_path = None
    if syllabus_file:
        # Save uploaded file
        upload_dir = "data/syllabus"
        os.makedirs(upload_dir, exist_ok=True)
        syllabus_path = os.path.join(upload_dir, syllabus_file.name)
        
        with open(syllabus_path, "wb") as f:
            f.write(syllabus_file.getbuffer())
        
        st.success(f"✅ Uploaded: {syllabus_file.name}")
    else:
        # Use default syllabus if available
        default_syllabus_txt = "data/syllabus/sample_syllabus.txt"
        default_syllabus_pdf = "data/syllabus/sample_syllabus.pdf"
        
        if os.path.exists(default_syllabus_txt):
            syllabus_path = default_syllabus_txt
            st.info(f"Using default: {os.path.basename(default_syllabus_txt)}")
        elif os.path.exists(default_syllabus_pdf):
            syllabus_path = default_syllabus_pdf
            st.info(f"Using default: {os.path.basename(default_syllabus_pdf)}")
    
    st.divider()
    
    # Quick actions
    st.subheader("Quick Actions")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.workflow_results = None
        st.rerun()

# Main content area - Chat Interface
st.header("💬 Chat Interface")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "results" in message:
            with st.expander("View Results"):
                st.json(message["results"])

# Chat input
if prompt := st.chat_input("Ask me to generate a teaching plan, create questions, or evaluate answers..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check if API is configured
    if st.session_state.llm_client is None:
        with st.chat_message("assistant"):
            st.error("❌ API key not configured. Please set GROQ_API_KEY environment variable.")
    else:
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🔄 Processing your request..."):
                try:
                    # Run workflow
                    results = run_workflow(
                        prompt,
                        syllabus_path=syllabus_path,
                        llm_client=st.session_state.llm_client
                    )
                    
                    st.session_state.workflow_results = results
                    
                    # Display response
                    if results.get("status") == "completed":
                        st.success("✅ Request processed successfully!")
                        
                        # Show summary
                        intent = results.get("intent", {})
                        tasks = intent.get("tasks", [])
                        if tasks:
                            st.write(f"**Detected tasks:** {', '.join(tasks)}")
                        
                        # Show generated content summary
                        generated = results.get("generated_content", [])
                        if generated:
                            st.write(f"**Generated:** {len(generated)} content item(s)")
                        
                        # Add assistant response to chat
                        response_text = f"Processed your request for: {', '.join(tasks)}"
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "results": results
                        })
                    else:
                        error = results.get("errors", ["Unknown error"])
                        st.error(f"❌ Error: {error[0] if error else 'Processing failed'}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Error: {error[0] if error else 'Processing failed'}"
                        })
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {str(e)}"
                    })

# Results Tab (if results exist)
if st.session_state.workflow_results:
    st.divider()
    st.header("📊 Detailed Results")
    
    results = st.session_state.workflow_results
    
    if results.get("status") == "completed":
        # Display syllabus summary
        if results.get("syllabus"):
            display_syllabus_summary(results["syllabus"])
            st.divider()
        
        # Display generated content - Show ALL generated content, not just validated
        all_generated = results.get("all_generated_content", [])
        
        # Fallback to validated content if all_generated not available
        if not all_generated:
            all_generated = results.get("generated_content", [])
        
        if all_generated:
            for content_item in all_generated:
                content_type = content_item.get("type", "unknown")
                
                if content_type == "teaching_plan":
                    display_teaching_plan(content_item.get("content", {}))
                elif content_type in ["assignments", "questions"]:
                    display_questions(content_item.get("content", {}))
                else:
                    with st.expander("View Raw Content"):
                        st.json(content_item)
                
                st.divider()
        else:
            st.warning("⚠️ No generated content to display. Check compliance results below.")
        
        # Display compliance results
        if results.get("compliance"):
            display_compliance_results(results["compliance"])
            
            # Show compliance details if there are issues
            if results.get("compliance", {}).get("rejected", 0) > 0:
                st.info("💡 Note: Some content may have been rejected by compliance checks, but is still shown above for review.")
            
            st.divider()
        
        # Display metrics
        if results.get("metrics"):
            display_metrics(results["metrics"])
            st.divider()
        
        # Download results
        st.subheader("📥 Download Results")
        try:
            results_json = json.dumps(results, indent=2, ensure_ascii=False, default=str)
            st.download_button(
                label="📄 Download Results as JSON",
                data=results_json,
                file_name=f"workflow_results_{results.get('timestamp', 'output').replace(':', '-')[:19]}.json",
                mime="application/json"
            )
        except Exception as e:
            st.error(f"Error preparing download: {str(e)}")
            st.json(results)  # Show raw JSON as fallback

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <p>AI Teaching Assistant - Built with Streamlit, Multi-Agent Architecture, and RAG</p>
    <p>Supports: Teaching Plans | Question Generation | Answer Evaluation</p>
    </div>
    """,
    unsafe_allow_html=True
)

