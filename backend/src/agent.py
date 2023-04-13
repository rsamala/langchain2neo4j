from langchain.agents.agent import AgentExecutor
from langchain.agents.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent
from langchain.agents import AgentType

from cypher_database_tool import LLMCypherGraphChain
from fulltext_neo4j_tool import LLMFulltextGraphChain


class MovieAgent(AgentExecutor):
    """Movie agent"""

    @staticmethod
    def function_name():
        return "MovieAgent"

    @classmethod
    def initialize(cls, movie_graph, model_name, *args, **kwargs):
        llm = ChatOpenAI(temperature=0, model_name=model_name)
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True)

        cypher_tool = LLMCypherGraphChain(
            llm=llm, graph=movie_graph, verbose=True)
        fulltext_tool = LLMFulltextGraphChain.from_llm(
            llm=llm, verbose=True, graph=movie_graph)

        # Load the tool configs that are needed.
        tools = [
            Tool(
                name="Cypher movies",
                func=cypher_tool.run,
                description="""
                Utilize this tool to search within a movie database, specifically designed to answer movie-related questions. 
                The tool accepts inputs such as clear title, genre, director, actor, or year, ensuring accurate and targeted results. 
                Ideal for inquiries that require information from one or more of the following categories: title, genre, director, actor, or year. 
                This specialized tool offers streamlined search capabilities to help you find the movie information you need with ease.
                Input should be full question.""",
            ),
            Tool(
                name="Full text",
                func=fulltext_tool.run,
                description="Utilize this tool to when the movies chain does not provide any context.",
            ),
        ]

        agent_chain = initialize_agent(
            tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)

        return agent_chain

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)
