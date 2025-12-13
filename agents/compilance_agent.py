def validate(content, syllabus):
    if not syllabus_topic_present(content, syllabus):
        return "FAIL"
    return "PASS"