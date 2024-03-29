import pytest


def test_empty_slap():
    assert ...


def test_single_slaps():
    assert ...
    assert ...


# @pytest.mark.parametrize("test_input,expected", [
#     ('ll', LikeState.empty),
#     ('dd', LikeState.empty),
#     ('ld', LikeState.disliked),
#     ('dl', LikeState.liked),
#     ('ldd', LikeState.empty),
#     ('lldd', LikeState.empty),
#     ('ddl', LikeState.liked),
# ])
# def test_multi_slaps(test_input, expected):
#     assert slap_many(LikeState.empty, test_input) is expected


@pytest.mark.skip(reason="regexes not supported yet")
def test_regex_slaps():
    assert ...


@pytest.mark.xfail
def test_divide_by_zero():
    assert 1 / 0 == 1


def test_invalid_slap():
    with pytest.raises(ValueError):
        raise ValueError


@pytest.mark.xfail
def test_db_slap(db_conn):
    db_conn.read_slaps()
    assert ...


def test_print(capture_stdout):
    print("hello")
    assert capture_stdout["stdout"] == "hello\n"
