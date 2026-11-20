"""Microsoft Foundry (Azure OpenAI) client for graph extraction and Q&A."""
import json
import os

from openai import OpenAI

EXTRACT_PROMPT = """Extract a knowledge graph from the user's text.
Return JSON only, in this shape:
{"entities": [{"name": "...", "type": "Person|Organization|Place|Product|Concept|...", "description": "short"}],
 "relationships": [{"source": "<entity name>", "target": "<entity name>", "type": "UPPER_SNAKE_CASE_VERB"}]}
Use the same exact entity name everywhere. Every relationship endpoint must be in "entities"."""

ANSWER_PROMPT = """You answer questions using ONLY the knowledge-graph facts provided.
Facts are written as (source) -[RELATION]-> (target). If the facts don't contain the answer, say so."""


class FoundryLLM:
    def __init__(self):
        endpoint = os.environ.get("FOUNDRY_ENDPOINT", "").rstrip("/")
        key = os.environ.get("FOUNDRY_API_KEY", "")
        if not endpoint or not key:
            raise RuntimeError("Set FOUNDRY_ENDPOINT and FOUNDRY_API_KEY in .env")
        # Foundry / Azure OpenAI exposes an OpenAI-compatible v1 API.
        self.client = OpenAI(base_url=f"{endpoint}/openai/v1/", api_key=key)
        self.model = os.environ.get("FOUNDRY_DEPLOYMENT", "gpt-5.4-mini")

    def _chat(self, system: str, user: str, json_mode: bool = False) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            **({"response_format": {"type": "json_object"}} if json_mode else {}),
        )
        return resp.choices[0].message.content

    def extract_graph(self, text: str) -> dict:
        return json.loads(self._chat(EXTRACT_PROMPT, text, json_mode=True))

    def answer(self, question: str, facts: list[tuple[str, str, str]]) -> str:
        lines = "\n".join(f"({s}) -[{r}]-> ({t})" for s, r, t in facts) or "(graph is empty)"
        return self._chat(ANSWER_PROMPT, f"Facts:\n{lines}\n\nQuestion: {question}")
