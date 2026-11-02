import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import tlform  # noqa: E402

SP = {"トウヤ": "Touya", "ヤマト": "Yamato"}


def test_wrap_dialogue_pages():
    e = {"id": "sce001:00010", "jp": "トウヤ「あ{nl}　い」", "style": 0}
    en = "Touya: " + " ".join(["word"] * 40)
    lines = tlform.layout(e, en).split("{nl}")
    assert all(len(x) <= 30 for x in lines)
    assert all(len(x) <= 28 for x in lines[2::3])     # last line of each page leaves the arrow column
    assert " ".join(lines) == en


def test_check_speaker_codes_and_ascii():
    e = {"id": "sce001:00010", "jp": "トウヤ「あ{ctl:3C3E}い」{page}ヤマト（う）", "style": 0}
    assert tlform.check(e, "Touya: Ah{ctl:3C3E} hey{page}Yamato: (Hm.)", SP) == ([], [])
    errs, _ = tlform.check(e, "Toya: Ah hey{page}Yamato: Hm.", SP)
    assert any("Touya" in x for x in errs) and any("control codes" in x for x in errs)
    assert any("'('" in x for x in errs)
    errs, _ = tlform.check(e, "Touya: Ah{ctl:3C3E} …{page}Yamato: (Hm.)", SP)
    assert any("non-ASCII" in x for x in errs)


def test_choice_and_battle():
    c = {"id": "sce003:03BA5", "jp": "　やり過ごす{nl}　攻撃する", "style": 128}
    assert tlform.layout(c, "Let it pass{nl}Attack") == " Let it pass{nl} Attack"
    assert tlform.check(c, "Let it pass", SP)[0]
    b = {"id": "bm000:0065", "jp": "{ctl:0041}トウヤ「当たるかっ！」{page}"}
    assert tlform.check(b, "{ctl:0041}Touya: Like that'll hit me!{page}", SP) == ([], [])
    assert tlform.check(b, "{ctl:0041}Touya: " + "x " * 60 + "{page}", SP)[0]
