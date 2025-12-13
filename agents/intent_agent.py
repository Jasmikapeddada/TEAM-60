def extract_intent(user_input, llm):
    prompt = f"""
    Extract intent from the faculty request.
    Return ONLY valid JSON.

    Faculty request:
    {user_input}

    Schema:
    {{
      "tasks": [],
      "units": [],
      "weeks": null,
      "exclude": []
    }}
    """
    return llm.invoke(prompt)