---
name: unreachable-output
description: Has output fields not referenced in Steps
version: "1.0"
---

# Role
You are an assistant.

# Input
- `query`: string (required) - A query

# Output
- **answer**: The main answer
- **confidence**: Confidence score
- **sources**: Reference sources

# Steps
1. Read {{query}}
2. Generate **answer**
