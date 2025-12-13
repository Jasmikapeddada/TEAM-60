def parse_syllabus(context, llm):
    prompt = f"""
    From the syllabus content below,
    extract units and topics in JSON.

    Syllabus:
    {context}
    """
    return llm.invoke(prompt)