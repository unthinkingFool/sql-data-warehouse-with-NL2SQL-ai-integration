
# nl2sql/executor.py
"""
SQL Executor: Connects to SQL Server and executes the generated query.
Includes safety checks to prevent non-SELECT queries from running.
"""

import os
import re
import time
from dataclasses import dataclass
from typing import Optional, Tuple
import pandas as pd
import pyodbc
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ExecutionResult:
    """The result of executing a SQL query."""
    success: bool
    data: Optional[pd.DataFrame]   # Query results as DataFrame
    row_count: int
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


def _get_connection() -> pyodbc.Connection:
    """Creates a connection to SQL Server using environment variables."""
    server = os.environ.get("SQL_SERVER", r"Swapnil\SQLEXPRESS")
    database = os.environ.get("SQL_DATABASE", "DataWareHouse")
    trusted = os.environ.get("SQL_TRUSTED_CONNECTION", "yes").lower() == "yes"

    if trusted:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=yes;"
        )
    else:
        user = os.environ["SQL_USER"]
        password = os.environ["SQL_PASSWORD"]
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
        )

    return pyodbc.connect(conn_str, timeout=30)


def _is_safe_query(sql: str) -> Tuple[bool, str]:
    """
    Safety check: ensures the query is a SELECT statement only.
    Returns (is_safe, reason_if_not_safe).
    """
    # Normalize whitespace and case
    normalized = re.sub(r'\s+', ' ', sql.strip()).upper()

    # Must start with SELECT or WITH (for CTEs)
    if not re.match(r'^(SELECT|WITH)\s', normalized):
        return False, "Query must start with SELECT or WITH (CTE). No DML or DDL allowed."

    # Block dangerous keywords anywhere in the query.
    # xp_ and sp_ are prefixes glued onto a procedure name (e.g. xp_cmdshell),
    # so a \b...\b word-boundary match won't catch them - check as plain substrings instead.
    dangerous_words = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE', 'EXEC', 'EXECUTE']
    dangerous_prefixes = ['XP_', 'SP_']

    for keyword in dangerous_words:
        if re.search(rf'\b{keyword}\b', normalized):
            return False, f"Dangerous keyword detected: {keyword}"

    for prefix in dangerous_prefixes:
        if prefix in normalized:
            return False, f"Dangerous keyword detected: {prefix}"

    return True, ""


def execute_query(sql: str, max_rows: int = 500) -> ExecutionResult:
    """
    Executes a SQL query against the data warehouse.

    Args:
        sql: The T-SQL query to execute (must be a SELECT).
        max_rows: Maximum number of rows to return (default: 500).

    Returns:
        ExecutionResult with data as a pandas DataFrame.
    """
    if not sql or not sql.strip():
        return ExecutionResult(
            success=False,
            data=None,
            row_count=0,
            error="No SQL query provided."
        )

    # Safety check first
    is_safe, reason = _is_safe_query(sql)
    if not is_safe:
        return ExecutionResult(
            success=False,
            data=None,
            row_count=0,
            error=f"Query blocked by safety check: {reason}"
        )

    conn = None
    try:
        conn = _get_connection()
        start = time.time()
        df = pd.read_sql(sql, conn)
        elapsed_ms = (time.time() - start) * 1000

        # Truncate to max_rows
        if len(df) > max_rows:
            df = df.head(max_rows)

        return ExecutionResult(
            success=True,
            data=df,
            row_count=len(df),
            execution_time_ms=round(elapsed_ms, 1)
        )

    except pyodbc.Error as e:
        return ExecutionResult(
            success=False,
            data=None,
            row_count=0,
            error=f"SQL Server error: {str(e)}"
        )
    except Exception as e:
        return ExecutionResult(
            success=False,
            data=None,
            row_count=0,
            error=f"Unexpected error: {str(e)}"
        )
    finally:
        if conn is not None:
            conn.close()