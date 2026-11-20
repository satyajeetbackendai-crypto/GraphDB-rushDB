"""RushDB-backed knowledge graph: entities are records, facts are relationships."""
import os

from rushdb import RushDB

ENTITY_LABEL = "Entity"


class GraphStore:
    def __init__(self, api_key: str | None = None):
        self.db = RushDB(api_key or os.environ["RUSHDB_API_KEY"])

    def upsert_entity(self, name: str, kind: str, description: str = ""):
        """Create the entity, or reuse it if one with the same name exists."""
        data = {"name": name.strip(), "kind": kind.strip() or "Thing"}
        if description:
            data["description"] = description
        return self.db.records.upsert(
            data, label=ENTITY_LABEL, options={"mergeBy": ["name"], "mergeStrategy": "append"}
        )

    def add_fact(self, source, target, rel_type: str):
        rel = rel_type.strip().upper().replace(" ", "_") or "RELATED_TO"
        self.db.records.attach(source.id, target.id, {"type": rel, "direction": "out"})

    def save_graph(self, graph: dict) -> tuple[int, int]:
        """graph = {"entities":[{name,type,description}], "relationships":[{source,target,type}]}"""
        records = {}
        for e in graph.get("entities", []):
            rec = self.upsert_entity(e["name"], e.get("type", ""), e.get("description", ""))
            records[e["name"].strip().lower()] = rec

        facts = 0
        for r in graph.get("relationships", []):
            src = records.get(r["source"].strip().lower()) or self.upsert_entity(r["source"], "")
            tgt = records.get(r["target"].strip().lower()) or self.upsert_entity(r["target"], "")
            self.add_fact(src, tgt, r["type"])
            facts += 1
        return len(records), facts

    def entities(self) -> dict[str, dict]:
        res = self.db.records.find({"labels": [ENTITY_LABEL], "limit": 1000})
        return {r.id: r.get_data() for r in res}

    def facts(self) -> list[tuple[str, str, str]]:
        """All (source, RELATION, target) triples in the graph."""
        names = {rid: d.get("name", rid) for rid, d in self.entities().items()}
        rels = self.db.relationships.find({}, pagination={"limit": 1000})
        triples = []
        for rel in rels:
            r = rel if isinstance(rel, dict) else rel.__dict__
            if r.get("sourceId") in names and r.get("targetId") in names:
                triples.append((names[r["sourceId"]], r["type"], names[r["targetId"]]))
        return sorted(set(triples))

    def neighbours(self, name: str) -> list[tuple[str, str, str]]:
        n = name.strip().lower()
        return [t for t in self.facts() if t[0].lower() == n or t[2].lower() == n]

    def clear(self):
        self.db.records.delete({"labels": [ENTITY_LABEL]})
