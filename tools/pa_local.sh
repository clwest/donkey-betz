#!/bin/bash
# Local PA chat shortcut
export PA_API_URL=http://localhost:8000
export PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557
python tools/pa_chat.py "$@" --tools --conversation pa-d19c1674b936
