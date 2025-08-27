"""Command line entry point for running the Smith chart GUI."""

try:  # support running via ``python src/smithpy/__main__.py``
    from .app import main
except ImportError:  # pragma: no cover - direct execution fallback
    from app import main

if __name__ == "__main__":
    main()
