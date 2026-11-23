"""mystx.parallel 的单元测试：覆写表语义与 fail-fast 守卫的触发条件。"""
from unittest.mock import MagicMock

import pytest

from mystx.parallel import (
    GUARD_EVENT,
    apply_parallel_safe_overrides,
    assert_parallel_ready,
    connect_parallel_guard,
    find_parallel_blockers,
)


def _ext(read_safe=None, write_safe=None):
    return MagicMock(parallel_read_safe=read_safe, parallel_write_safe=write_safe)


def _app(extensions: dict | None = None, parallel: int = 0, allowed: bool = True):
    app = MagicMock()
    app.extensions = dict(extensions or {})
    app.parallel = parallel
    app.is_parallel_allowed.return_value = allowed
    return app


def test_apply_overrides_sets_flags_on_loaded_extension():
    ext = _ext(read_safe=None, write_safe=None)
    app = _app({"third.party": ext})

    applied = apply_parallel_safe_overrides(app, {"third.party": (True, True)})

    assert applied == ["third.party"]
    assert ext.parallel_read_safe is True
    assert ext.parallel_write_safe is True


def test_apply_overrides_coerces_to_bool_and_honours_false():
    ext = _ext(read_safe=True, write_safe=True)
    app = _app({"third.party": ext})

    apply_parallel_safe_overrides(app, {"third.party": (False, False)})

    assert ext.parallel_read_safe is False
    assert ext.parallel_write_safe is False


def test_apply_overrides_skips_unknown_extension():
    """覆写表可跨项目复用：表中有、当前未加载的扩展名应被静默跳过。"""
    app = _app({})

    applied = apply_parallel_safe_overrides(app, {"not.loaded": (True, True)})

    assert applied == []


def test_find_parallel_blockers_reports_only_non_true():
    app = _app(
        {
            "ok": _ext(read_safe=True, write_safe=True),
            "missing": _ext(read_safe=None, write_safe=None),
            "explicit_false": _ext(read_safe=False, write_safe=True),
        }
    )

    assert find_parallel_blockers(app) == ["missing", "explicit_false"]


def test_guard_is_noop_for_serial_build():
    """纯串行构建（parallel==0）不得被守卫打扰。"""
    app = _app({"blocker": _ext()}, parallel=0, allowed=False)

    assert assert_parallel_ready(app) is None


def test_guard_is_noop_when_parallel_allowed():
    app = _app({"ok": _ext(True, True)}, parallel=4, allowed=True)

    assert assert_parallel_ready(app) is None


def test_guard_raises_and_names_blockers():
    app = _app({"blocker": _ext(None, None)}, parallel=4, allowed=False)

    with pytest.raises(RuntimeError) as excinfo:
        assert_parallel_ready(app)

    assert "blocker" in str(excinfo.value)


def test_connect_guard_applies_overrides_then_connects():
    ext = _ext(None, None)
    app = _app({"third.party": ext})

    applied = connect_parallel_guard(app, {"third.party": (True, True)})

    assert applied == ["third.party"]
    app.connect.assert_called_once_with(GUARD_EVENT, assert_parallel_ready)


def test_connect_guard_without_overrides_still_connects():
    app = _app({})

    applied = connect_parallel_guard(app)

    assert applied == []
    app.connect.assert_called_once_with(GUARD_EVENT, assert_parallel_ready)
