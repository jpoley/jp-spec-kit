---
id: task-076
title: Local RAG system for Claude Code subagents using DuckDB and HNSW
status: To Do
assignee: []
created_date: '2025-11-26 23:45'
labels:
  - research
  - rag
  - duckdb
  - infrastructure
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement a tool-first, per-subagent, local RAG system using DuckDB + HNSW where each Claude Code subagent has its own isolated knowledge base accessible via MCP tools. Enables agents to retrieve organization-specific facts, patterns, and policies without embedding everything in prompts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Design per-agent storage layout with DuckDB schema (documents + embeddings tables) and HNSW index strategy
- [ ] #2 Implement ingestion pipeline: source collection, markdown/HTML/PDF parsing, chunking (300-800 tokens), and embedding generation
- [ ] #3 Implement local RAG microservice with POST /rag/query endpoint supporting agent_id, query, top_k, and filters
- [ ] #4 Implement MCP tool adapter (subagent_rag_search) that bridges Claude Code to the RAG service
- [ ] #5 Create retrieval quality test suite with 20-50 representative queries and precision/recall metrics
- [ ] #6 Document operational runbook: index rebuild, content updates, debugging slow queries
<!-- AC:END -->
