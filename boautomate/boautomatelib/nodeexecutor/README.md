Code executor on the node
=========================

Creates environment on the node that is executing the pipeline code.

The `NodeExecutor` class should be a base class of all scripts.
`Context` is a component that provides all tools you request, it includes the input payload from request, 
and configuration of a pipeline.

```python
from boautomate.boautomatelib.nodeexecutor.slack import Slack

# (...)

self.context().get_tool(Slack).send('El bien más preciado es la libertad, hay que defenderla con fe y valor.')
```

- Pipeline utils
- Base class
- Facts parsing
- Context
