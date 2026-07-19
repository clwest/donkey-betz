# Evidence-Integrity Stop — T2

- **Timestamp (UTC):** 2026-07-19T01:54:45.701+00:00
- **Trigger:** T2
- **Reason:** abstain_rate=0.400 exceeds cap 0.3 within window (routed_count=20)
- **Measurement window:** win-5310154b8d764c2a (session)
- **Counter snapshot:** {"routed_count": 20, "ambiguous_count": 4, "unclassifiable_count": 4, "context_needed_count": 0, "operator_override_count": 0}
- **Router state at abort:** disabled for remainder of window
- **Re-enable:** next measurement window boundary (per design §12 abort scope)
- **Route back:** Rigby SIGN cycle + Chris D-verdict required before router logic changes.
