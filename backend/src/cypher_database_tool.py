from database import Neo4jDatabase
from pydantic import BaseModel, Extra
from langchain.prompts.prompt import PromptTemplate
from langchain.prompts.base import BasePromptTemplate
from langchain.llms.base import BaseLLM
from langchain.chains.llm import LLMChain
from langchain.chains.base import Chain
from typing import Dict, List, Any

import logging
logger = logging.getLogger(__name__)

examples = """
# Who played in Top Gun?
MATCH (m:Movie)<-[r:ACTED_IN]-(a)
RETURN {{actor: a.name, role: r.role}} AS result
# What is the plot of the Copycat movie?
MATCH (m:Movie {{title: "Copycat"}})
RETURN {{plot: m.plot}} AS result
# Did Luis Guzmán appear in any other movies?
MATCH (p:Person {{name:"Luis Guzmán"}})-[r:ACTED_IN]->(movie)
RETURN {{movie: movie.title, role: r.role}} AS result
# Do you know of any matrix movies?
MATCH (m:Movie)
WHERE toLower(m.title) CONTAINS toLower("matrix")
RETURN {{movie:m.title}} AS result
# Which movies do I like?
MATCH (u:User {{id: $userId}})-[:LIKE_MOVIE]->(m:Movie)
RETURN {{movie:m.title}} AS result
"""


CYPHER_TEMPLATE = """
You are an assistant with an ability to generate Cypher queries based off example Cypher queries.
Example Cypher queries are:\n""" + examples + """\n
Do not response with any explanation or any other information except the Cypher query.
You do not ever apologize and strictly generate cypher statements based of the provided Cypher examples.
You need to update the database using an appropriate Cypher statement when a user mentions their likes or dislikes, or what they watched already.
Do not provide any Cypher statements that can't be inferred from Cypher examples.
Inform the user when you can't infer the cypher statement due to the lack of context of the conversation and state what is the missing context.
The {question} is
"""

CYPHER_PROMPT = PromptTemplate(
    input_variables=["question"], template=CYPHER_TEMPLATE)

TEXT_TEMPLATE = """
You are an assistant that helps to generate text to form nice and human understandable answers based.
The latest prompt contains the information, and you need to generate a human readable response based on the given information.
Make it sound like the information are coming from an AI assistant, but don't add any information.
Do not add any additional information that is not explicitly provided in the latest prompt.
I repeat, do not add any information that is not explicitly given.
The question was 
{question}
and the information used to provide the answer is
{information}
"""

TEXT_PROMPT = PromptTemplate(
    input_variables=["question", "information"], template=TEXT_TEMPLATE)


def clean_answer(text):
    response = text
    # If the model apologized, remove the first line or sentence
    if "apologi" in response:
        if "\n" in response:
            response = " ".join(response.split("\n")[1:])
        else:
            response = " ".join(response.split(".")[1:])
    return response


class LLMCypherGraphChain(Chain, BaseModel):
    """Chain that interprets a prompt and executes python code to do math.
    """

    llm: Any
    """LLM wrapper to use."""
    cypher_prompt: BasePromptTemplate = CYPHER_PROMPT
    text_prompt: BasePromptTemplate = TEXT_PROMPT
    input_key: str = "question"  #: :meta private:
    output_key: str = "answer"  #: :meta private:
    graph: Neo4jDatabase

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.
        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Expect output key.
        :meta private:
        """
        return [self.output_key]

    def _fetch_neo4j_result(self, generated_cypher: str) -> Dict[str, str]:
        import yaml

        self.callback_manager.on_text("\nQuery:\n", verbose=self.verbose)
        self.callback_manager.on_text(
            generated_cypher, color="green", verbose=self.verbose)
        # Convert t to a dictionary
        output = self.graph.query(generated_cypher)
        self.callback_manager.on_text("\nInformation: ", verbose=self.verbose)
        self.callback_manager.on_text(
            output, color="yellow", verbose=self.verbose)
        return {self.output_key: output}

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        logger.critical(f"Cypher generator inputs: {inputs}")
        cypher_executor = LLMChain(
            prompt=self.cypher_prompt, llm=self.llm, callback_manager=self.callback_manager
        )
        self.callback_manager.on_text(
            inputs[self.input_key], verbose=self.verbose)
        t = cypher_executor.predict(
            question=inputs[self.input_key], stop=["Output:"])
        data = self._fetch_neo4j_result(t)
        text_executor = LLMChain(
            prompt=self.text_prompt, llm=self.llm, callback_manager=self.callback_manager
        )
        answer = text_executor.predict(
            question=inputs[self.input_key], information=data)
        return {'answer': clean_answer(answer)}

    @property
    def _chain_type(self) -> str:
        return "neo4j_llm"


if __name__ == "__main__":
    from langchain.llms import OpenAI

    llm = OpenAI(temperature=0.3)
    database = Neo4jDatabase(host="bolt://100.27.33.83:7687",
                             user="neo4j", password="room-loans-transmissions")
    chain = LLMGraphChain(llm=llm, verbose=True, graph=database)

    output = chain.run(
        "Who played in Top Gun?"
    )

    print(output)
