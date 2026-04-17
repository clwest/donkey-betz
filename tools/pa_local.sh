#!/bin/bash
# Local PA chat shortcut.
#
# Session 1098 fix: token + conversation_id belong to donkeyking (the
# account Chris is logged into via the ChatUI). Previously this wrapper
# pointed at admin's token + conversation_id, which silently routed all
# Claude Code → Rigby chatter to an account Chris couldn't see in the
# UI. Memory rule: pa_chat.py defaults to PROD; this wrapper forces
# LOCAL + the right user.
#
# To change the default conversation (e.g., start a new thread), edit
# the --conversation flag below. Current value matches what donkeyking
# has been using in the ChatUI.
export PA_API_URL=http://localhost:8000
export PA_API_TOKEN=e3c7276f00f12b77bda365c7c186577cd854cf2a
python tools/pa_chat.py "$@" --tools --conversation pa-d19c1674b936
