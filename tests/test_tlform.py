import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import tlform  # noqa: E402

SP = {"トウヤ": "Touya", "ヤマト": "Yamato"}


def test_wrap_dialogue_pages():
    e = {"id": "sce001:00010", "jp": "トウヤ「あ{nl}　い」", "style": 0}
    en = "Touya: " + " ".join(["word"] * 40)
    lines = tlform.layout(e, en * 2).split("{nl}")
    assert len(lines) > 3
    assert all(tlform.width(x) <= tlform.DLG_W for x in lines)
    assert all(tlform.width(x) <= tlform.PAGE_LAST_W for x in lines[2::3])   # page arrow column stays free
    assert " ".join(lines) == en * 2


def test_wrap_balanced_no_stub():
    s = "Koichiro: She's coming over here... Come on, Touya... ...Don't say I didn't warn you~"
    lines = tlform.wrap(s + " " + s, 240, 224)
    assert lines[2].endswith("you~") and len(lines) == 5, lines   # the page ends on a sentence, not mid-sentence
    assert min(map(tlform.width, lines)) >= 120, lines            # balanced, no stub line
    assert tlform.wrap("one  two", 240) == ["one  two"]
    assert tlform.wrap("", 240) == [""]


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
    assert tlform.check(b, "{ctl:0041}Touya: " + "x " * 100 + "{page}", SP)[0]
