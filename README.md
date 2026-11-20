# GraphDB with Microsoft Foundry + RushDB

A small GraphRAG demo:
1. **Microsoft Foundry** (Azure OpenAI) pulls entities and relationships out of plain text.
2. **RushDB** stores them as a graph: each entity is a record labelled `Entity`, and each fact is a typed relationship.
3. Questions are answered by the LLM using only the facts stored in the graph.

## Setup
```bash
pip install -r requirements.txt
```
Fill in `.env`:
- `RUSHDB_API_KEY`: already set
- `FOUNDRY_ENDPOINT`: e.g. `https://<resource>.openai.azure.com` (Foundry portal → your project → Overview / Models + endpoints)
- `FOUNDRY_API_KEY`: the key for that resource
- `FOUNDRY_DEPLOYMENT`: the name of your model deployment (e.g. `gpt-5.4-mini`)

## Usage
```bash
python app.py ingest sample.txt          # build the graph from a text file (or pass text inline)
python app.py load                       # load sample_graph.json directly (no Foundry needed)
python app.py show                       # list every (source)-[REL]->(target) fact
python app.py about Microsoft            # facts about one entity
python app.py ask "Who is the CEO of OpenAI?"
python app.py clear                      # wipe the graph
```
You can also browse the graph visually in the RushDB dashboard at https://app.rushdb.com.

## Files
- `graph_store.py`: RushDB wrapper (upserts entities by name, attaches relationships, reads triples)
- `llm.py`: Foundry client (graph extraction in JSON mode, grounded answers)
- `app.py`: CLI
