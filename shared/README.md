# shared

Definitions shared across IceMeister's layers: message schemas, protocol definitions, and constants.

**Status:** placeholder. Format not yet chosen.

These definitions have to be consumed from several languages:

- C and C++ in `firmware`
- ROS 2 in `controller`
- Kotlin in `backend`
- TypeScript in `frontend`

That rules out a TypeScript-only package. The likely shape is a language-neutral schema format with code generation invoked from each layer's own build.
