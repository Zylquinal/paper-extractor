# Paper Pipeline

Extract information from research paper PDFs using AI (OpenAI-compatible API) and save results to an Excel file.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
```

Edit `.env`:

```
PAPER_PIPELINE_API_KEY=sk-your-api-key-here
PAPER_PIPELINE_BASE_URL=https://api.openai.com/v1
PAPER_PIPELINE_MODEL=gpt-4o
```

- `PAPER_PIPELINE_API_KEY` — API key (required)
- `PAPER_PIPELINE_BASE_URL` — API base URL (default: `https://api.openai.com/v1`)
- `PAPER_PIPELINE_MODEL` — Model name (default: `gpt-4o`)

## Usage

```bash
python main.py paper.pdf -o output.xlsx
```

With model override:

```bash
python main.py paper.pdf -o output.xlsx --model gpt-4o-mini
```

## Testing

```bash
pytest tests/ -v
```
