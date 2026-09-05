# Installation, Build, Execution, and Testing

## 1. Requirements

- Python 3.11 or newer
- `pip` and virtual-environment support
- Internet access during installation when dependencies are not cached
- Optional: Ollama or an API key for LLM-backed operation

The deterministic demonstration does not require a model server or API key.

## 2. Install the executable wheel

Extract the archive and enter its top-level directory, then run:

```bash
python3.11 -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install executable/table2text_pydanticai-0.1.0-py3-none-any.whl
```

Confirm both console programs are installed:

```bash
table2text --help
table2text-evaluate --help
```

## 3. Run the supplied deterministic demonstration

On macOS or Linux:

```bash
bash examples/run_deterministic_demo.sh
```

The equivalent platform-independent command is:

```bash
table2text run examples/weather_sample.csv \
  --request "Describe the dataset and report its strongest supported findings." \
  --no-llm \
  --output-dir demo_runs
```

The command prints the run identifier and artifact directory. The final report
is stored under `demo_runs/<run-id>/final_report.md`.

## 4. Configure LLM-backed execution

Copy the supplied environment template into the current working directory:

```bash
cp source/MScProject/table2text_pydanticai/.env.example .env
```

Edit `.env`, select model identifiers, and add only the API key required by the
chosen provider. Never commit or redistribute the completed `.env` file.

Run the workflow without `--no-llm`:

```bash
table2text run examples/weather_sample.csv \
  --request "Describe the dataset and report its strongest supported findings." \
  --output-dir llm_runs
```

## 5. Install from source for development

From the extracted archive root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "source/MScProject/table2text_pydanticai[dev]"
```

Install the larger benchmark stack only when reproducing evaluation metrics:

```bash
python -m pip install -e \
  "source/MScProject/table2text_pydanticai[dev,evaluation]"
```

## 6. Run tests and static checks

```bash
cd source/MScProject/table2text_pydanticai
pytest -p no:rerunfailures
ruff check src tests scripts evaluation/scripts
```

## 7. Build a new wheel

From the archive root with `hatchling` available:

```bash
python -m pip install hatchling
python -m pip wheel --no-deps \
  --wheel-dir executable \
  source/MScProject/table2text_pydanticai
```

The package is pure Python, so the wheel is platform-independent. No separate
native executable is required.

## 8. Evaluation notebooks

Install the evaluation dependencies and Jupyter, then open the notebooks in
`source/MScProject/notebooks/` or
`source/MScProject/table2text_pydanticai/evaluation/notebooks/`. Protected
evaluation artifacts are read-only research records and should not be edited.
