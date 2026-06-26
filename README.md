#  SQL Data Warehouse + NL2SQL Engine

<div align="center">

**A production-grade data warehouse with a natural language query interface — ask business questions in plain English, get real data back.**

*Medallion Architecture (Bronze → Silver → Gold) meets a RAG-powered NL2SQL engine driven by Groq LLaMA 3.3 70B.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQL Server](https://img.shields.io/badge/SQL_Server-Express-CC2927?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=for-the-badge)](https://console.groq.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG_Vector_Store-6C3FC9?style=for-the-badge)](https://www.trychroma.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/swapnil-das-603824236/)

</div>

---

> 📽️ **Demo GIF** — `docs/demo.gif` *(record with Loom: type a plain-English question, watch the SQL generate and execute live)*

---

## ✨ What Makes This Different From A Standard Data Warehouse Project

Most data warehouse repos stop at the Gold layer — pipelines built, data modeled, then queried manually via SSMS. This project goes further.

A full **GenAI layer** sits on top of the warehouse. Analysts ask questions in plain English. The system retrieves schema context using RAG, generates T-SQL using an LLM, executes it safely, and returns both a result table and a plain-English explanation — all in one click.

```
"What are the top 10 customers by revenue in 2013?"
         ↓
 [ChromaDB RAG] — retrieves the 4 most relevant Gold layer schema chunks
         ↓
 [Groq LLaMA 3.3 70B] — generates safe, accurate T-SQL with schema context
         ↓
 [Safety Layer] — blocks any non-SELECT query before it reaches the database
         ↓
 [SQL Server] — executes against the Gold layer star schema
         ↓
 Results Table + Plain-English Explanation + Downloadable CSV
```

This replicates what companies like Stripe, Databricks, and Snowflake are building internally — and it's built end-to-end on top of a solid data engineering foundation.

---

## 📋 Table of Contents

- [Data Architecture](#️-data-architecture)
- [Project Overview](#-project-overview)
- [Tech Stack](#️-tech-stack)
- [Repository Structure](#-repository-structure)
- [Setup & Installation](#️-setup--installation)
- [Example Queries](#-example-queries)
- [Data Quality Monitoring](#-data-quality-monitoring)
- [Skills Demonstrated](#-skills-demonstrated)
- [Important Links & Tools](#-important-links--tools)
- [License](#️-license)
- [About Me](#-about-me)

---

## 🏗️ Data Architecture

![Architecture Diagram](docs/DataArchitecture.png)

## Data Flow Diagram

![Data Flow Diagram](docs/DataFlowDiagram.png)

## Data Integration Model

![Data Integration Model Diagram](docs/DataIntegrationModel.png)

## Data Mart

![Data Mart Diagram](docs/DataMart.png)

---

## 📖 Project Overview

This project is built in two distinct pillars that work together as a single, cohesive production-grade system.

### 🔧 Pillar 1 — Data Engineering (Medallion Architecture)

**Objective:** Develop a modern data warehouse using SQL Server to consolidate sales data, enabling analytical reporting and informed decision-making.

- **Data Architecture:** Designing a Modern Data Warehouse using Medallion Architecture — Bronze, Silver, and Gold layers.
- **ETL Pipelines:** Extracting, transforming, and loading data from two source systems (ERP and CRM) provided as CSV files.
- **Data Quality:** Cleansing and resolving data quality issues prior to analysis.
- **Data Modeling:** Developing fact and dimension tables optimized for analytical queries — `fact_sales`, `dim_customers`, `dim_products`.
- **Analytics & Reporting:** SQL-based reports and dashboards delivering insights into Customer Behavior, Product Performance, and Sales Trends.
- **Documentation:** Clear data model documentation to support both business stakeholders and analytics teams.

### 🤖 Pillar 2 — GenAI Layer (NL2SQL Engine)

**Objective:** Layer a natural language query interface on top of the Gold layer so analysts can query the warehouse in plain English without writing SQL.

- **Schema Documentation (`schema_context.md`):** A richly annotated document describing every Gold layer table, column, business rule, and example question — the foundation of the RAG pipeline.
- **RAG Indexing:** `sentence-transformers/all-MiniLM-L6-v2` embeds the schema into ChromaDB locally. No API cost, runs offline.
- **LLM SQL Generation:** Groq (`llama-3.3-70b-versatile`) translates English questions into T-SQL using retrieved schema context, with structured JSON output and explicit safety instructions.
- **Safety Layer:** Blocks INSERT, UPDATE, DELETE, DROP, TRUNCATE, EXEC, and other dangerous keywords before any query reaches SQL Server.
- **Streamlit UI:** Interactive demo interface — type a question, inspect the generated SQL, see the retrieved schema context, and download results as CSV.
- **Data Quality Monitor:** Automated checks against the Silver and Gold layers, scored by severity (critical / high / medium), producing a structured JSON report.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Database** | Microsoft SQL Server Express | Data warehouse host |
| **SQL Dialect** | T-SQL (Transact-SQL) | Queries, ETL, modeling |
| **ETL & Modeling** | Custom SQL scripts | Bronze → Silver → Gold pipeline |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | Local schema embedding (~80 MB, no API cost) |
| **Vector Store** | ChromaDB (persistent) | Schema chunk retrieval via cosine similarity |
| **LLM** | Groq API — `llama-3.3-70b-versatile` | T-SQL generation from English questions |
| **DB Connector** | `pyodbc` + `sqlalchemy` | SQL Server connection and execution |
| **Data Handling** | `pandas` | Result sets as DataFrames |
| **UI** | Streamlit | Live query interface |
| **Diagrams** | DrawIO | Architecture and data model visuals |
| **Version Control** | Git + GitHub | Source control |

---

## 📂 Repository Structure

```
sql-data-warehouse-with-NL2SQL-ai-integration/
│
├── datasets/                           # Raw datasets (ERP and CRM CSV files)
│
├── docs/                               # Project documentation and architecture details
│   ├── DataArchitecture.drawio
│   ├── DataArchitecture.png
│   ├── DataFlowDiagram.drawio
│   ├── DataFlowDiagram.png
│   ├── DataIntegrationModel.drawio
│   ├── DataIntegrationModel.png
│   ├── DataModel.drawio
│   ├── DataMart.png
│   └── schema_context.md              # ← NEW: enriched schema documentation for RAG
│
├── scripts/                            # SQL scripts for ETL and transformations
│   ├── bronze/                         # Scripts for extracting and loading raw data
│   ├── silver/                         # Scripts for cleaning and transforming data
│   └── gold/                           # Scripts for creating analytical models (star schema)
│
├── tests/                              # Test scripts and quality files     
│
├── nl2sql/                             # ← NEW: the entire GenAI innovation lives here
│   ├── __init__.py
│   ├── embedder.py                    # RAG: reads schema_context.md, builds ChromaDB index
│   ├── retriever.py                   # RAG: finds top-k most relevant schema chunks per question
│   ├── generator.py                   # LLM: sends schema + question to Groq, returns T-SQL
│   ├── executor.py                    # Safely connects to SQL Server, executes, returns DataFrame
│   ├── pipeline.py                    # Orchestrates the full RAG → LLM → Execution flow
│   └── app.py                         # Streamlit UI — the live demo interface
│
├── .env.example                        # ← NEW: environment variable template
├── requirements.txt                    # ← NEW: Python dependencies
├── README.md                           # Project overview and instructions
└── LICENSE                             # MIT License
```

---

## ⚙️ Setup & Installation

### Prerequisites

- SQL Server Express (free) with the data warehouse loaded
- Python 3.10+
- A Groq API key (free tier works) — [Get one at console.groq.com](https://console.groq.com/)

---

### Step 1 — Clone & Install Dependencies

```bash
git clone https://github.com/unthinkingFool/sql-data-warehouse-with-NL2SQL-ai-integration.git
cd sql-data-warehouse-with-NL2SQL-ai-integration
pip install -r requirements.txt
cp .env.example .env
```

**`requirements.txt`**

```text
# LLM calls (Groq)
groq

# Local vector store for RAG
chromadb>=0.4.0

# Local embeddings (no API cost)
sentence-transformers>=2.2.2

# SQL Server ODBC driver
pyodbc>=5.0.0

# ORM / connection management
sqlalchemy>=2.0.0

# Interactive web UI
streamlit>=1.31.0

# Tabular result display
pandas>=2.0.0

# .env file loading
python-dotenv>=1.0.0

# Testing
pytest>=7.0.0
```

---

### Step 2 — Configure `.env`

```dotenv
# Copy this to .env and fill in your values

# Groq LLM
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# SQL Server connection
SQL_SERVER=localhost\SQLEXPRESS
SQL_DATABASE=DataWarehouse
SQL_TRUSTED_CONNECTION=yes

# Optional: use SQL auth instead of Windows auth
# SQL_USER=your_username
# SQL_PASSWORD=your_password
```

---

### Step 3 — Build the Warehouse

Open SSMS and run scripts in order:

```sql
-- Run in SSMS:
scripts/init_database.sql
scripts/bronze/ddl_bronze.sql
scripts/bronze/load_bronze.sql
scripts/bronze/ddl_silver.sql
scripts/silver/load_silver.sql
scripts/gold/load_gold.sql
```

---

### Step 4 — Build the RAG Index *(one-time, ~30 seconds)*

```bash
python -m nl2sql.embedder
# [Embedder] Split schema into 24 chunks
# [Embedder] Loading embedding model (all-MiniLM-L6-v2)...
# [Embedder] Index built. 24 chunks stored in .chroma_db/
```

---

---

### Step 5 — Launch the App

```bash
streamlit run nl2sql/app.py
# Opens http://localhost:8501
```

---

## 💬 Example Queries

The Streamlit UI ships with clickable example questions. Each one tests a different level of SQL complexity:

| Natural Language Question | SQL Complexity |
|---|---|
| Who are the top 10 customers by total revenue? | Single join, GROUP BY |
| What is the total revenue by product category? | Multi-join, aggregation |
| Show monthly sales trends for 2013 | Date functions, GROUP BY |
| What are the top 5 most expensive products in Bikes? | Filter + ORDER BY |
| What is the average order value by customer segment? | JOIN, GROUP BY, AVG |
| How many orders were placed each year? | Date extraction, COUNT |
| Which products have never been sold? | LEFT JOIN, NULL check |
| Customers with no orders in the last 12 months | LEFT JOIN, date filter |
| Month-over-month revenue growth rate | Window function (LAG) |

---


## 🧠 Skills Demonstrated

| Skill Area | What Was Built |
|---|---|
| **Data Engineering** | Medallion Architecture (Bronze → Silver → Gold), ETL pipelines, T-SQL stored procedures |
| **Data Modeling** | Star schema design, SCD handling, surrogate keys, fact & dimension tables |
| **RAG** | Schema embedding with `sentence-transformers`, cosine similarity retrieval via ChromaDB |
| **Prompt Engineering** | Structured JSON output, T-SQL safety constraints, schema prefix enforcement, assumption surfacing |
| **LLM Integration** | Groq API with `llama-3.3-70b-versatile`, context injection, hallucination mitigation |
| **Python Engineering** | Modular package design, dataclasses, error handling, lazy loading |
| **Software Engineering** | Separation of concerns, testable components, environment config, safety-first execution |
| **Analytics** | Customer behavior, product performance, and sales trend reporting via SQL |

---

## 🚀 Project Requirements

### Building the Data Warehouse (Data Engineering)

**Objective:** Develop a modern data warehouse using SQL Server to consolidate sales data, enabling analytical reporting and informed decision-making.

**Specifications:**
- **Data Sources:** Import data from two source systems (ERP and CRM) provided as CSV files.
- **Data Quality:** Cleanse and resolve data quality issues prior to analysis.
- **Integration:** Combine both sources into a single, user-friendly data model designed for analytical queries.
- **Scope:** Focus on the latest dataset only; historization of data is not required.
- **Documentation:** Provide clear documentation of the data model to support both business stakeholders and analytics teams.

### BI: Analytics & Reporting (Data Analysis)

**Objective:** Develop SQL-based analytics to deliver detailed insights into:

- Customer Behavior
- Product Performance
- Sales Trends

These insights empower stakeholders with key business metrics, enabling strategic decision-making.

---

## 🔗 Important Links & Tools

- **[Datasets](https://github.com/unthinkingFool/sql-data-warehouse/tree/main/datasets):** Access to the project datasets (CSV files)
- **[SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads):** Lightweight server for hosting your SQL database
- **[SQL Server Management Studio (SSMS)](https://learn.microsoft.com/en-us/ssms/install/install?view=sql-server-ver16):** GUI for managing and interacting with databases
- **Git Repository:** Set up a GitHub account and repository to manage, version, and collaborate on your code efficiently
- **[DrawIO](https://www.drawio.com/):** Design data architecture, models, flows, and diagrams
- **[Notion Project Steps](https://app.notion.com/p/DATA-WAREHOUSE-PROJECT-38879ef02c298026a5dfcb1b85e53e46?source=copy_link):** Access to All Project Phases and Tasks
- **[Groq](https://groq.com/):** Get free model api.

---

## 🛡️ License

This project is licensed under the MIT License. You are free to use, modify, and share this project with proper attribution.

---

## 🌟 About Me

Hi there! I'm **Swapnil Das**, currently preparing for interviews and diving deep into the data domain. I work with **AI and Machine Learning**, **Agentic AI workflows**, and **data-driven problem solving**. I'm actively expanding my knowledge in databases, SQL Server, and related topics.

I'm passionate about building my career in **Data Engineering**, **Database Engineering**, or **Machine Learning / AI Engineering**.

Let's stay in touch! Feel free to connect with me on the following platform:

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/swapnil-das-603824236/)
