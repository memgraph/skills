"""Skill-evaluation harness for the memgraph/skills repo.

Implements the agentskills.io "Evaluating skills" methodology: each test case is
run twice (WITH the skill injected as context, and WITHOUT it as a baseline), an
LLM judge grades every assertion PASS/FAIL with evidence, and results are
aggregated per iteration into a with-vs-without benchmark.

See evals/README.md for usage.
"""

__all__ = ["schema", "grader", "aggregate", "client", "run_evals"]
