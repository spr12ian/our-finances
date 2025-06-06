This project uses the `src/` layout to store all Python packages and modules.

Benefits:
- Prevents accidental imports from the current working directory
- Keeps project structure clean and modular
- Plays well with tools like `pytest`, `mypy`, and `setuptools`
- Mirrors the environment of an installed package

This layout is a best practice in modern Python development, especially for projects with scripts, notebooks, tests, and packages.
