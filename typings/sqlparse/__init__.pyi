from typing import Any

# Token types
Tokenlist = Any  # We can refine this if needed
Statement = Any  # sqlparse.sql.Statement if we define its structure

def split(sql: str) -> list[str]: ...
def format(
    sql: str,
    keyword_case: str | None = ...,
    identifier_case: str | None = ...,
    strip_comments: bool = ...,
    reindent: bool = ...,
    output_format: str | None = ...,
    indent_width: int = ...,
    indent_columns: bool = ...,
    indent_after_first: bool = ...,
    wrap_after: int = ...,
    comma_first: bool = ...,
    use_space_around_operators: bool = ...,
) -> str: ...
def parse(sql: str) -> list[Statement]: ...
def is_keyword(token: str) -> bool: ...
def is_identifier(token: str) -> bool: ...

# Tokenizer helpers (commonly used in diagnostics or low-level parsing)
def reformat(sql: str, **options: Any) -> str: ...
def _tokenize(sql: str) -> list[Tokenlist]: ...
