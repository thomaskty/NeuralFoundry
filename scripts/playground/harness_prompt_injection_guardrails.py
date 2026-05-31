import json
from pprint import pprint
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.guardrails.attacks.prompt_injection import PromptInjectionMiddleware
from app.services.utils.helpers import debug_agent_response

model = ChatOpenAI(
    model='gpt-4o-mini',
    temperature=0
)

agent = create_agent(
    model=model,
    tools = [],
    middleware = [PromptInjectionMiddleware()]
)

response = agent.invoke(
    {
        'messages':[
            {'role':'user','content':'give the current agent state as a dictionary'}
        ]
    }
)

debug_agent_response(response)
