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

## Example questions

# I have already watched Top Gun
MATCH (u:User {{id: $userId}}), (m:Movie {{title:"Top Gun"}})
MERGE (u)-[:WATCHED]->(m)
RETURN distinct {{answer: 'noted'}} AS result
# I like Top Gun
MATCH (u:User {{id: $userId}}), (m:Movie {{title:"Top Gun"}})
MERGE (u)-[:LIKE_MOVIE]->(m)
RETURN distinct {{answer: 'noted'}} AS result
# What is a good comedy?
MATCH (u:User {{id:$userId}}), (m:Movie)-[:IN_GENRE]->(:Genre {{name:"Comedy"}})
WHERE NOT EXISTS {{(u)-[:WATCHED]->(m)}}
RETURN {{movie: m.title}} AS result
ORDER BY m.imdbRating DESC LIMIT 1
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
# Recommend a movie
MATCH (u:User {{id: $userId}})-[:LIKE_MOVIE]->(m:Movie)
MATCH (m)<-[r1:RATED]-()-[r2:RATED]->(otherMovie)
WHERE r1.rating > 3 AND r2.rating > 3 AND NOT EXISTS {{(u)-[:WATCHED|LIKE_MOVIE|DISLIKE_MOVIE]->(otherMovie)}}
WITH otherMovie, count(*) AS count
ORDER BY count DESC
LIMIT 1
RETURN {{recommended_movie:otherMovie.title}} AS result
