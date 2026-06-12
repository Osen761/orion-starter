"""LangChain tools for Orion's data analyst agent."""

from __future__ import annotations

import contextlib
import io
import queue
import threading
import traceback
from typing import Any

import numpy as np
import pandas as pd
from langchain_core.tools import tool

from app.config.settings import settings


class _ExecutionTimeoutError(TimeoutError):
    """Raised when user-supplied analysis code exceeds the time limit."""


df = pd.read_csv(settings.DATA_PATH)
print(f"Loaded sales dataset with shape: {df.shape}")


@tool
def get_dataset_info() -> str:
    """Returns metadata about the sales dataset including column names, data types, shape, and a sample of rows. Always call this first."""

    # TODO(Phase 2): return dataset metadata for the preloaded DataFrame `df`.
    # Include:
    # - df.shape
    # - column names and dtypes
    # - the first 3 rows as a formatted string
    raise NotImplementedError(
        "TODO: implement get_dataset_info() in app/agent/tools.py"
    )


@tool
def python_repl(code: str) -> str:
    """Executes Python code to analyze the sales data. The DataFrame is already available as `df`. Returns the output of the code or an error message."""

    # TODO(Phase 2): execute the supplied code with `df`, `pd`, and `np`
    # already in scope.
    # Requirements:
    # - capture stdout with io.StringIO + contextlib.redirect_stdout
    # - return errors as strings prefixed with "ERROR: "
    # - enforce a 30-second timeout
    # - keep the tool return value human-readable for agent self-correction
    _ = (code, contextlib, io, queue, threading, traceback, Any, np, pd)
    raise NotImplementedError("TODO: implement python_repl() in app/agent/tools.py")


tools = [get_dataset_info, python_repl]
