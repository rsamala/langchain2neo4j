from __future__ import annotations
from database import Neo4jDatabase
from langchain.prompts.base import BasePromptTemplate
from langchain.llms.base import BaseLLM
from langchain.chains.llm import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.graph_qa.prompts import ENTITY_EXTRACTION_PROMPT, PROMPT
from langchain.chains.base import Chain

from typing import Any, Dict, List

from pydantic import Field
import logging
logger = logging.getLogger(__name__)


fulltext_search = """
WITH $embedding AS e
MATCH (m:Movie)
WHERE m.embedding IS NOT NULL AND size(m.embedding) = 1536
WITH m, gds.similarity.cosine(m.embedding, e) AS similarity
ORDER BY similarity DESC LIMIT 5
CALL {
  WITH m
  MATCH (m)-[r:!RATED]->(target)
  RETURN coalesce(m.name, m.title) + " " + type(r) + " " + coalesce(target.name, target.title) AS result
  UNION
  WITH m
  MATCH (m)<-[r:!RATED]-(target)
  RETURN coalesce(target.name, target.title) + " " + type(r) + " " + coalesce(m.name, m.title) AS result
}
RETURN result LIMIT 100
"""


class LLMNeo4jVectorChain(Chain):
    """Chain for question-answering against a graph."""

    graph: Neo4jDatabase = Field(exclude=True)
    qa_chain: LLMChain
    input_key: str = "query"  #: :meta private:
    output_key: str = "result"  #: :meta private:
    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()

    @property
    def input_keys(self) -> List[str]:
        """Return the input keys.
        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Return the output keys.
        :meta private:
        """
        _output_keys = [self.output_key]
        return _output_keys

    @classmethod
    def from_llm(
        cls,
        llm: BaseLLM,
        qa_prompt: BasePromptTemplate = PROMPT,
        **kwargs: Any,
    ) -> GraphQAChain:
        """Initialize from LLM."""
        qa_chain = LLMChain(llm=llm, prompt=qa_prompt)

        return cls(qa_chain=qa_chain, **kwargs)

    def _call(self, inputs: Dict[str, str]) -> Dict[str, Any]:
        """Embed a question and do semantich search."""
        question = inputs[self.input_key]
        logger.critical(question)
        embedding = self.embeddings.embed_query(question)
        self.callback_manager.on_text(
            "Query parameters:", end="\n", verbose=self.verbose
        )
        self.callback_manager.on_text(
            embedding[:5], color="green", end="\n", verbose=self.verbose
        )
        context = self.graph.query(
            fulltext_search, {'embedding': embedding})
        self.callback_manager.on_text(
            "Full Context:", end="\n", verbose=self.verbose)
        self.callback_manager.on_text(
            context, color="green", end="\n", verbose=self.verbose
        )
        logger.critical(context)
        result = self.qa_chain({"question": question, "context": context})
        return {self.output_key: result[self.qa_chain.output_key]}


if __name__ == '__main__':
    from langchain.llms import OpenAI

    llm = OpenAI(temperature=0.0)
    database = Neo4jDatabase(host="bolt://100.27.33.83:7687",
                             user="neo4j", password="room-loans-transmissions")
    chain = LLMNeo4jVectorChain.from_llm(llm=llm, verbose=True, graph=database)

    output = chain.run(
        "What type of movie is Grumpier?"
    )

    print(output)
