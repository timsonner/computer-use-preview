# Computer Use Preview

This program sends a natural-language query to a Gemini computer-use model, then carries out the actions the model returns. It can drive a local Playwright browser, a [Browserbase](https://www.browserbase.com/) session, or the local desktop.

The Playwright and Browserbase paths stay inside a browser. The desktop path (`--env desktop`) uses PyAutoGUI for mouse and keyboard input and Pillow to capture the screen. Model coordinates are on a 0 to 1000 grid. The agent scales them to the environment's pixel size before it clicks or types.

Use the desktop environment only on a machine you intend to control. PyAutoGUI's fail-safe is on: move the pointer to a screen corner to abort.

## Prerequisites

- Python 3.10 or 3.11. Continuous integration in `.github/workflows/main.yaml` runs the tests on those versions.
- A Gemini Developer API key, or a Vertex AI project and location.
- For `--env playwright` (the default): Google Chrome, unless you pass `--channel chromium` (or `none`, or an empty string) to use Playwright's Chromium.
- For `--env browserbase`: a Browserbase API key and project id.
- For `--env desktop`: a graphical session. PyAutoGUI and Pillow are installed with the other dependencies. On macOS, the `command` key stays Command. On other platforms it is sent as the Windows key.

## Install

There is no separate compile or package step. Install the dependencies and run `main.py` from the repository root.

On Debian or Ubuntu, if `python3 -m venv` reports that ensurepip is missing, install the matching venv package first (this environment needed `python3.12-venv`).

```bash
git clone https://github.com/timsonner/computer-use-preview.git
cd computer-use-preview
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install the Chrome build Playwright launches by default:

```bash
python -m playwright install chrome
```

`python -m playwright install --with-deps chrome` also installs Playwright's system libraries. That flag may need administrator rights.

## Run

Set credentials, then pass a query. `--query` is required.

Gemini Developer API:

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
python main.py --query "Go to Google and type Hello World into the search bar"
```

Vertex AI. `USE_VERTEXAI` must be `true` or `1` (case is ignored). The client also receives `VERTEXAI_PROJECT` and `VERTEXAI_LOCATION`.

```bash
export USE_VERTEXAI=true
export VERTEXAI_PROJECT="YOUR_PROJECT_ID"
export VERTEXAI_LOCATION="YOUR_LOCATION"
python main.py --query "Go to Google and type Hello World into the search bar"
```

## Test

The tests are `unittest` cases. CI runs them with pytest, and they do not call the live API.

```bash
pytest
```

## Usage

```bash
python main.py --help
```

| Argument | Default | What it does |
| --- | --- | --- |
| `--query` | required | Natural-language instruction for the agent. |
| `--env` | `playwright` | `playwright`, `browserbase`, or `desktop`. |
| `--initial_url` | `https://www.google.com` | Page loaded at start. The desktop environment opens this URL in the system browser. |
| `--highlight_mouse` | off | Playwright only. Draws a red circle at the action point for about two seconds. |
| `--model` | `gemini-2.5-computer-use-preview-10-2025` | Model name passed to the Gemini client. |
| `--channel` | `chrome` | Playwright browser channel, such as `chrome`, `chrome-beta`, or `msedge`. `chromium`, `none`, or an empty string selects Playwright's default Chromium. |
| `--ignore_https_errors` | off | Playwright only. Continues when the certificate is not trusted. |

Playwright and Browserbase use a 1440 by 900 viewport. The desktop environment uses the size reported by PyAutoGUI.

If `PLAYWRIGHT_HEADLESS` is set to any non-empty value, the local Playwright browser starts headless. Leave it unset for a visible window. A value such as `false` is still non-empty, so it turns headless on.

Browserbase reads `BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID`. The process prints the Browserbase session page when the session starts.

Examples:

```bash
python main.py --env playwright --highlight_mouse --query "Go to Google and type Hello World into the search bar"
```

```bash
python main.py --env playwright --channel chromium --ignore_https_errors --initial_url "https://localhost" --query "Open the page and describe what is on it"
```

```bash
export BROWSERBASE_API_KEY="YOUR_BROWSERBASE_API_KEY"
export BROWSERBASE_PROJECT_ID="YOUR_BROWSERBASE_PROJECT_ID"
python main.py --env browserbase --query "Go to Google and type Hello World into the search bar"
```

```bash
python main.py --env desktop --initial_url "https://www.google.com" --query "Search for the weather"
```

The model can request these actions: `open_web_browser`, `click_at`, `hover_at`, `type_text_at`, `scroll_document`, `scroll_at`, `wait_5_seconds`, `go_back`, `go_forward`, `search`, `navigate`, `key_combination`, and `drag_and_drop`. A sample custom function, `multiply_numbers`, is also registered and returns the product of two numbers.

If a model call includes a safety decision of `require_confirmation`, the program prints the explanation and asks `Do you wish to proceed? [Yes]/[No]`. Answering no ends the loop. If the API blocks the prompt, the program raises an error that includes the block reason.

## Layout

```text
main.py                 Command-line entry point
agent.py                Gemini tool loop and action dispatch
requirements.txt        Python dependencies
test_agent.py           Agent unit tests
test_main.py            CLI unit tests
computers/computer.py   Environment interface
computers/playwright/   Local Playwright browser
computers/browserbase/  Browserbase session
computers/desktop/      Local desktop via PyAutoGUI and Pillow
.github/workflows/main.yaml
```

## License

Apache License 2.0. See [LICENSE](LICENSE).

Contributions follow [CONTRIBUTING.md](CONTRIBUTING.md): a Google Contributor License Agreement and review on a GitHub pull request.
