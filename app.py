"""Tiny GraphRAG CLI: Microsoft Foundry extracts the graph, RushDB stores it.

  python app.py ingest sample.txt        # text -> entities + relationships in RushDB
  python app.py load [graph.json]        # load ready-made graph JSON (no LLM needed)
  python app.py ask"Who runs OpenAI?"   # answer from graph facts
  python app.py show                     # print every fact
  python app.py about Microsoft          # facts touching one entity
  python app.py clear                    # delete all entities
"""
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

from graph_store import GraphStore  # noqa: E402


def print_facts(facts):
    for s, r, t in facts:
        print(f"  ({s}) -[{r}]-> ({t})")
    print(f"{len(facts)} fact(s)")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return
    cmd, args = argv[1], argv[2:]
    store = GraphStore()

    if cmd == "ingest":
        from llm import FoundryLLM

        path = Path(args[0]) if args else None
        text = path.read_text(encoding="utf-8") if path and path.exists() else " ".join(args)
        graph = FoundryLLM().extract_graph(text)
        n_ent, n_rel = store.save_graph(graph)
        print(f"Stored {n_ent} entities and {n_rel} relationships in RushDB")
    elif cmd == "load":
        import json

        path = Path(args[0]) if args else Path(__file__).with_name("sample_graph.json")
        n_ent, n_rel = store.save_graph(json.loads(path.read_text(encoding="utf-8")))
        print(f"Loaded {n_ent} entities and {n_rel} relationships into RushDB")
    elif cmd == "ask":
        from llm import FoundryLLM

        print(FoundryLLM().answer(" ".join(args), store.facts()))
    elif cmd == "show":
        print_facts(store.facts())
    elif cmd == "about":
        print_facts(store.neighbours(" ".join(args)))
    elif cmd == "clear":
        store.clear()
        print("Graph cleared")
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv)
