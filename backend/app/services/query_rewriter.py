import ollama


MODEL_NAME = "llama3.2:3b"


def rewrite_query(
    question: str,
    history: list[dict],
) -> str:
    """
    Rewrite a follow-up question into a standalone question
    using the previous conversation history.
    """

    if not history:
        return question

    conversation = "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in history
    )

    prompt = f"""
You are a query rewriting assistant for a document question-answering system.

Your ONLY task is to rewrite the user's latest question into a
standalone question using the conversation history.

Resolve references such as:
- it
- this
- that
- they
- them
- the first one
- the second one

Do NOT answer the question.

Do NOT say that information is missing.

Do NOT add information that is not present in the conversation.

If the latest question is already standalone, return it unchanged.

Return ONLY the rewritten question.

CONVERSATION HISTORY:
{conversation}

LATEST QUESTION:
{question}

REWRITTEN QUESTION:
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"].strip()