"""
This module tests the clean_ids.py script.
"""

import sys
import io
import platform
import pytest
import requests
from bin.clean_ids import main


def test_script_execution(monkeypatch, capsys):
    """
    Test clean_ids.py script execution with mock input.
    """
    # 1. Simulate the standard input data
    # We use io.StringIO to make a string act like a readable stream/file
    fake_input = io.StringIO("kcFsuxaJ1es\nasd123\n")
    monkeypatch.setattr(sys, "stdin", fake_input)

    # 2. Run the script's main logic
    main()

    # 3. Capture the printed output
    captured = capsys.readouterr()

    # 4. Assert that the data was modified correctly
    assert captured.out == "kcFsuxaJ1es\n"

@pytest.mark.parametrize("test_input, expected_output",[
    ("yV4jyj8Hr1g\nl25VwzGQhvo\no9g49L-MmeE\nclaire\nL-fK_BUmesc\n",
    "yV4jyj8Hr1g\nl25VwzGQhvo\no9g49L-MmeE\nL-fK_BUmesc\n"),
    ("hello!!\nlivelaughlove\n321blastoff!\n", ""),
    ("yV4jyj8Hr1g\nl25VwzGQhvo\no9g49L-MmeE\n", "yV4jyj8Hr1g\nl25VwzGQhvo\no9g49L-MmeE\n")
])
def test_sequence_of_ids(monkeypatch, capsys, test_input, expected_output):
    """
    Use a parameterized test to evaluate different sequences of IDs.
    """
    fake_input = io.StringIO(test_input)
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == expected_output

def test_throw_errors(monkeypatch):
    """
    Test exception handling.
    """
    fake_input = io.StringIO("kcFsuxaJ1es\nasd123\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() raised an unexpected exception: {e}")

def test_id_length():
    """
    Test that the correct length is evaluated for a YouTube ID.
    """
    valid_id = "yV4jyj8Hr1g"
    assert len(valid_id) == 11 # valid ids are 11 characters long

def test_all_special_chars_id(monkeypatch, capsys):
    """
    Test that a completely special character ID would not be deemed legitimate.
    """
    all_spec_char_id = io.StringIO( "!!!!@@@**$$\n")
    monkeypatch.setattr(sys, "stdin", all_spec_char_id)
    main()
    captured = capsys.readouterr()
    assert captured.out == ""

def test_os_is_ubuntu():
    """
    Test system OS.
    """
    assert platform.system() == "Linux"


def test_python_version():
    """
    Test python version.
    """
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 12

@pytest.mark.skip(reason="Live-video existence checking not yet implemented; "
                          "clean_ids.py only validates ID format, not video existence")
def test_url_is_valid(monkeypatch, capsys):
    """
    Placeholder for potential feature: verify that a format-valid YouTube ID
    also corresponds to a currently live video, via a real HTTP request.
    Currently skipped because clean_ids.py has no such check, and this test
    would require a live network call (requests.get) against YouTube,
    which is unsuitable for a unit test (external dependency).
    """
    fake_input = io.StringIO("kcFsuxaJ1es\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    url = f"https://www.youtube.com/watch?v={captured.out.strip()}"
    response = requests.get(url, timeout=5)
    assert response.status_code == 200

@pytest.mark.xfail(reason="non-current python version")
def test_old_python_version():
    """
    Test that python version is not 3.11 or lower.
    """
    assert sys.version_info.minor <= 11 # expect to fail since we are using the most recent version of python
