# Khoj - AI Research Assistant

Khoj is a multi-agent research assistant. You give it a question, it routes the question to a specialist agent, pauses and asks you for approval before it touches the web, runs the research, summarizes what it finds into a structured report, and checks its own citations before showing you anything. Backend is FastAPI and LangGraph, frontend is React.

I did not build this to ship a product. I built it because I wanted to actually understand how LangGraph state machines, checkpointing and multi-agent handoffs work under the hood instead of just reading about them in a blog post. Most of the decisions in this repo came out of trying something, watching it break, and fixing it until it made sense to me. There are places where it shows.

## What it actually does

- Classifies an incoming query and routes it to a Science, Technology or General research agent
- Pauses before any web search happens and waits for the user to approve, or edit, the query - this is the human in the loop part
- Runs the approved research through Tavily web search, with retry and backoff if the call fails
- Checks ChromaDB for relevant chunks from past research sessions before doing a fresh web search, so it isn't repeating work it has already done
- Summarizes findings into a structured report, with sections and citations
- Verifies every citation both for URL accessibility and for actual relevance to the claim it is attached to, using a seperate LLM call for the second part
- Checkpoints every step to Postgres, so a session can be resumed after a crash, or rolled back to any earlier state (this is the "time travel" feature LangGraph is known for)
- Remembers a user's past queries across sessions using a long-term memory store, separate from the short-term checkpointing

## Architecture

The backend is a LangGraph state machine. Roughly:

```
router -> human_approval (graph pauses here) -> research (specialist agent picked here) -> summary -> citation_check -> output
```

Each node is a plain async function operating on one shared typed state object. Citation checking runs as its own subgraph rather than being bolted onto the main one, mainly so it stays testable on its own. The whole graph is checkpointed with `AsyncPostgresSaver`, which is what makes pause-and-resume across process restarts actually work, not just in theory.

## Stack

- Backend: FastAPI, LangChain, LangGraph, PostgreSQL (SQLAlchemy, async), Redis, ChromaDB, Alembic
- Frontend: React, TypeScript, Vite, Zustand, Tailwind CSS
- Testing: pytest, pytest-asyncio, Playwright for a manual smoke check of the frontend

## Some numbers

I'd rather show actual numbers than describe this as "production grade" and leave it at that.

- 96 commits
- roughly 4,800 lines of backend Python across 66 source files
- roughly 1,000 lines of frontend TypeScript
- 22 automated tests passing, 1 skipped on purpose (explained below)
- 6 build phases, starting from a bare FastAPI skeleton and ending at checkpointed multi-agent orchestration, RAG, long-term memory and a working frontend

None of these numbers prove the code is good. They just prove I actually sat down and did the work instead of stopping after the first agent call worked.

## Getting started

You need Docker, or Python 3.14+ and Node 20+ if you'd rather run things without containers.

```bash
git clone https://github.com/pragyandhar/khoj---AI-Research-Assistant-with-Multi-Agent-Orchestration.git
cd khoj---AI-Research-Assistant-with-Multi-Agent-Orchestration
cp .env.example .env
# fill in OPENAI_API_KEY, TAVILY_API_KEY, etc in .env
docker compose up --build
```

Backend comes up on `localhost:8000`, frontend on `localhost:3000`.

Running the backend directly, without Docker:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

## What is not finished

I would rather write this down than have someone find it out the hard way.

- The RAGAS evaluation module is written and structurally correct, but I cannot actually run it right now. The version of `ragas` that resolves against this project's `langchain-community` pin tries to import a class, `ChatVertexAI`, that does not exist in that version of langchain-community. It's a genuine upstream incompatibility, not a bug in my code, but until it's resolved the "faithfulness score" test skips instead of actually running.
- There is no auth system yet. `user_id` exists in the schema and is threaded through the whole graph, but nothing sets it, so the long-term memory features are wired up but effectively dormant.
- The frontend has been run locally and checked with Playwright, it has not been deployed anywhere.
- The Alembic migration files exist as plain scripts, but `alembic.ini` and `env.py` were never set up, so they cannot be run through the actual `alembic` CLI yet. `create_all_tables()` is what builds the schema for now.

## What I actually learned

The hardest part for me was not any one library, it was realizing how much of "multi agent orchestration" is really just disciplined state management with extra steps. Once I stopped treating the LLM calls as the interesting part and started treating the state transitions as the interesting part, LangGraph made a lot more sense to me.

I also underestimated how many small correctness bugs only show up once you actually run the thing end to end. An async context manager entered the wrong way, an error path that never clears a loading flag, a graph edge that quietly loops back on itself. None of these were visible from reading the code carefully. They only showed up once I ran it and watched it fail.

This is still a learning project first and a portfolio piece second, and I'm sure someone more experienced would structure parts of it differently. But it runs end to end, and the numbers above are real, not aspirational.
