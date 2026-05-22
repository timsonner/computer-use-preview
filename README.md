# Computer Use Preview (Workstation & Local Devices Fork)

This repository is a customized fork of the original Google Upstream repository: [google-gemini/computer-use-preview](https://github.com/google-gemini/computer-use-preview).

In addition to the original web-browser-only computer use capabilities, this fork introduces support for **full local workstation control** and enhances testing with **local physical devices**.

---

## 🚀 Key Fork Enhancements

### 1. 🖥️ Full Workstation/Desktop Environment Support (`--env="desktop"`)
You can now let Gemini control your actual local workstation (OS) rather than being restricted to a sandboxed browser window! 
* Uses `PyAutoGUI` for mouse/keyboard inputs and `Pillow` for real-time high-performance memory screenshots.
* **OS Shortcut & Key Support**: Includes mapping for `command+r` to open the Windows Run dialog, pressing `command` to open the Windows Start Menu, typing commands into `cmd.exe`/terminal sessions, and clicking outside browser windows.
* **DPI-Aware Coordinate Scaling**: Safely translates Gemini's normalized `0-1000` coordinate output to your monitor's exact pixel dimensions dynamically.
* **Fail-Safe Built-in**: `pyautogui.FAILSAFE = True` is enabled. You can abort the agent's run at any second simply by moving your physical mouse cursor to any corner of your screen.

### 2. 🔒 Local Device Testing (Self-Signed SSL/TLS Bypass)
When testing on local networks or developer servers (such as firewalls, routers, or self-signed API targets), Playwright would previously fail with `net::ERR_CERT_AUTHORITY_INVALID`.
* We configured browser contexts with `ignore_https_errors=True` by default so the agent can safely interact with local/internal devices during testing.

### 3. 🧹 Clean Logs (Suppressed SDK Warnings)
* Configured `GenerateContentConfig` with `automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)`. This suppresses redundant warning logs printed by the `google-genai` SDK regarding AFC being disabled, ensuring clean console outputs.

---

## Quick Start

This section will guide you through setting up and running the Computer Use Preview model, either the Gemini Developer API or Vertex AI. Follow these steps to get started.

### 1. Installation

**Clone the Repository**

```bash
git clone https://github.com/google/computer-use-preview.git
cd computer-use-preview
```

**Set up Python Virtual Environment and Install Dependencies**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Install Playwright and Browser Dependencies**

```bash
# Install system dependencies required by Playwright for Chrome
playwright install-deps chrome

# Install the Chrome browser for Playwright
playwright install chrome
```

### 2. Configuration
You can get started using either the Gemini Developer API or Vertex AI.

#### A. If using the Gemini Developer API:

You need a Gemini API key to use the agent:

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Or to add this to your virtual environment:

```bash
echo 'export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"' >> .venv/bin/activate
# After editing, you'll need to deactivate and reactivate your virtual
# environment if it's already active:
deactivate
source .venv/bin/activate
```

Replace `YOUR_GEMINI_API_KEY` with your actual key.

#### B. If using the Vertex AI Client:

You need to explicitly use Vertex AI, then provide project and location to use the agent:

```bash
export USE_VERTEXAI=true
export VERTEXAI_PROJECT="YOUR_PROJECT_ID"
export VERTEXAI_LOCATION="YOUR_LOCATION"
```

Or to add this to your virtual environment:

```bash
echo 'export USE_VERTEXAI=true' >> .venv/bin/activate
echo 'export VERTEXAI_PROJECT="your-project-id"' >> .venv/bin/activate
echo 'export VERTEXAI_LOCATION="your-location"' >> .venv/bin/activate
# After editing, you'll need to deactivate and reactivate your virtual
# environment if it's already active:
deactivate
source .venv/bin/activate
```

Replace `YOUR_PROJECT_ID` and `YOUR_LOCATION` with your actual project and location.

### 3. Running the Tool

The primary way to use the tool is via the `main.py` script.

**General Command Structure:**

```bash
python main.py --query "Go to Google and type 'Hello World' into the search bar"
```

**Available Environments:**

You can specify a particular environment with the ```--env <environment>``` flag.  Available options:

- `playwright`: Runs the browser locally using Playwright.
- `browserbase`: Connects to a Browserbase instance.
- `desktop`: Controls the actual local physical workstation using PyAutoGUI and Pillow.

**Local Workstation (Desktop)**

Runs the agent on your host operating system. Perfect for opening system applications, running shell terminals, or controlling multiple OS windows:

```bash
python main.py --query="Open cmd.exe using windows-r and run ipconfig" --env="desktop"
```

**Local Playwright**

Runs the agent using a Chrome browser instance controlled locally by Playwright.

```bash
python main.py --query="Go to Google and type 'Hello World' into the search bar" --env="playwright"
```

You can also specify an initial URL for the Playwright environment:

```bash
python main.py --query="Go to Google and type 'Hello World' into the search bar" --env="playwright" --initial_url="https://www.google.com/search?q=latest+AI+news"
```

**Browserbase**

Runs the agent using Browserbase as the browser backend. Ensure the proper Browserbase environment variables are set:`BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID`.

```bash
python main.py --query="Go to Google and type 'Hello World' into the search bar" --env="browserbase"
```

**Available Models:**

You can choose the model to use by specifying the ```--model <model name>``` flag. Available options on Gemini Developer API and Vertex AI Client:

- `gemini-2.5-computer-use-preview-10-2025`: This is the default model.
- `gemini-3-flash-preview`: The preview version of Gemini 3 Flash.

## Agent CLI

The `main.py` script is the command-line interface (CLI) for running the browser agent.

### Command-Line Arguments

| Argument | Description | Required | Default | Supported Environment(s) |
|-|-|-|-|-|
| `--query` | The natural language query for the browser agent to execute. | Yes | N/A | All |
| `--env` | The computer use environment to use. Must be one of the following: `playwright`, `browserbase`, or `desktop` | No | `playwright` | All |
| `--initial_url` | The initial URL to load when the browser starts. | No | https://www.google.com | `playwright`, `browserbase` |
| `--highlight_mouse` | If specified, the agent will attempt to highlight the mouse cursor's position in the screenshots. This is useful for visual debugging. | No | False (not highlighted) | `playwright` |
| `--model` | The model to use. See the "Available Models" section for more information. | No | `gemini-2.5-computer-use-preview-10-2025` | All |

### Environment Variables

| Variable | Description | Required |
|-|-|-|
| GEMINI_API_KEY | Your API key for the Gemini model. | Yes |
| BROWSERBASE_API_KEY | Your API key for Browserbase. | Yes (when using the browserbase environment) |
| BROWSERBASE_PROJECT_ID | Your Project ID for Browserbase. | Yes (when using the browserbase environment) |

## Known Issues

### Playwright Dropdown Menu

On certain operating systems, the Playwright browser is unable to capture `<select>` elements because they are rendered by the operating system. As a result, the agent is unable to send the correct screenshot to the model.

There are several ways to mitigate this.

1. Use the Browserbase option instead of Playwright.
2. Inject a script like [proxy-select](https://github.com/amitamb/proxy-select) to render a custom `<select>` element. You must inject `proxy-select.css` and `proxy-select.js` into each page that has a non-custom `<select>` element. You can do this in the [`Playwright.__enter__`](https://github.com/google-gemini/computer-use-preview/blob/main/computers/playwright/playwright.py#L100) method by adding a few lines of code, like the following (replacing `PROXY_SELECT_JS` and `PROXY_SELECT_CSS` with the appropriate variables):

```python
self._page.add_init_script(PROXY_SELECT_JS)
def inject_style(page):
    try:
        page.add_style_tag(content=PROXY_SELECT_CSS)
    except Exception as e:
        print(f"Error injecting style: {e}")

self._page.on('domcontentloaded', inject_style)
```

Note, option 2 does not work 100% of the time, but is a temporary workaround for certain websites. The better option is to use Browserbase.
