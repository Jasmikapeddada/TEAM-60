def generate_content(context, intent, llm):
    prompt = f"""
    Generate {intent['tasks']} using ONLY the syllabus below.
    Do NOT introduce new topics.

    Syllabus:
    {context}

    Constraints:
    {intent}
    """
    return llm.invoke(prompt)