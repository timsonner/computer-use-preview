# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import io
import sys
import time
import termcolor
import webbrowser
from typing import Literal

try:
    import pyautogui
except BaseException:
    pyautogui = None

try:
    from PIL import ImageGrab
except BaseException:
    ImageGrab = None

from ..computer import (
    Computer,
    EnvState,
)

# Enable PyAutoGUI fail-safe to let users abort execution by moving the cursor to any corner.
if pyautogui is not None:
    pyautogui.FAILSAFE = True



class DesktopComputer(Computer):
    """Controls the actual local physical workstation using PyAutoGUI and Pillow."""

    def __init__(
        self,
        initial_url: str | None = None,
    ):
        if pyautogui is None or ImageGrab is None:
            raise ImportError(
                "PyAutoGUI and Pillow (PIL) are required for DesktopComputer. "
                "Please run `pip install pyautogui Pillow` to install them."
            )
        self._initial_url = initial_url

    def __enter__(self):
        termcolor.cprint(
            "Creating physical desktop session...",
            color="green",
            attrs=["bold"],
        )
        if self._initial_url:
            self.navigate(self._initial_url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        termcolor.cprint(
            "Closing physical desktop session.",
            color="green",
            attrs=["bold"],
        )

    def screen_size(self) -> tuple[int, int]:
        return pyautogui.size()

    def open_web_browser(self) -> EnvState:
        return self.navigate("https://www.google.com")

    def click_at(self, x: int, y: int) -> EnvState:
        pyautogui.click(x, y)
        return self.current_state()

    def hover_at(self, x: int, y: int) -> EnvState:
        pyautogui.moveTo(x, y)
        return self.current_state()

    def type_text_at(
        self,
        x: int,
        y: int,
        text: str,
        press_enter: bool,
        clear_before_typing: bool,
    ) -> EnvState:
        pyautogui.click(x, y)
        time.sleep(0.1)

        if clear_before_typing:
            if sys.platform == "darwin":
                pyautogui.hotkey("command", "a")
                pyautogui.press("delete")
            else:
                # Select all and delete. Using backspace instead of delete is crucial:
                # if ctrl+a types a literal '^A' in legacy CMD, backspace will delete the '^A',
                # whereas delete would do nothing (leaving the '^A' prepended to the typed text).
                pyautogui.hotkey("ctrl", "a")
                pyautogui.press("backspace")
            time.sleep(0.1)

        pyautogui.write(text, interval=0.01)

        if press_enter:
            pyautogui.press("enter")
        return self.current_state()

    def scroll_document(
        self, direction: Literal["up", "down", "left", "right"]
    ) -> EnvState:
        if direction == "down":
            pyautogui.scroll(-400)
        elif direction == "up":
            pyautogui.scroll(400)
        elif direction == "left":
            # hscroll is supported on some platforms (macOS/Linux)
            if hasattr(pyautogui, "hscroll"):
                pyautogui.hscroll(-400)
            else:
                pyautogui.press("left")
        elif direction == "right":
            if hasattr(pyautogui, "hscroll"):
                pyautogui.hscroll(400)
            else:
                pyautogui.press("right")
        return self.current_state()

    def scroll_at(
        self,
        x: int,
        y: int,
        direction: Literal["up", "down", "left", "right"],
        magnitude: int,
    ) -> EnvState:
        pyautogui.moveTo(x, y)
        time.sleep(0.1)
        if direction == "down":
            pyautogui.scroll(-magnitude)
        elif direction == "up":
            pyautogui.scroll(magnitude)
        elif direction == "left":
            if hasattr(pyautogui, "hscroll"):
                pyautogui.hscroll(-magnitude)
            else:
                pyautogui.press("left")
        elif direction == "right":
            if hasattr(pyautogui, "hscroll"):
                pyautogui.hscroll(magnitude)
            else:
                pyautogui.press("right")
        return self.current_state()

    def wait_5_seconds(self) -> EnvState:
        time.sleep(5)
        return self.current_state()

    def go_back(self) -> EnvState:
        pyautogui.hotkey("alt", "left")
        return self.current_state()

    def go_forward(self) -> EnvState:
        pyautogui.hotkey("alt", "right")
        return self.current_state()

    def search(self) -> EnvState:
        return self.navigate("https://www.google.com")

    def navigate(self, url: str) -> EnvState:
        normalized_url = url
        if not normalized_url.startswith(("http://", "https://")):
            normalized_url = "https://" + normalized_url
        webbrowser.open(normalized_url)
        return self.current_state()

    def key_combination(self, keys: list[str]) -> EnvState:
        # Map some key names to pyautogui names
        mapped_keys = []
        for key in keys:
            k = key.lower()
            if k == "control":
                k = "ctrl"
            elif k == "command":
                k = "command" if sys.platform == "darwin" else "win"
            elif k == "return":
                k = "enter"
            mapped_keys.append(k)

        pyautogui.hotkey(*mapped_keys)
        return self.current_state()

    def drag_and_drop(
        self, x: int, y: int, destination_x: int, destination_y: int
    ) -> EnvState:
        pyautogui.moveTo(x, y)
        pyautogui.dragTo(destination_x, destination_y, duration=0.5)
        return self.current_state()

    def current_state(self) -> EnvState:
        # Wait a moment for UI rendering to complete
        time.sleep(0.5)
        screenshot = ImageGrab.grab()
        # Save screenshot directly to an in-memory PNG buffer
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        screenshot_bytes = buffer.getvalue()
        return EnvState(screenshot=screenshot_bytes, url="desktop")
