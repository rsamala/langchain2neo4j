from langchain.agents.agent import AgentExecutor
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.tools import Tool
from langchain.llms import OpenAI
from movie_database_tool import LLMGraphChain


class MovieAgent(AgentExecutor):
    """Movie agent"""

    @staticmethod
    def function_name():
        return "MovieAgent"

    @classmethod
    def initialize(cls, movie_graph, *args, **kwargs):
        llm = OpenAI(temperature=0)

        movie_tool = LLMGraphChain(llm=llm, graph=movie_graph, verbose=True)

        # Load the tool configs that are needed.
        tools = [
            Tool(
                name="Movies_chain",
                func=movie_tool.run,
                description="Utilize this tool to search within a movie database, specifically designed to answer movie-related questions. The tool accepts inputs such as clear title, genre, director, actor, or year, ensuring accurate and targeted results. Ideal for inquiries that require information from one or more of the following categories: title, genre, director, actor, or year. This specialized tool offers streamlined search capabilities to help you find the movie information you need with ease.",
            ),
        ]

        agent = ZeroShotAgent.from_llm_and_tools(
            llm, tools
        )

        return cls.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)