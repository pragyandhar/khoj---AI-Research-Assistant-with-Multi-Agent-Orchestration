# WHAT DOES THIS FILE DO: Integration test asserting the RAG pipeline clears a minimum RAGAS faithfulness score.
#
# This is a live evaluation: RAGAS scores faithfulness/relevancy/precision via real LLM calls
# against a real OpenAI API key, and needs a ragas install compatible with this project's
# pinned langchain-community (see app/evaluation/rag_eval.py's module docstring — that
# compatibility is not guaranteed, and is broken in this repo's default dev environment).
# Neither a real API key nor a working ragas import is available in the default test run, so
# this test only runs when explicitly opted into, and skips with a clear reason otherwise.

# ================== IMPORTS ==================
import os

import pytest

from app.evaluation.rag_eval import RAGEvaluator
# ================== IMPORTS ==================


# =========== VARIABLES : Opt-in flag for this live evaluation ===========
RUN_RAGAS_EVAL = os.environ.get("RUN_RAGAS_EVAL") == "1"  # USE: Explicit opt-in — this test costs real API calls
# =========== VARIABLES : Opt-in flag for this live evaluation ===========


# =========== FUNCTION ===========
# ROLE: Verifies the RAG pipeline's RAGAS faithfulness score clears the 0.7 minimum threshold.
@pytest.mark.asyncio
@pytest.mark.skipif(
    not RUN_RAGAS_EVAL,
    reason="Set RUN_RAGAS_EVAL=1 (with a compatible ragas install and a real OPENAI_API_KEY) to run this live RAGAS evaluation."
)
async def test_rag_pipeline_meets_faithfulness_threshold():
    """ Runs a live RAGAS evaluation and asserts faithfulness clears the minimum acceptable score. """

    # FLOW-1: Build the eval dataset from the default sample queries and score it
    evaluator = RAGEvaluator()
    dataset = await evaluator.prepare_eval_dataset(evaluator.DEFAULT_QUERIES)  # USE: Live rag_search + summary agent runs
    results = await evaluator.evaluate(dataset)  # USE: Live RAGAS scoring

    # FLOW-2: The pipeline must stay above the minimum acceptable faithfulness score
    assert results["faithfulness"] > 0.7
# =========== FUNCTION ===========
