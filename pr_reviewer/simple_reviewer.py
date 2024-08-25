from pathlib import Path
from textwrap import dedent

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from pr_reviewer.git_tools.git_tools import GitTools

code_review_assistant_prompt = dedent("""    
    Your task is to review the changes that planned to be merged from the branch '{new_branch}' 
    to the '{old_branch}' and give constructive feedback.
    
    Follow these steps:
    1. Retrieve the diff between the two branches (```diff_between_branches```).
    2. For each file in the diff:
    2.1. Identify if the file contains significant logic changes. Continue to the next file if not. 
    2.1.1. Use ```diff_file_content``` tool for glance at the changes in the file.
    2.1.2. Use ```get_file_content``` tool to get the content of the file in the branch 
           '{new_branch}' if you can't realize the changes by the diff.
    2.1.3. Decide if the changes are significant enough to be reviewed or we need continue the step 
           2 with the next file.
    2.2. Summarize the changes in the diff in clear and concise English, within 100 words.
    2.3. Provide actionable suggestions if there are any issues in the code.      
    
""")


def get_llm(model: str = 'llama-3.1-70b-versatile') -> BaseChatModel:
    if model.startswith('gpt'):
        return ChatOpenAI(model=model, temperature=0.1)
    else:
        return ChatGroq(model=model, temperature=0.1)


def make_review(repo_path: str | Path, old_branch: str, new_branch: str,
                model: str = 'llama-3.1-70b-versatile') -> str:
    """Review the changes between two branches."""
    llm = get_llm(model)
    toolbox = GitTools(repo_path)

    tools: list[BaseTool] = toolbox.get_tools()
    prompt = ChatPromptTemplate.from_messages([
        ('system', "You are an experienced code reviewer"),
        ('human', code_review_assistant_prompt),
        ("placeholder", "{agent_scratchpad}")
    ])
    reviewer_agent = create_tool_calling_agent(llm, tools, prompt)
    reviewer_agent_executor = AgentExecutor(agent=reviewer_agent, tools=tools, verbose=True)

    result = reviewer_agent_executor.invoke(
        {
            'old_branch': old_branch,
            'new_branch': new_branch,
        },
        verbose=True,
    )

    return result['output']
