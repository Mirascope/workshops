import os

import lilypad
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

os.environ["LILYPAD_PROJECT_ID"] = "a70e4888-db68-4df8-8498-42128a4ee479"
os.environ["LILYPAD_API_KEY"] = (
    "a4d85f040ae529e7b2a3368e2ab3c3e40a6e6e0e14058fc1b15190f0d882fb68"
)
lilypad.configure()

client = OpenAI()


def answer_question_prompt(question: str) -> list[ChatCompletionMessageParam]:
    return [
        {"role": "user", "content": f"Answer this question: {question}"},
    ]


@lilypad.generation()
def answer_question(question: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=answer_question_prompt(question),
    )
    return str(completion.choices[0].message.content)


response = answer_question("What is the capital of France?")
print(response)
# > The capital of France is Paris.
