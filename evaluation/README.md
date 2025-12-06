# LLM Evaluation Guide

This folder contains tools for evaluating different LLM models on the RAG system using LLM-as-a-Judge methodology.

## Files

- `generate_qa_dataset.ipynb`: Notebook for automatically generating QA datasets from uploaded PDFs
- `llm_judge_evaluation.ipynb`: Main evaluation notebook that tests multiple models via OpenRouter and uses an LLM judge to score answers
- `qa_dataset.json`: Generated QA dataset (created by generate_qa_dataset.ipynb)

## Quick Start

### 1. Setup Environment Variables

Add to your `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-...              # For embeddings (text-embedding-ada-002)
OPENROUTER_API_KEY=sk-or-v1-...    # For testing models and judge model (Mistral Large)
FORCE_OPENROUTER=true              # Force OpenRouter for all model calls
```

### 2. Start the Server

```bash
cd /path/to/project
python3 main.py
```

The server should be running on `http://localhost:8000`.

### 3. Upload PDFs

Before running evaluation, upload your PDFs to the system via the web interface at `http://localhost:8000`.

### 4. Prepare QA Dataset

You have two options:

#### Option A: Auto-generate (Recommended)
1. Open `generate_qa_dataset.ipynb` in Jupyter
2. Make sure PDFs are uploaded to the system
3. Run all cells to automatically generate questions and answers from your PDFs
4. The dataset will be saved as `qa_dataset.json`

#### Option B: Manual Creation
Create a JSON file with your questions. The format should be:

```json
[
  {
    "id": 1,
    "question": "Your question here",
    "answer": "Reference answer (optional)",
    "context": "Context from PDF (optional)"
  }
]
```

Note: The `answer` field is optional as it's not used in evaluation. Only `question` and `context` are required for evaluation.

### 5. Run Evaluation

1. Open `llm_judge_evaluation.ipynb` in Jupyter
2. Update `DATASET_PATH` to point to your QA dataset
3. Update `MODELS_TO_TEST` with the models you want to test
4. Run all cells

## Model Names

When specifying models in `MODELS_TO_TEST`, you can use:
- Short names: `"gpt-3.5-turbo"` → auto-formatted to `"openai/gpt-3.5-turbo"`
- Full OpenRouter format: `"openai/gpt-4"`, `"anthropic/claude-3-sonnet"`, etc.

See [OpenRouter Models](https://openrouter.ai/models) for available models.

## Output

Results are saved to `llm_judge_results/llm_judge_evaluation_YYYYMMDD_HHMMSS.json` with:
- Individual question evaluations
- Scores on 3 dimensions (Retrieval Relevance, Faithfulness, Answer Quality)
- Summary statistics per model
- Response times and citation counts

## Evaluation Criteria

Each answer is scored 1-5 on:
1. **Retrieval Relevance**: How relevant are the retrieved documents to the query? The judge model evaluates the relationship between the question and the retrieved content.
2. **Faithfulness (Groundedness)**: Is the answer faithful to the retrieved context? Measures whether the answer is supported by the retrieved documents and avoids hallucination.
3. **Answer Quality**: Overall quality of the answer in terms of clarity, completeness, and structure.

