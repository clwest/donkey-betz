# Consolidated Daily Consolidation

**Consolidation Date:** 2025-08-06  
**Reason:** Multiple low-quality files from 2025-03-24  
**Original Files:** 20  
**Generated for UKF Embedding**

---

## File 2: DONKEY-2025-03-24-FLT-readme-7f77.md
**Original Path:** `17-donkey-betz/DONKEY-2025-03-24-FLT-readme-7f77.md`  
**Date Consolidated:** 2025-08-06 19:05:01

# The Impeller Geometry Library

Set of utilities used by most graphics operations. While the utilities
themselves are rendering backend agnostic, the layout and packing of the various
POD structs is arranged such that these can be copied into device memory
directly. The supported operations also mimic GLSL to some extent. For this
reason, the Impeller shader compiler and reflector uses these utilities in
generated code.

---

## File 10: DONKEY-2025-03-24-FLT-readme-b7bc.md
**Original Path:** `17-donkey-betz/DONKEY-2025-03-24-FLT-readme-b7bc.md`  
**Date Consolidated:** 2025-08-06 19:05:01

Android Toolkit
===============

Type-safe managed wrappers around Android objects vended by the NDK. Does not
require linking to libandroid.so. The symbols are resolved via dynamic runtime
lookup so that the toolkit can be built with an older NDK but still run on
modern Android versions and use the latest features.

---

## File 13: DONKEY-2025-03-24-FLT-readme-431d.md
**Original Path:** `17-donkey-betz/DONKEY-2025-03-24-FLT-readme-431d.md`  
**Date Consolidated:** 2025-08-06 19:05:01

# The Impeller Playground

An extension of the testing fixtures set, provides utilities for interactive
experimentation with the Impeller rendering subsystem. One the test author is
satisfied with the behavior of component as verified in the playground, pixel
test assertions can be added to before committing the new test case. Meant to
provide a gentle-er on-ramp to testing Impeller components. The WSI in the
playground allows for points at which third-party profiling and instrumentation
tools can be used to examine isolated test cases.

---

## File 17: DONKEY-2025-03-24-FLT-readme-0c8b.md
**Original Path:** `17-donkey-betz/DONKEY-2025-03-24-FLT-readme-0c8b.md`  
**Date Consolidated:** 2025-08-06 19:05:01

# Timezone data for testing

This directory contains the fixed timezone data version 2019a for testing.  It
is used in the runner tests to show that loading these files from a specified
location results in the TZ data version "2019a" becoming available to the
binaries.

---

## File 19: DONKEY-2025-03-24-FLT-readme-5f40.md
**Original Path:** `17-donkey-betz/DONKEY-2025-03-24-FLT-readme-5f40.md`  
**Date Consolidated:** 2025-08-06 19:05:01

# The Impeller Shader Compiler & Reflector

Host side tooling that consumes [GLSL 4.60 (Core
Profile)](https://www.khronos.org/registry/OpenGL/specs/gl/GLSLangSpec.4.60.pdf)
shaders and generates libraries suitable for consumption by an Impeller backend.
Along with said libraries, the reflector generates code and meta-data to
construct rendering and compute pipelines at runtime.

---
