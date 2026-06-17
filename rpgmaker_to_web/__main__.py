"""Allow `python -m rpgmaker_to_web ...`."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
