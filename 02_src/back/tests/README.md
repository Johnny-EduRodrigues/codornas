# Tests

The file __init__.py must exists, so unittest can find tests inside subfoldes.

# Run

Inside the "back" folder, run:

```bash
uv run --project . --directory src python -m unittest discover -s ../tests -p 'test_*.py' -v
```