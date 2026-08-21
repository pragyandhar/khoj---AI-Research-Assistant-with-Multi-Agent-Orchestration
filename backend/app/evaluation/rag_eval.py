# WHAT DOES THIS FILE DO: Evaluates the RAG pipeline's retrieval and answer quality using RAGAS metrics.
#
# NOTE ON THIS ENVIRONMENT: `ragas` (any version resolvable against this project's pinned
# langchain-community) fails to import here — `ragas.llms.base` unconditionally does
# `from langchain_community.chat_models.vertexai import ChatVertexAI`, a submodule that does
# not exist in langchain-community>=0.4.2. This is an upstream ragas/langchain-community
# incompatibility, not something fixable from this file. `ragas` and `datasets` are therefore
# imported lazily, inside the methods that need them, so importing this module — and the rest
# of the app — never breaks even where ragas itself cannot be imported. Running an actual
# evaluation requires an environment with a compatible ragas/langchain-community pairing and a
# real OpenAI API key (RAGAS metrics score faithfulness/relevancy via live LLM calls).

# ================== IMPORTS ==================
from app.agents.summary_agent import SummaryAgent
from app.core.logging import get_logger
from app.tools.rag_retriever import rag_search
# ================== IMPORTS ==================


# =========== VARIABLES : Evaluation Logger ===========
logger = get_logger(__name__)               # USE: RAG evaluation execution logger instance
# =========== VARIABLES : Evaluation Logger ===========


# =========== CLASS ===========
# ROLE: Runs RAGAS evaluation over the RAG pipeline's retrieval and generation quality.
class RAGEvaluator:
    """ Builds an evaluation dataset from live RAG search + summary runs, then scores it with RAGAS. """

    DEFAULT_QUERIES = [
        "What is quantum computing?",
        "How does CRISPR gene editing work?",
        "What are the latest advances in battery technology?",
        "Explain how Kubernetes orchestrates containers.",
        "What causes climate change?",
        "How do large language models generate text?",
        "What is the significance of the Higgs boson?",
        "How does blockchain achieve consensus?",
        "What are the health benefits of intermittent fasting?",
        "How do neural networks learn through backpropagation?",
    ]                                            # USE: Default 10 sample queries for run_evaluation_report()


    # =========== FUNCTION ===========
    # ROLE: Builds a RAGAS-compatible dataset from live RAG retrieval and summary generation.
    async def prepare_eval_dataset(self, test_queries: list[str]):
        """ Runs each query through rag_search and the summary agent to build an eval dataset. """

        from datasets import Dataset            # USE: Lazy import — optional, heavy dependency

        # FLOW-1: For each query, retrieve context and generate an answer to be scored
        questions, answers, contexts = [], [], []  # USE: Parallel lists building the eval dataset
        summary_agent = SummaryAgent()           # USE: Shared agent generating answers from retrieved context

        for query in test_queries:
            context = await rag_search.ainvoke({"query": query})  # USE: Retrieved context for this query
            report = await summary_agent.run(research_output=context, original_query=query, topic="general")  # USE: Generated answer

            questions.append(query)
            answers.append(report.summary)
            contexts.append([context])           # USE: RAGAS expects a list of context chunks per question

        # FLOW-2: Assemble the RAGAS dataset schema
        return Dataset.from_dict({"question": questions, "answer": answers, "contexts": contexts})
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Scores a prepared dataset on faithfulness, answer relevancy, and context precision.
    async def evaluate(self, dataset) -> dict:
        """ Runs RAGAS metrics over the dataset and returns their aggregate scores. """

        import asyncio

        from ragas import evaluate as ragas_evaluate  # USE: Lazy import — see module-level note
        from ragas.metrics import faithfulness, answer_relevancy, context_precision

        # FLOW-1: ragas.evaluate is a blocking call — run it off the event loop
        result = await asyncio.to_thread(
            ragas_evaluate,
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision],
        )                                       # USE: RAGAS scoring run

        # FLOW-2: Return the three headline scores as a plain dict
        return {
            "faithfulness": result["faithfulness"],
            "answer_relevancy": result["answer_relevancy"],
            "context_precision": result["context_precision"],
        }
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Convenience entrypoint building the default dataset, evaluating it, and logging results.
    async def run_evaluation_report(self) -> None:
        """ Evaluates the RAG pipeline against the default sample queries and logs the scores. """

        # FLOW-1: Build the dataset, evaluate it, and log the resulting metric scores
        dataset = await self.prepare_eval_dataset(self.DEFAULT_QUERIES)  # USE: Dataset from 10 sample queries
        results = await self.evaluate(dataset)  # USE: Aggregate RAGAS scores

        logger.info("ragas_evaluation", **results)  # USE: Resume-metric audit log
    # =========== FUNCTION ===========
# =========== CLASS ===========
