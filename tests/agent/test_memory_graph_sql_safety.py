from sqlalchemy import or_, select

from agent.memory_graph.db.models import Path, SearchDocument, escape_like_literal
from agent.memory_graph.services.search import SearchIndexer


def test_escape_like_literal_escapes_all_like_metacharacters():
    assert escape_like_literal(r"100%_\path") == r"100\%\_\\path"


def test_prefix_lookup_uses_escaped_like_pattern(monkeypatch):
    captured = {}

    class FakeResult:
        def all(self):
            return []

    class FakeSession:
        async def execute(self, stmt):
            compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
            captured["sql"] = compiled
            return FakeResult()

    import asyncio

    svc = SearchIndexer(session_factory=lambda: None)
    asyncio.run(svc.get_node_uuids_for_prefix(FakeSession(), "core", r"用户_档案%/A\B", namespace="telegram:test"))
    sql = captured["sql"]
    assert "LIKE '用户\\_档案\\%/A\\\\B/%' ESCAPE '\\'" in sql


def test_tsvector_search_sql_uses_bound_parameters_not_interpolated_user_query():
    # The full-text branch uses SQLAlchemy text() for ranking. User-controlled
    # query/domain values must stay in bind parameters, never f-stringed into SQL.
    source = SearchIndexer.search.__code__.co_consts
    sql_chunks = "\n".join(c for c in source if isinstance(c, str))
    assert ":raw_query" in sql_chunks
    assert ":ts_query" in sql_chunks
    assert "{query}" not in sql_chunks
    assert "{domain}" not in sql_chunks
