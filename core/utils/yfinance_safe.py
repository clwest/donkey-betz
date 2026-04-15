"""Safe yfinance call utilities.

Session 1084: yfinance 0.2.65+ uses `curl_cffi.requests.Session` internally
(not stdlib `requests.Session`) and rejects attempts to pass a stdlib
Session via the `session=` kwarg. When yfinance's internal curl calls
have no explicit timeout and upstream returns a half-closed TCP
connection, the call blocks forever at the C level and the calling
process cannot service new work — including background heartbeat threads
that need the Python import lock. Observed this session: default Celery
worker wedged 33min at 0% CPU with CLOSE_WAIT sockets to
`e1/e2-bmr.ycpi.vip.deb.yahoo.com:https`.

Two layers of protection:

1. `make_timeout_session()` — returns a `curl_cffi.requests.Session`
   with a default `timeout` kwarg. curl_cffi honors the init-time
   timeout on every request unless overridden. Pass into
   `yf.Ticker(sym, session=...)` / `yf.Tickers(syms, session=...)`.

2. `fetch_with_timeout(callable_, timeout=60)` — submits a zero-arg
   callable to a shared bounded ThreadPoolExecutor and raises
   `TimeoutError` if it exceeds the wall-clock limit. This is a
   belt-and-suspenders BACKSTOP for cases where yfinance ignores the
   session timeout (internal retries, cached curl handles, etc.). If
   yfinance genuinely hangs at C level, the abandoned thread will leak
   but the caller is unblocked — safer than wedging the whole worker.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as _FuturesTimeout
from typing import Any, Callable

logger = logging.getLogger(__name__)


def make_timeout_session(timeout: float = 30.0):
    """Return a `curl_cffi.requests.Session` with a default timeout.

    Suitable for passing as the `session=` kwarg to `yfinance.Ticker` /
    `yfinance.Tickers`. Each call returns a new Session — callers should
    reuse the instance across multiple ticker lookups in the same batch
    to benefit from HTTP connection pooling.

    curl_cffi is yfinance's required session type as of yfinance 0.2.65;
    attempting to pass a stdlib `requests.Session` raises a ValueError
    inside yfinance. curl_cffi's `timeout` kwarg is honored per-request.
    """
    from curl_cffi import requests as _curl_requests
    return _curl_requests.Session(timeout=timeout, impersonate="chrome")


_shared_executor = ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix="yfinance-safe",
)


def fetch_with_timeout(callable_: Callable[[], Any], timeout: float = 60.0) -> Any:
    """Run `callable_` in a shared bounded executor with a hard timeout.

    Raises `TimeoutError` on deadline. The underlying thread is abandoned
    (not cancelled — Python cannot cancel a running thread), so use this
    as a backstop AFTER the timeout session, not a replacement. If the
    abandoned thread is hung in a C-level `recv()`, it will leak until
    the process restarts. The shared executor caps max concurrent
    abandoned threads at 4 to prevent runaway FD consumption.
    """
    future = _shared_executor.submit(callable_)
    try:
        return future.result(timeout=timeout)
    except _FuturesTimeout:
        logger.warning(
            "[yfinance_safe] call exceeded %.1fs hard backstop — thread abandoned",
            timeout,
        )
        raise TimeoutError(f"yfinance call exceeded {timeout}s hard backstop")
