import pytest
import main


def test_extract_fromDB():
    db = main.extract_fromDB("subjects", "name")
    api = main.extract_fromAPI("subject")
    assert db <= api


def test_extract_fromAPI():
    bd = main.extract_fromDB("measures", "unit")
    api = main.extract_fromAPI("unit")
    assert set(bd).issubset(set(api))


def test_query_OK(monkeypatch):

    monkeypatch.setattr("sys.argv", ["main.py"])
    with pytest.raises(SystemExit) as ex_info:
        main.query()
    assert (
        ex_info.value.code.strip()
        == "Provide at least one argument to specify the run mode"
    )

    monkeypatch.setattr("sys.argv", ["main.py", "--shell"])
    with pytest.raises(SystemExit) as ex_info:
        main.query()
    assert (
        ex_info.value.code.strip()
        == "Shell mode requires additional arguments, at least two more (for the query type and for the artefact/context)"
    )

    monkeypatch.setattr("sys.argv", ["main.py", "--shell", "data"])
    with pytest.raises(SystemExit) as ex_info:
        main.query()
    assert ex_info.value.code.strip().startswith(
        "For data queries, 6 more arguments needed after the query type:"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--shell",
            "data",
            "flow",
            "NAD",
            "@DF_NAAG_I",
            "+",
            "*",
            "ge:2018+le:2024",
        ],
    )
    with pytest.raises(SystemExit) as ex_info:
        main.query()
    assert ex_info.value.code.strip().startswith(
        'Caught an exception: "Something went wrong! Status code:'
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--shell",
            "data",
            "dataflow",
            "OECD.SDD.NAD",
            "DSD_NAAG@DF_NAAG_I",
            "+",
            "*",
            "c[TIME_PERIOD]=ge:2018+le:2024",
        ],
    )
    assert main.query() is None
