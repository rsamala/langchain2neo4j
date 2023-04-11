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

3. You need to create a full text index in Neo4j using this Cypher statement:

```cypher
CREATE FULLTEXT INDEX movie IF NOT EXISTS
FOR (n:Movie)
ON EACH [n.title]
```

7. Open the application in your browser at http://localhost:3000

## Example questions
```
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
```