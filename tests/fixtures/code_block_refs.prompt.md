---
name: code-block-refs
description: Variables in code blocks should be ignored
version: "1.0"
---

# Role
You are a code assistant.

# Input
- `language`: string (required) - Programming language
- `task`: string (required) - What to generate

# Output
- **code**: Generated code

# Steps
1. Determine {{language}} and {{task}}
2. Generate **code**

Here is an example:
```python
# This {{should_not_be_detected}} as a variable
print("{{also_not_a_var}}")
```
