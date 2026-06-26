# nl2sql/generator.py
"""
SQL Generator: Uses Groq (Llama 3.3 70B) to generate T-SQL queries from English questions.
The prompt is carefully engineered to be safe, accurate, and explainable.
"""

import os
import re
import json
from dataclasses import dataclass
from typing import Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# The model name lives in .env (GROQ_MODEL), not hardcoded here.
# That way, when Groq deprecates a model, you change one line in .env
# instead of hunting through code.
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


@dataclass
class GenerationResult:
    """The full output of the SQL generation step."""
    sql: str                        # The generated SQL query
    explanation: str                # Plain-English explanation of what the query does
    assumptions: list[str]          # Assumptions made (e.g., "I assumed 'recent' means 2013")
    confidence: str                 # "high", "medium", or "low"
    error: Optional[str] = None     # Set if the LLM couldn't generate valid SQL


SYSTEM_PROMPT = """
You are a SQL expert connected to a data warehouse built on Microsoft SQL Server.
Your job is to translate English business questions into accurate T-SQL queries.

CRITICAL RULES:
1. ONLY generate SELECT statements. Never write INSERT, UPDATE, DELETE, DROP, or any DDL.
2. ALWAYS use the schema prefix. Tables live in: gold.fact_sales, gold.dim_customers, gold.dim_products
3. Use proper T-SQL syntax (SQL Server, not MySQL or PostgreSQL).
4. If a question is ambiguous, state your assumptions clearly.
5. Always add an ORDER BY that makes business sense.
6. Add a TOP 100 clause to all queries unless the user asks for all rows.
7. Use meaningful column aliases so the output is self-explanatory.

OUTPUT FORMAT (JSON — respond with only this, no markdown):
{
  "sql": "SELECT TOP 10 ... FROM gold.fact_sales f JOIN ...",
  "explanation": "This query finds the top 10 customers by total revenue by joining sales with customer data and summing the sales_amount column.",
  "assumptions": ["'Revenue' means sales_amount, not quantity", "Ordered by total revenue descending"],
  "confidence": "high"
}

If you cannot generate a safe, accurate query, set sql to null and explain why in the explanation field.
""".strip()


def generate_sql(question: str, schema_context: str) -> GenerationResult:
    """
    Generates T-SQL from an English question using Groq (Llama 3.3 70B Versatile).

    Args:
        question: The user's English question.
        schema_context: Relevant schema chunks retrieved by the RAG retriever.

    Returns:
        GenerationResult with sql, explanation, assumptions, and confidence.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return GenerationResult(
            sql="",
            explanation="",
            assumptions=[],
            confidence="low",
            error="GROQ_API_KEY is not set. Add it to your .env file."
        )

    client = Groq(api_key=api_key)

    user_message = f"""
Here is the relevant warehouse schema context for this question:

{schema_context}

---

Business Question: {question}

Generate a T-SQL query to answer this question based on the schema above.
Remember: only SELECT, use gold. schema prefix, SQL Server syntax.
""".strip()

    raw_text = ""

    try:
        chat_completion = client.chat.completions.create(
            model=MODEL,
            temperature=0.1,  # low temperature = more deterministic, less "creative" SQL
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},  # ask Groq to guarantee valid JSON syntax
        )

        raw_text = chat_completion.choices[0].message.content.strip()

        # Safety net: strip accidental markdown code fences, just in case
        raw_text = re.sub(r"```(?:json)?|```", "", raw_text).strip()

        parsed = json.loads(raw_text)

        return GenerationResult(
            sql=parsed.get("sql") or "",
            explanation=parsed.get("explanation", ""),
            assumptions=parsed.get("assumptions", []),
            confidence=parsed.get("confidence", "medium")
        )

    except json.JSONDecodeError:
        return GenerationResult(
            sql="",
            explanation="",
            assumptions=[],
            confidence="low",
            error=f"LLM returned non-JSON output. Raw: {raw_text[:300]}"
        )
    except Exception as e:
        return GenerationResult(
            sql="",
            explanation="",
            assumptions=[],
            confidence="low",
            error=str(e)
        )