"""Employee-job-specific implementations (Session 1256 PR 1.2).

Each module in this package defines the *job-specific* pieces for one
AI Employee job: probes, step functions, escalation formatters, comms
config. The generic mission lifecycle lives in
``core.employees.mission_runner.MissionRunner``; each job here composes
that runner with its own step set + formatters via a small
``build_<job>_runner()`` factory.

Today: one job (``docs_cascade``). Future jobs follow the same shape.
"""
