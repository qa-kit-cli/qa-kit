"""Rich-based console helpers: banners, step tracker, interactive prompts."""

from __future__ import annotations

import sys
from types import TracebackType
from typing import Sequence, Type

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

console = Console()
err_console = Console(stderr=True)


def print_banner(title: str, subtitle: str = "") -> None:
    text = Text(title, style="bold cyan")
    if subtitle:
        text.append(f"\n{subtitle}", style="dim")
    console.print(Panel(text, border_style="cyan", padding=(0, 2)))


def print_success(msg: str) -> None:
    console.print(f"[bold green]✓[/] {msg}")


def print_warning(msg: str) -> None:
    console.print(f"[bold yellow]![/] {msg}")


def print_error(msg: str) -> None:
    err_console.print(f"[bold red]✗[/] {msg}")


def print_info(msg: str) -> None:
    console.print(f"[dim]→[/] {msg}")


def print_step(n: int, total: int, label: str) -> None:
    console.print(f"[bold cyan][{n}/{total}][/] {label}")


def print_table(headers: Sequence[str], rows: Sequence[Sequence[str]], title: str = "") -> None:
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for h in headers:
        table.add_column(h)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def ask(prompt: str, default: str = "") -> str:
    return Prompt.ask(prompt, default=default, console=console)


def confirm(prompt: str, default: bool = True) -> bool:
    return Confirm.ask(prompt, default=default, console=console)


class StepTracker:
    """Context manager for displaying multi-step progress."""

    def __init__(self, total: int, title: str = "") -> None:
        self._total = total
        self._current = 0
        self._title = title

    def __enter__(self) -> "StepTracker":
        if self._title:
            console.print(f"\n[bold]{self._title}[/]\n")
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass

    def step(self, label: str) -> None:
        self._current += 1
        console.print(f"[bold cyan][{self._current}/{self._total}][/] {label}")

    def done(self, msg: str = "Done") -> None:
        console.print(f"\n[bold green]✓[/] {msg}")


def arrow_select(prompt: str, choices: list[str]) -> str:
    """Arrow-key interactive menu. Falls back to numbered input when not a TTY."""
    if not sys.stdin.isatty():
        return _numbered_select(prompt, choices)

    try:
        import readchar
    except Exception:
        return _numbered_select(prompt, choices)

    current = 0
    n = len(choices)

    def _draw(first: bool = False) -> None:
        if not first:
            # Move cursor up past all choice lines + prompt line
            sys.stdout.write(f"\033[{n + 1}A\033[J")
        sys.stdout.write(f"\033[1m{prompt}\033[0m\n")
        for i, choice in enumerate(choices):
            if i == current:
                sys.stdout.write(f"  \033[1;36m▶ {choice}\033[0m\n")
            else:
                sys.stdout.write(f"    {choice}\n")
        sys.stdout.flush()

    _draw(first=True)

    while True:
        key = readchar.readkey()
        if key == readchar.key.UP and current > 0:
            current -= 1
            _draw()
        elif key == readchar.key.DOWN and current < n - 1:
            current += 1
            _draw()
        elif key in (readchar.key.ENTER, "\n", "\r"):
            console.print()
            return choices[current]


def _numbered_select(prompt: str, choices: list[str]) -> str:
    console.print(f"\n[bold]{prompt}[/]")
    for i, choice in enumerate(choices, 1):
        console.print(f"  [cyan]{i}.[/] {choice}")
    while True:
        raw = Prompt.ask("Enter number", console=console)
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        print_warning("Please enter a valid number.")
