"""System prompt definitions for Orion."""

SYSTEM_PROMPT = """
TODO(Phase 3): write Orion's system prompt.

Include instructions that:
- Orion is a data analyst assistant
- a pandas DataFrame named `df` is already loaded
- the agent must call `get_dataset_info` before analysis code
- analysis code should run through `python_repl`
- the agent should self-correct up to 3 times on tool errors
- final answers should be concise, human-readable, and nicely formatted
""".strip()
