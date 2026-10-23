import pytest

from salestools.report import load_gz, read_csv, save_gz, summarize


class TestFiles:
    def setup_method(self):
        self.files = []

    def teardown_method(self):
        for path in self.files:
            path.unlink(missing_ok=True)

    def test_csv(self, tmp_path):
        path = tmp_path / "a.csv"
        path.write_text("a,b\n1,2\n", encoding="utf-8")
        assert read_csv(path) == [{"a": "1", "b": "2"}]

    def test_gz_roundtrip(self, tmp_path):
        out = save_gz({"x": [1, 2]}, tmp_path / "sub" / "x.json.gz")
        self.files.append(out)
        assert load_gz(out) == {"x": [1, 2]}


@pytest.mark.parametrize(
    "amounts, expected",
    [
        ([10, 20, 30], {"count": 3, "total": 60, "mean": 20, "median": 20}),
        ([1, 2, 3, 4], {"count": 4, "total": 10, "mean": 2.5, "median": 2.5}),
    ],
)
def test_summarize(amounts, expected):
    assert summarize(amounts) == expected


def test_summarize_empty():
    with pytest.raises(ValueError):
        summarize([])
