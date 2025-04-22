def apply_chatml_format(messages):
    """
    ChatML 형식으로 메시지 리스트를 변환합니다.
    messages: List[Dict[str, str]] 형태로, 각 메시지는 {'role': ..., 'content': ...} 구조입니다.
    """
    chat_input = ""
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        chat_input += f"<|im_start|>{role}\n{content}\n<|im_end|>\n"
    return chat_input
