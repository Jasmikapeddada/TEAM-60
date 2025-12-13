def run_workflow(user_input):
    intent = intent_agent(user_input)

    syllabus = syllabus_agent()

    results = []
    if "teaching_plan" in intent["tasks"]:
        results.append(content_agent())

    if "assignments" in intent["tasks"]:
        results.append(content_agent())

    compliance_agent(results)
    return results 