import inspect
from enum import Enum
from typing import Annotated

import lilypad
from dotenv import load_dotenv
from mirascope.core import FromCallArgs, openai, prompt_template
from pydantic import BaseModel, Field

load_dotenv()
lilypad.configure()


class TicketCategory(str, Enum):
    BUG_REPORT = "Bug Report"
    FEATURE_REQUEST = "Feature Request"


class TicketPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class Ticket(BaseModel):
    issue: Annotated[str, FromCallArgs()]
    category: TicketCategory
    priority: TicketPriority
    summary: str = Field(
        ...,
        description="A highlight summary of the most important details of the ticket.",
    )


@lilypad.generation()
@openai.call(
    "gpt-4o-mini",
    response_model=Ticket,
)
@prompt_template(
    """
    SYSTEM:
    Your task is to triage an issue posted by a user.
    Successfully triaging a ticket involves:
    - Identifying the category of the ticket.
    - Assigning a priority to the ticket.
    - Summarizing the most important details of the ticket.
 
    USER: Please triage this issue: {issue}
    """
)
def triage_issue(issue: str): ...


issue = inspect.cleandoc("""
I tried using the new feature but it's not working as expected.
Can you help me figure out what's going wrong?
""")
ticket = triage_issue(issue)
print(ticket)
# > issue="I tried using the new feature but it's not working as expected.\nCan you help me figure out what's going wrong?"
#   category=<TicketCategory.BUG_REPORT: 'Bug Report'>
#   priority=<TicketPriority.MEDIUM: 'Medium'>
#   summary='User is experiencing issues with a new feature not functioning correctly.'


def request_assistance(question: str) -> str:
    """Requests assistance from an expert.

    Ensure `question` is as clear and concise as possible.
    This will help the expert provide a more accurate response.
    """
    return input(f"[NEED ASSISTANCE] {question}\n[ANSWER] ")


@lilypad.generation()
@openai.call(
    "gpt-4o-mini",
    tools=[request_assistance],
)
@prompt_template(
    """
    SYSTEM:
    You are a customer support agent.
    Successfully responding to a ticket involves:
    - Understanding the issue.
    - Ensuring you have all the necessary information, asking if necessary.
    - Providing a helpful response that addresses the issue.

    You final response will be sent verbatim to the user.

    If unable to answer, request assistance from an expert.
    You can do so by calling the `request_assistance` tool.
    This tool is extremely helpful when you are lacking information or knowledge.

    MESSAGES: {history}
    USER: {ticket}
    """
)
def customer_support_bot(
    issue: str, history: list[openai.OpenAIMessageParam]
) -> openai.OpenAIDynamicConfig:
    ticket = triage_issue(issue)
    return {"computed_fields": {"ticket": ticket}}


@lilypad.generation()
def handle_issue(issue: str) -> str:
    history = []
    response = customer_support_bot(issue, history)
    history += [response.user_message_param, response.message_param]
    while tools := response.tools:
        history += response.tool_message_params([(tool, tool.call()) for tool in tools])
        response = customer_support_bot("", history)
        history.append(response.message_param)
    return response.content


issue = inspect.cleandoc("""
I tried using the new feature but it's not working as expected.
Can you help me figure out what's going wrong?
""")
response = handle_issue(issue)
print(response)
