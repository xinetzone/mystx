import copy
import importlib.util

from mystx.utils import deep_merge, has_module


def test_deep_merge_nested_2level():
    base = {"a": {"b": 1}}
    override = {"a": {"c": 2}}
    result = deep_merge(base, override)
    assert result == {"a": {"b": 1, "c": 2}}


def test_deep_merge_remove_marker_none_deletes_key():
    base = {"a": 1, "b": 2}
    override = {"b": None, "c": 3}
    result = deep_merge(base, override, remove_marker=None)
    assert result == {"a": 1, "c": 3}


def test_deep_merge_preserves_base_unmutated():
    base = {"a": {"b": 1}}
    backup = copy.deepcopy(base)
    deep_merge(base, {"a": {"c": 2}})
    assert base == backup


def test_has_module_vs_find_spec():
    expected = importlib.util.find_spec("myst_parser") is not None
    assert has_module("myst_parser") == expected


def test_deep_merge_flat_override():
    base = {"x": 1, "y": 2}
    override = {"y": 99, "z": 3}
    result = deep_merge(base, override)
    assert result == {"x": 1, "y": 99, "z": 3}


def test_has_module_absent_returns_false():
    assert has_module("___definitely_not_a_real_module_xyz___") is False
