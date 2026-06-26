
# nl2sql/pipeline.py
"""
NL2SQL Pipeline: Orchestrates the full flow from English question to SQL results.

Flow:
  English Question
       │
       ▼
  [RAG Retriever]   → finds relevant schema chunks
       │
       ▼
  [SQL Generator]   → LLM turns question + schema into T-SQL
       │
       ▼
  [Safety Check]    → blocks any non-SELECT queries
       │
       ▼
  [SQL Executor]    → runs against SQL Server Gold layer
       │
       ▼
  Structured Result (SQL + Data + Explanation)
"""

from dataclasses import dataclass
from typing import Optional, List
import pandas as pd

from .retriever import retrieve_schema_context
from .generator import generate_sql, GenerationResult
from .executor import execute_query, ExecutionResult


@dataclass
class PipelineResult:
    """Full result of the NL2SQL pipeline."""
    question: str

    # RAG step
    retrieved_context: str

    # LLM step
    generated_sql: str
    explanation: str
    assumptions: List[str]
    confidence: str

    # Execution step
    success: bool
    data: Optional[pd.DataFrame]
    row_count: int
    execution_time_ms: Optional[float]
    error: Optional[str] = None


def run_pipeline(question: str, top_k_context: int = 4) -> PipelineResult:
    """
    Runs the full NL2SQL pipeline for a given English question.

    Args:
        question: The user's English question about the warehouse data.
        top_k_context: How many schema chunks to retrieve for context.

    Returns:
        PipelineResult with all intermediate and final results.

    Example:
        >>> result = run_pipeline("Who are the top 5 customers by total revenue?")
        >>> print(result.generated_sql)
        >>> print(result.data)
    """
    # Step 1: Retrieve relevant schema context (RAG)
    context = retrieve_schema_context(question, top_k=top_k_context)

    # Step 2: Generate SQL using LLM
    gen: GenerationResult = generate_sql(question, context)

    if gen.error or not gen.sql:
        return PipelineResult(
            question=question,
            retrieved_context=context,
            generated_sql=gen.sql or "",
            explanation=gen.explanation,
            assumptions=gen.assumptions,
            confidence=gen.confidence,
            success=False,
            data=None,
            row_count=0,
            execution_time_ms=None,
            error=gen.error or "SQL generation failed - the LLM could not generate a valid query."
        )

    # Step 3: Execute SQL
    exec_result: ExecutionResult = execute_query(gen.sql)

    return PipelineResult(
        question=question,
        retrieved_context=context,
        generated_sql=gen.sql,
        explanation=gen.explanation,
        assumptions=gen.assumptions,
        confidence=gen.confidence,
        success=exec_result.success,
        data=exec_result.data,
        row_count=exec_result.row_count,
        execution_time_ms=exec_result.execution_time_ms,
        error=exec_result.error
    )