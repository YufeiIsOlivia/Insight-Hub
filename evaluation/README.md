# LLM Evaluation Guide

This folder contains tools for evaluating different LLM models on the RAG system using LLM-as-a-Judge methodology.

## Files

- `llm_judge_evaluation.ipynb`: Main evaluation notebook that tests multiple models via OpenRouter and uses an LLM judge to score answers
- `qa_dataset_example.json`: Example QA dataset format

## Quick Start

### 1. Setup Environment Variables

Add to your `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-...              # For judge model (GPT-4)
OPENROUTER_API_KEY=sk-or-v1-...    # For testing different models
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
Create a JSON file with your questions. See `qa_dataset_example.json` for format:

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
- Scores on 5 dimensions (Accuracy, Completeness, Relevance, Clarity, Citation Quality)
- Summary statistics per model
- Response times and citation counts

## Evaluation Criteria

Each answer is scored 1-5 on:
1. **Accuracy**: Factual correctness
2. **Completeness**: How fully the question is addressed
3. **Relevance**: How relevant the answer is to the question
4. **Clarity**: How clear and well-structured the answer is
5. **Citation Quality**: Appropriateness and relevance of citations

