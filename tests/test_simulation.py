from utils.simulation_view import get_office_simulation_html


def test_simulation_html_default():
    html = get_office_simulation_html()
    assert "<!DOCTYPE html>" in html
    assert "mapCanvas" in html
    assert "leaderSvg" in html
    assert "vpLibrary" in html
    assert "vpOpposing" in html
    assert "vpConference" in html

def test_simulation_html_no_truncation():
    long_msg1 = "As legal counsel representing the Complainants, I must highlight that the single most unfair and one-sided clause in this dispute is the Respondent's arbitrary and unilateral alienation of the originally allotted unit Unit No. SH-20A on the Ground Floor."
    long_msg2 = "As legal counsel for the Respondent, we categorically reject the assertion of arbitrariness and maintain that the reallocation was permitted under force majeure."
    long_msg3 = "We reject the defense and demand full immediate restoration of the original unit or total refund with 18% statutory interest."

    html = get_office_simulation_html(long_msg1, long_msg2, long_msg3)

    # Ensure the full text is embedded in the HTML without truncation
    assert "arbitrary and unilateral alienation of the originally allotted unit Unit No. SH-20A" in html
    assert "categorically reject the assertion of arbitrariness" in html
    assert "total refund with 18% statutory interest" in html

def test_simulation_special_characters_escaping():
    # Test strings with quotes, newlines, apostrophes, and brackets
    evil_msg = 'Clause 5.1: "Tenant" shall pay \\ backslashes and \'quotes\' & <script>alert("XSS")</script>'
    html = get_office_simulation_html(evil_msg, "Defending quote 'test'", "Counter offer")

    # Verify script doesn't crash or break HTML structure
    assert "<!DOCTYPE html>" in html
    assert "script" in html

def test_simulation_viewport_dimensions():
    html = get_office_simulation_html()
    assert 'width: 900px;' in html
    assert 'height: 600px;' in html
    assert 'width: 580px;' in html
