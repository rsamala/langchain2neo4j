from langchain.agents.agent import AgentExecutor
from langchain.agents.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent
from langchain.agents import AgentType

from cypher_database_tool import LLMCypherGraphChain
from fulltext_neo4j_tool import LLMFulltextGraphChain
from cosine_neo4j_tool import LLMNeo4jVectorChain


class MovieAgent(AgentExecutor):
    """Movie agent"""

    @staticmethod
    def function_name():
        return "MovieAgent"

    @classmethod
    def initialize(cls, movie_graph, model_name, *args, **kwargs):
        if model_name in ['gpt-3.5-turbo', 'gpt-4']:
            llm = ChatOpenAI(temperature=0, model_name=model_name)
        else:
            llm = OpenAI(temperature=0, model_name=model_name)

        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True)

        cypher_tool = LLMCypherGraphChain(
            llm=llm, graph=movie_graph, verbose=True)
        fulltext_tool = LLMFulltextGraphChain.from_llm(
            llm=llm, verbose=True, graph=movie_graph)
        vector_tool = LLMNeo4jVectorChain.from_llm(
            llm=llm, verbose=True, graph=movie_graph
        )

        # Load the tool configs that are needed.
        tools = [
            Tool(
                name="Cypher",
                func=cypher_tool.run,
                description="""
                Utilize this tool to search within a movie database, specifically designed to answer movie-related questions.
                This specialized tool offers streamlined search capabilities to help you find the movie information you need with ease.
                Input should be full question.""",
            ),
            Tool(
                name="Full text",
                func=fulltext_tool.run,
                description="Utilize this when you can't find information about movies from other tools.Input should be a list of relevant movies.",
            ),
            Tool(
                name="Vector search",
                func=vector_tool.run,
                description="Utilize this when you can't find information about movies from other tools.Input should be full question.",
            ),

        ]

        agent_chain = initialize_agent(
            tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)

        return agent_chain

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)
