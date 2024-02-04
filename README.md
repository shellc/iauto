# iauto

`iauto` is a Python library for intelligent automation.

## Key Features

* **Workflow Orchestration**: Defining workflow using YAML, for collaboration and version control
* **Playwright Integration**: Automate web workflows with Playwright
* **Appium Integration**: Automate web, iOS, Android, Windows, and macOS workflows with Appium
* **LLMs Integration**: Integrate AI into automated workflows, support OpenAI API and self-hosting LLMs
    * [OpenAI Chat completion API](https://platform.openai.com/docs/api-reference)
    * [llama.cpp](https://github.com/ggerganov/llama.cpp) with more than 20 modles
    * ChatGLM by chatglm.cpp

## Quick Start

### Installation

Python version requirement: >=3.8

`iauto` can be installed from PyPI using `pip`. It is recommended to create a new virtual environment before installation to avoid conflicts.

```bash
pip install -U iauto
```

To enable cuBLAS acceleration on NVIDIA GPU:

```bash
CMAKE_ARGS="-DGGML_CUBLAS=ON" pip install -U iauto
```

To enable Metal on Apple silicon devices:

```bash
CMAKE_ARGS="-DGGML_METAL=ON" pip install -U iauto
```

### Playbook

Automate your workflow by writing a playbook.

**Example: Web automation**

`browser.yaml`

```yaml
playbook:
  description: Open browser and goto https://bing.com
  actions:
    - browser.open:
        args:
          exec: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
        result: $browser
    - browser.goto:
        args:
          browser: $browser
          url: https://bing.com
        result: $page
    - repeat:
        actions:
          - browser.eval:
              args:
                page: $page
                javascript: new Date()
              result: $now
          - log: $now
          - time.wait: 2
```

Run the playbook:

```bash
python -m iauto ./browser.yaml
```

**Example: Chatbot**

`chatbot.yaml`:

```yaml
playbook:
  description: Chat to OpenAI
  actions:
    - llm.session:
        result: $session
    - repeat:
        actions:
          - shell.prompt:
              args: "Human: "
              result: $prompt
          - llm.chat:
              args:
                session: $session
                prompt: $prompt
              result: $message
          - shell.print: "AI: {$message}"
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=sk-<YOUR_API_KEY>
```

Run the playbook:

```bash
python -m iauto ./chatbot.yaml
```

* [Control Flow](./playbooks/control_flow.yaml)
* [Appium Webdriver](./playbooks/webdriver.yaml)
* [Playwright Browser](./playbooks/browser.yaml)
* [OpenAI REPL Chatbot](./playbooks/openai_repl.yaml)
* [ChatGLM REPL Chatbot](./playbooks/chatglm_repl.yaml)
* [QWen REPL Chatbot](./playbooks/qwen_repl.yaml)
* [LLM ReAct reasoning](./playbooks/llm_react_repl.yaml)
* [Bing search](./playbooks/bing.yaml)
* [Google News](./playbooks/google_news.yaml)

**[More example playbooks](./playbooks)**

## Contribution

We are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

### Development setup

* Code Style: [PEP-8](https://peps.python.org/pep-0008/)
* Docstring Style: [Google Style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)

```bash
# Create python venv
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Apply autopep8, isort and flake8 as pre commit hooks
pre-commit install
```
### Build

```bash
./build.sh
```

## License

[MIT](./LICENSE)
