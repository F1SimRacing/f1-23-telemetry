# F1 23 Telemetry Supporting v29x3
Currently supporting the `v29x3: Update game mode IDs in the appendix` version from
the F1 23 UDP specification which is available [here](https://answers.ea.com/t5/General-Discussion/F1-23-UDP-Specification/td-p/12632888)

# Installing

```commandline
pip install f1-23-telemetry
```

# Running
```commandline
telemetry-f1-23-listener
```

# Usage

```python
from f1_23_telemetry.listener import TelemetryListener

listener = TelemetryListener(port=20777, host='localhost')
packet = listener.get()
```

# Releasing
```commandline
pip install --upgrade build twine
python -m build
python3 -m twine upload f1-23-telemetry dist/
```
