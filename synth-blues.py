from asciimidi import play, Config
from note_util import stack, concat, make_lines, n, set_key

TUNING = """
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
C3 == == == == == == ==
"""

def shuffle_bar(p0, p1, p2, p3):
    return f"{p1:3} {p0:3} {p2:3} {p0:3} {p3:3} {p0:3} {p2:3} {p0:3}"

def bass_bar(p0, p1, p2, p3):
    return f"{p0:3} === {p1:3} === {p2:3} === {p3:3} ==="

def horn_bar(p0, p1):
    return f"""
{p1:3} --- {p1:3} {p1:3} --- {p1:3} === ---
{p0:3} --- {p0:3} {p0:3} --- {p0:3} === ---
"""

def horn_bar2(i, v, vii):
    return f"""
{v:3} === --- {vii:3} {vii:3} === --- ---
{i:3} === --- {i:3} {i:3} === --- ---
"""

def lead_bar(p0, p1, p2):
    return f"--- --- --- --- --- {p0:3} {p1:3} {p2:3}"

def song2():
    r = n("A2", "A minor")

    i = r-14
    iv = i+3
    v = i+4
    i_bass = [bass_bar(i, i+4, i+"M6", i+6)]
    iv_bass = [bass_bar(iv, iv+4, iv+"M6", iv+6)]
    v_bass = [bass_bar(v, v+4, v+"M6", v+6)]

    i = r+7
    iv = i - 4
    v = i - 3
    i_horn = [horn_bar2(i, i+4, i+6)]
    iv_horn = [horn_bar2(iv, iv+4, iv+6)]
    v_horn = [horn_bar2(v, v+4, v+6)]

    i = r
    iv = i + 3
    v = i + 4
    i_lead = [lead_bar(i+4, i+3, i+2)]
    iv_lead = [lead_bar(iv-4, iv-3, iv-1)]
    v_lead = [lead_bar(v-4, v-2, v-1)]

    i_bar_into_i = [stack(i_lead + i_horn + i_bass)]
    i_bar_into_iv = [stack(iv_lead + i_horn + i_bass)]
    i_bar_into_v = [stack(v_lead + i_horn + i_bass)]
    iv_bar_into_iv = [stack(iv_lead + iv_horn + iv_bass)]
    iv_bar_into_i = [stack(i_lead + iv_horn + iv_bass)]
    v_bar_into_iv = [stack(iv_lead + v_horn + v_bass)]

    bars = i_bar_into_i + i_bar_into_i + i_bar_into_i + i_bar_into_iv +\
           iv_bar_into_iv + iv_bar_into_i + i_bar_into_i + i_bar_into_v +\
           v_bar_into_iv + iv_bar_into_i + i_bar_into_i + i_bar_into_i

    return make_lines(bars * 4)

play(song2(), Config(beats_per_minute=82, note_width=.75, swing=.7))

#play([TUNING], Config(beats_per_minute=10, loops=10))
