# Langchain2Neo4j

![LangchainNeo4j Demo](./image/langchain2neo4j.png)

The Langchain2Neo4j is a proof of concept application of how to integrate Neo4j into the Langchain ecosystem.
This project took heavy inspiration from [IMDB-LLM](https://github.com/ibiscp/LLM-IMDB).
The IMDB-LLM integrated graph search using networkx library into langchain ecosystem.
I borrowed the idea and changed the project to use Neo4j as the source of information for the LLM.

## Neo4j database

The project uses the [Recommendation project](https://sandbox.neo4j.com/?usecase=recommendations) that is available as part of the Neo4j Sandbox.
If you want a local instance of Neo4j, you can restore a database dump that is available [here](https://github.com/neo4j-graph-examples/recommendations/tree/main/data).

## Installation and Setup

1. Fill-in the environment variables as shown in the `env.example`

2. Run the project using docker-compose

```bash
docker-compose up
```

7. Open the application in your browser at http://localhost:3000
