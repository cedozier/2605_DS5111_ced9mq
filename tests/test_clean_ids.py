import sys
import io
import pytest
from clean_ids import main
import platform


def test_script_execution(monkeypatch, capsys):
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
    ("yV4jyj8Hr1g\nl25VwzGQhvo\no9g49L-MmeE\nclaire\nL-fK_BUmesc\n", "yV4jyj8Hr1g\nl25VwzGQhvo\no9g49L-MmeE\nL-fK_BUmesc\n"),
    ("hello!!\nlivelaughlove\n321blastoff!\n", ""),
    ("yV4jyj8Hr1g\nl25VwzGQhvo\no9g49L-MmeE\n", "yV4jyj8Hr1g\nl25VwzGQhvo\no9g49L-MmeE\n")
])
def test_sequence_of_ids(monkeypatch, capsys, test_input, expected_output):
    fake_input = io.StringIO(test_input)
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == expected_output


def test_id_length():
    valid_id = "yV4jyj8Hr1g"
    assert len(valid_id) == 11 # valid ids are 11 characters long

def test_all_special_chars_id(monkeypatch, capsys):
    all_spec_char_id = io.StringIO( "!!!!@@@**$$\n")
    monkeypatch.setattr(sys, "stdin", all_spec_char_id)
    main()
    captured = capsys.readouterr()
    assert captured.out == ""

def test_os_is_ubuntu():
    assert platform.system() == "Linux"


def test_python_version():
    assert sys.version_info.major == 3
    assert sys.version_info.minor == 14

@pytest.mark.skip(reason="URL validation not yet been implemented")
def test_url_is_valid():
    fake_input = io.StringIO("kcFsuxaJ1es\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    url = f"https://www.youtube.com/watch?v={captured.out.strip()}"
    assert requests.get(url).status_code == 200
