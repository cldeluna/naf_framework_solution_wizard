"""
NAF Framework Puzzle Progress Component with Frame

Interlocking jigsaw puzzle pieces as an animated progress indicator.
Six core framework pieces sit inside a four-piece picture frame.
The frame pieces represent project-context and planning sections.

Usage:
    from puzzle_progress import (
        render_puzzle_progress, get_completion_state,
        get_frame_completion_state, PUZZLE_SECTIONS, FRAME_SECTIONS,
    )
    render_puzzle_progress(
        get_completion_state(),
        frame_completed=get_frame_completion_state(),
    )
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Section definitions — inner (framework) pieces
# ---------------------------------------------------------------------------
PUZZLE_SECTIONS = {
    "presentation":  {"label": "Presentation",  "color": "#E8B817", "row": 0, "col": 0},
    "observability": {"label": "Observability", "color": "#2ECC40", "row": 0, "col": 1},
    "orchestration": {"label": "Orchestration", "color": "#00BFFF", "row": 0, "col": 2},
    "intent":        {"label": "Intent",        "color": "#FF6B35", "row": 1, "col": 0},
    "collector":     {"label": "Collector",     "color": "#DC143C", "row": 1, "col": 1},
    "executor":      {"label": "Executor",      "color": "#7B68EE", "row": 1, "col": 2},
}

# ---------------------------------------------------------------------------
# Section definitions — frame (context / planning) pieces
# ---------------------------------------------------------------------------
FRAME_SECTIONS = {
    "problem_statement": {"label": "Problem Statement",   "color": "#A8B8C8", "position": "top"},
    "stakeholders":      {"label": "Stakeholders",        "color": "#708898", "position": "left"},
    "staffing_timeline": {"label": "Staffing & Timeline", "color": "#B0A090", "position": "right"},
    "dependencies":      {"label": "Dependencies",        "color": "#607888", "position": "bottom"},
}

# ---------------------------------------------------------------------------
# Scatter offsets — applied when pieces are NOT completed
# ---------------------------------------------------------------------------
_SCATTER = {
    # Small unique offsets — pieces stay near home slot, readable, don't pile up
    "presentation":  {"x": -20, "y": -15, "rot": -8},
    "observability": {"x": 12,  "y": -18, "rot": 6},
    "orchestration": {"x": 22,  "y": -12, "rot": -7},
    "intent":        {"x": -18, "y": 18,  "rot": 7},
    "collector":     {"x": 10,  "y": 20,  "rot": -6},
    "executor":      {"x": 20,  "y": 15,  "rot": 8},
}

_FRAME_SCATTER = {
    # Frame pieces scatter outward from their edge
    "problem_statement": {"x": 0,   "y": -30, "rot": 2},
    "stakeholders":      {"x": -30, "y": 0,   "rot": -3},
    "staffing_timeline": {"x": 30,  "y": 0,   "rot": 3},
    "dependencies":      {"x": 0,   "y": 30,  "rot": -2},
}


# ---------------------------------------------------------------------------
# Render function
# ---------------------------------------------------------------------------
def render_puzzle_progress(
    completed_sections: dict[str, bool],
    frame_completed: dict[str, bool] | None = None,
    height: int = 620,
    clickable: bool = True,
) -> None:
    """Render interlocking jigsaw puzzle with surrounding frame pieces.

    Args:
        completed_sections: dict mapping inner-piece keys to completion booleans
        frame_completed: dict mapping frame-piece keys to completion booleans
        height: pixel height for the component
        clickable: if True, clicking a piece triggers the matching Streamlit
                   button in the parent DOM
    """
    if frame_completed is None:
        frame_completed = {}

    # --- build inner-piece JSON ------------------------------------------
    pieces_js = []
    for key, info in PUZZLE_SECTIONS.items():
        done = completed_sections.get(key, False)
        s = _SCATTER[key]
        pieces_js.append(
            f'{{"key":"{key}","label":"{info["label"]}",'
            f'"color":"{info["color"]}","row":{info["row"]},"col":{info["col"]},'
            f'"done":{str(done).lower()},'
            f'"sx":{s["x"]},"sy":{s["y"]},"sr":{s["rot"]}}}'
        )
    pieces_json = "[" + ",".join(pieces_js) + "]"

    # --- build frame-piece JSON ------------------------------------------
    frame_js = []
    for key, info in FRAME_SECTIONS.items():
        done = frame_completed.get(key, False)
        s = _FRAME_SCATTER[key]
        frame_js.append(
            f'{{"key":"{key}","label":"{info["label"]}",'
            f'"color":"{info["color"]}","position":"{info["position"]}",'
            f'"done":{str(done).lower()},'
            f'"sx":{s["x"]},"sy":{s["y"]},"sr":{s["rot"]}}}'
        )
    frame_json = "[" + ",".join(frame_js) + "]"

    # --- progress counts -------------------------------------------------
    total = len(PUZZLE_SECTIONS) + len(FRAME_SECTIONS)
    done_count = (
        sum(1 for v in completed_sections.values() if v)
        + sum(1 for v in frame_completed.values() if v)
    )
    all_done = done_count == total

    # --- HTML / CSS / JS -------------------------------------------------
    html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;700&display=swap');
        .pzw {{
            font-family: 'Inter', sans-serif;
            max-width: 820px;
            margin: 0 auto;
            padding: 10px 0;
            text-align: center;
        }}
        .pzw h3 {{
            margin: 0 0 6px;
            font-size: 15px;
            color: #888;
            font-weight: 500;
        }}
        .pbar {{
            width: 55%;
            max-width: 360px;
            height: 5px;
            background: #e0e0e0;
            border-radius: 3px;
            margin: 0 auto 14px;
            overflow: hidden;
        }}
        .pfill {{
            height: 100%;
            width: {done_count / total * 100:.1f}%;
            background: linear-gradient(90deg, #2ECC40, #00BFFF);
            border-radius: 3px;
            transition: width 0.8s ease;
        }}
        .psvg {{
            width: 100%;
            max-width: 780px;
            margin: 0 auto;
        }}
        .psvg svg {{
            width: 100%;
            height: auto;
        }}
        .pg {{
            cursor: default;
            transition: transform 1.0s cubic-bezier(0.34, 1.56, 0.64, 1),
                        filter 0.4s ease,
                        opacity 0.4s ease;
        }}
        .pg.sc {{
            filter: brightness(0.7) saturate(0.45);
            opacity: 0.88;
        }}
        .pg:hover {{
            filter: brightness(1.1) drop-shadow(0 6px 16px rgba(0,0,0,0.3));
        }}
        .pg.sc:hover {{
            filter: brightness(0.85) saturate(0.6) drop-shadow(0 4px 12px rgba(0,0,0,0.25));
            opacity: 1;
        }}
        .pp {{
            stroke: rgba(0,0,0,0.2);
            stroke-width: 1.8;
            stroke-linejoin: round;
        }}
        .cmsg {{
            font-size: 15px;
            font-weight: 700;
            color: #2ECC40;
            opacity: {1 if all_done else 0};
            transition: opacity 0.6s;
            margin-top: 8px;
        }}
    </style>

    <div class="pzw">
        <h3>NAF Solution Progress &mdash; {done_count} of {total} complete</h3>
        <div class="pbar"><div class="pfill"></div></div>
        <div class="psvg">
            <svg id="pzSvg" viewBox="-160 -130 960 540" xmlns="http://www.w3.org/2000/svg"
                 style="overflow:visible;"></svg>
        </div>
        <div class="cmsg">
            {"All sections complete! Your solution design is ready." if all_done else ""}
        </div>
    </div>

    <script>
    (function() {{
        var NS = 'http://www.w3.org/2000/svg';
        var CLICKABLE = {'true' if clickable else 'false'};
        var pieces = {pieces_json};
        var framePcs = {frame_json};
        var svg = document.getElementById('pzSvg');

        /* ---- layout constants ---- */
        var W = 185, H = 90, PAD = 25, FT = 65;
        var COLS = [PAD, PAD+W, PAD+2*W];
        var ROWS = [PAD, PAD+H];
        var NZ = 14, NK = 5, NH = 8, HR = 11;
        var COL_CTRS = [PAD+W/2, PAD+W+W/2, PAD+2*W+W/2];
        var ROW_CTRS = [PAD+H/2, PAD+H+H/2];

        /* ---- inner piece edge config (with indent on outer edges for frame) ---- */
        var edges = {{
            '0,0': [-1, 1, 1, -1],
            '0,1': [-1, 1, 1, -1],
            '0,2': [-1, -1, 1, -1],
            '1,0': [-1, 1, -1, -1],
            '1,1': [-1, 1, -1, -1],
            '1,2': [-1, -1, -1, -1]
        }};

        /* ---- sign-aware jigsaw path (1 = nub out, -1 = indent) ---- */
        function jigsawPath(x, y, w, h, top, right, bottom, left) {{
            var d = 'M ' + x + ' ' + y;

            /* TOP edge */
            if (top === 0) {{
                d += ' L ' + (x+w) + ' ' + y;
            }} else {{
                var mx = x + w/2, nk = -top * NK, sw = top < 0 ? 1 : 0;
                d += ' L '+(mx-NZ)+' '+y;
                d += ' L '+(mx-NH)+' '+(y+nk);
                d += ' A '+HR+' '+HR+' 0 1 '+sw+' '+(mx+NH)+' '+(y+nk);
                d += ' L '+(mx+NZ)+' '+y;
                d += ' L '+(x+w)+' '+y;
            }}

            /* RIGHT edge */
            if (right === 0) {{
                d += ' L ' + (x+w) + ' ' + (y+h);
            }} else {{
                var my = y + h/2, nk = right * NK, sw = right > 0 ? 1 : 0;
                d += ' L '+(x+w)+' '+(my-NZ);
                d += ' L '+(x+w+nk)+' '+(my-NH);
                d += ' A '+HR+' '+HR+' 0 1 '+sw+' '+(x+w+nk)+' '+(my+NH);
                d += ' L '+(x+w)+' '+(my+NZ);
                d += ' L '+(x+w)+' '+(y+h);
            }}

            /* BOTTOM edge (right to left) */
            if (bottom === 0) {{
                d += ' L ' + x + ' ' + (y+h);
            }} else {{
                var mx = x + w/2, nk = bottom * NK, sw = bottom > 0 ? 0 : 1;
                d += ' L '+(mx+NZ)+' '+(y+h);
                d += ' L '+(mx+NH)+' '+(y+h+nk);
                d += ' A '+HR+' '+HR+' 0 1 '+sw+' '+(mx-NH)+' '+(y+h+nk);
                d += ' L '+(mx-NZ)+' '+(y+h);
                d += ' L '+x+' '+(y+h);
            }}

            /* LEFT edge (bottom to top) */
            if (left === 0) {{
                d += ' Z';
            }} else {{
                var my = y + h/2, nk = -left * NK, sw = left > 0 ? 1 : 0;
                d += ' L '+x+' '+(my+NZ);
                d += ' L '+(x+nk)+' '+(my+NH);
                d += ' A '+HR+' '+HR+' 0 1 '+sw+' '+(x+nk)+' '+(my-NH);
                d += ' L '+x+' '+(my-NZ);
                d += ' Z';
            }}
            return d;
        }}

        /* ---- frame path builders (multi-nub edges) ---- */

        function topFramePath() {{
            var x=PAD-FT, y=PAD-FT, w=3*W+2*FT, h=FT;
            var d='M '+x+' '+y;
            d+=' L '+(x+w)+' '+y;            /* top: flat */
            d+=' L '+(x+w)+' '+(y+h);        /* right: flat */
            /* bottom: right-to-left with 3 nubs DOWN */
            for(var i=COL_CTRS.length-1;i>=0;i--){{
                var mx=COL_CTRS[i];
                d+=' L '+(mx+NZ)+' '+(y+h);
                d+=' L '+(mx+NH)+' '+(y+h+NK);
                d+=' A '+HR+' '+HR+' 0 1 0 '+(mx-NH)+' '+(y+h+NK);
                d+=' L '+(mx-NZ)+' '+(y+h);
            }}
            d+=' L '+x+' '+(y+h);            /* finish bottom */
            d+=' Z';                          /* left: flat */
            return {{d:d, cx:x+w/2, cy:y+h/2}};
        }}

        function bottomFramePath() {{
            var x=PAD-FT, y=PAD+2*H, w=3*W+2*FT, h=FT;
            var d='M '+x+' '+y;
            /* top: left-to-right with 3 nubs UP */
            for(var i=0;i<COL_CTRS.length;i++){{
                var mx=COL_CTRS[i];
                d+=' L '+(mx-NZ)+' '+y;
                d+=' L '+(mx-NH)+' '+(y-NK);
                d+=' A '+HR+' '+HR+' 0 1 0 '+(mx+NH)+' '+(y-NK);
                d+=' L '+(mx+NZ)+' '+y;
            }}
            d+=' L '+(x+w)+' '+y;             /* finish top */
            d+=' L '+(x+w)+' '+(y+h);         /* right: flat */
            d+=' L '+x+' '+(y+h);             /* bottom: flat */
            d+=' Z';                           /* left: flat */
            return {{d:d, cx:x+w/2, cy:y+h/2}};
        }}

        function leftFramePath() {{
            var x=PAD-FT, y=PAD, w=FT, h=2*H;
            var d='M '+x+' '+y;
            d+=' L '+(x+w)+' '+y;             /* top: flat */
            /* right: top-to-bottom with 2 nubs RIGHT */
            for(var i=0;i<ROW_CTRS.length;i++){{
                var my=ROW_CTRS[i];
                d+=' L '+(x+w)+' '+(my-NZ);
                d+=' L '+(x+w+NK)+' '+(my-NH);
                d+=' A '+HR+' '+HR+' 0 1 1 '+(x+w+NK)+' '+(my+NH);
                d+=' L '+(x+w)+' '+(my+NZ);
            }}
            d+=' L '+(x+w)+' '+(y+h);         /* finish right */
            d+=' L '+x+' '+(y+h);             /* bottom: flat */
            d+=' Z';                           /* left: flat */
            return {{d:d, cx:x+w/2, cy:y+h/2}};
        }}

        function rightFramePath() {{
            var x=PAD+3*W, y=PAD, w=FT, h=2*H;
            var d='M '+x+' '+y;
            d+=' L '+(x+w)+' '+y;             /* top: flat */
            d+=' L '+(x+w)+' '+(y+h);         /* right: flat */
            d+=' L '+x+' '+(y+h);             /* bottom: flat */
            /* left: bottom-to-top with 2 nubs LEFT */
            for(var i=ROW_CTRS.length-1;i>=0;i--){{
                var my=ROW_CTRS[i];
                d+=' L '+x+' '+(my+NZ);
                d+=' L '+(x-NK)+' '+(my+NH);
                d+=' A '+HR+' '+HR+' 0 1 1 '+(x-NK)+' '+(my-NH);
                d+=' L '+x+' '+(my-NZ);
            }}
            d+=' Z';
            return {{d:d, cx:x+w/2, cy:y+h/2}};
        }}

        var frameFns = {{
            top: topFramePath,
            bottom: bottomFramePath,
            left: leftFramePath,
            right: rightFramePath
        }};

        /* ---- icon helper ---- */
        function addIcon(parent, svgStr, tx, ty) {{
            var g = document.createElementNS(NS, 'g');
            g.setAttribute('transform', 'translate('+tx+','+ty+')');
            var tmp = document.createElementNS(NS, 'svg');
            tmp.innerHTML = svgStr;
            while (tmp.firstChild) g.appendChild(tmp.firstChild);
            parent.appendChild(g);
        }}

        /* ---- icon templates ---- */
        var ICONS = {{
            presentation: '<rect x="-11" y="-9" width="22" height="14" rx="1.5" fill="none" stroke="#1a1a1a" stroke-width="1.6"/><line x1="-3" y1="5" x2="-5" y2="9" stroke="#1a1a1a" stroke-width="1.5"/><line x1="3" y1="5" x2="5" y2="9" stroke="#1a1a1a" stroke-width="1.5"/><line x1="-6" y1="9" x2="6" y2="9" stroke="#1a1a1a" stroke-width="1.5"/>',
            observability: '<circle cx="-2" cy="-2" r="6" fill="none" stroke="#1a1a1a" stroke-width="1.6"/><line x1="2.3" y1="2.3" x2="8" y2="8" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round"/>',
            orchestration: '<circle cx="0" cy="-7" r="3" fill="#1a1a1a"/><circle cx="-9" cy="5" r="3" fill="#1a1a1a"/><circle cx="9" cy="5" r="3" fill="#1a1a1a"/><line x1="0" y1="-4" x2="-7" y2="3" stroke="#1a1a1a" stroke-width="1.5"/><line x1="0" y1="-4" x2="7" y2="3" stroke="#1a1a1a" stroke-width="1.5"/>',
            intent: '<path d="M0,-10 L10,0 L0,10 L-10,0 Z" fill="none" stroke="#1a1a1a" stroke-width="1.6"/><path d="M0,-5 L5,0 L0,5 L-5,0 Z" fill="none" stroke="#1a1a1a" stroke-width="1.1" stroke-dasharray="2,2"/>',
            collector: '<path d="M0,-10 L6,-3 L-6,-3 Z" fill="#1a1a1a" opacity="0.8"/><path d="M0,-4 L8,4 L-8,4 Z" fill="#1a1a1a" opacity="0.65"/><path d="M0,2 L9,10 L-9,10 Z" fill="#1a1a1a" opacity="0.5"/>',
            executor: '<path d="M-8,-8 L0,-2 L8,-8" fill="none" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M-8,-2 L0,4 L8,-2" fill="none" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M-8,4 L0,10 L8,4" fill="none" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
        }};

        /* ---- click helper ---- */
        function wireClick(g, label) {{
            if (!CLICKABLE) return;
            g.style.cursor = 'pointer';
            g.addEventListener('click', function() {{
                try {{
                    var btns = window.parent.document.querySelectorAll(
                        'button[kind="secondary"], button[kind="primary"]');
                    for (var b = 0; b < btns.length; b++) {{
                        var txt = btns[b].textContent.trim();
                        if (txt === label || txt.endsWith(' ' + label)) {{
                            btns[b].click();
                            return;
                        }}
                    }}
                }} catch(e) {{}}
            }});
        }}

        /* ============================================================
         *  RENDER FRAME PIECES  (behind inner pieces)
         * ============================================================ */
        framePcs.forEach(function(fp) {{
            var info = frameFns[fp.position]();
            var g = document.createElementNS(NS, 'g');
            g.classList.add('pg');
            if (!fp.done) g.classList.add('sc');

            var path = document.createElementNS(NS, 'path');
            path.setAttribute('d', info.d);
            path.setAttribute('fill', fp.color);
            path.classList.add('pp');
            g.appendChild(path);

            /* label */
            var label = document.createElementNS(NS, 'text');
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('font-family', 'Inter, system-ui, sans-serif');
            label.setAttribute('font-weight', '700');
            label.setAttribute('fill', '#ffffff');
            label.setAttribute('letter-spacing', '1.5');
            label.setAttribute('pointer-events', 'none');
            label.setAttribute('paint-order', 'stroke');
            label.setAttribute('stroke', 'rgba(0,0,0,0.3)');
            label.setAttribute('stroke-width', '2.5');

            if (fp.position === 'left' || fp.position === 'right') {{
                /* vertical text */
                var rot = fp.position === 'left' ? -90 : 90;
                label.setAttribute('font-size', '12');
                label.setAttribute('x', info.cx);
                label.setAttribute('y', info.cy);
                label.setAttribute('dominant-baseline', 'central');
                label.setAttribute('transform',
                    'rotate('+rot+','+info.cx+','+info.cy+')');
            }} else {{
                /* horizontal text */
                label.setAttribute('font-size', '13');
                label.setAttribute('x', info.cx);
                label.setAttribute('y', info.cy + 4);
                label.setAttribute('dominant-baseline', 'central');
            }}
            label.textContent = fp.label.toUpperCase();
            g.appendChild(label);

            /* check mark */
            if (fp.done) {{
                var chk = document.createElementNS(NS, 'text');
                if (fp.position === 'top' || fp.position === 'bottom') {{
                    chk.setAttribute('x', info.cx + 280);
                    chk.setAttribute('y', info.cy + 5);
                }} else {{
                    chk.setAttribute('x', info.cx);
                    chk.setAttribute('y', fp.position === 'left' ? info.cy - 70 : info.cy + 75);
                }}
                chk.setAttribute('text-anchor', 'middle');
                chk.setAttribute('font-size', '13');
                chk.setAttribute('fill', '#1a1a1a');
                chk.setAttribute('pointer-events', 'none');
                chk.textContent = '\\u2713';
                g.appendChild(chk);
            }}

            /* scatter / snap */
            g.style.transformOrigin = info.cx + 'px ' + info.cy + 'px';
            if (fp.done) {{
                g.style.transform = 'translate(0,0) rotate(0deg)';
            }} else {{
                g.style.transform = 'translate('+fp.sx+'px,'+fp.sy+'px) rotate('+fp.sr+'deg)';
            }}

            wireClick(g, fp.label);
            svg.appendChild(g);
        }});

        /* ============================================================
         *  RENDER INNER PIECES  (on top of frame)
         * ============================================================ */
        pieces.forEach(function(p) {{
            var key = p.row + ',' + p.col;
            var e = edges[key];
            var bx = COLS[p.col], by = ROWS[p.row];
            var pathD = jigsawPath(bx, by, W, H, e[0], e[1], e[2], e[3]);

            var g = document.createElementNS(NS, 'g');
            g.classList.add('pg');
            if (!p.done) g.classList.add('sc');

            var path = document.createElementNS(NS, 'path');
            path.setAttribute('d', pathD);
            path.setAttribute('fill', p.color);
            path.classList.add('pp');
            g.appendChild(path);

            var cx = bx + W/2;
            var cy = by + H/2;

            if (ICONS[p.key]) {{
                addIcon(g, ICONS[p.key], cx, cy - 10);
            }}

            var label = document.createElementNS(NS, 'text');
            label.setAttribute('x', cx);
            label.setAttribute('y', cy + 18);
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('font-family', 'Inter, system-ui, sans-serif');
            label.setAttribute('font-size', '12');
            label.setAttribute('font-weight', '700');
            label.setAttribute('fill', '#1a1a1a');
            label.setAttribute('letter-spacing', '1');
            label.setAttribute('pointer-events', 'none');
            label.textContent = p.label.toUpperCase();
            g.appendChild(label);

            if (p.done) {{
                var chk = document.createElementNS(NS, 'text');
                chk.setAttribute('x', bx + W - 10);
                chk.setAttribute('y', by + 16);
                chk.setAttribute('font-size', '13');
                chk.setAttribute('fill', '#1a1a1a');
                chk.setAttribute('pointer-events', 'none');
                chk.textContent = '\\u2713';
                g.appendChild(chk);
            }}

            g.style.transformOrigin = cx + 'px ' + cy + 'px';
            if (p.done) {{
                g.style.transform = 'translate(0,0) rotate(0deg)';
            }} else {{
                g.style.transform = 'translate('+p.sx+'px,'+p.sy+'px) rotate('+p.sr+'deg)';
            }}

            wireClick(g, p.label);
            svg.appendChild(g);
        }});
    }})();
    </script>
    """

    st.iframe(html, height=height)


# ---------------------------------------------------------------------------
# Completion checks — inner (framework) pieces
# ---------------------------------------------------------------------------
def check_section_completion(section_key: str) -> bool:
    """Check if a wizard section has meaningful data in session_state."""
    ss = st.session_state

    def _any_checked(prefix):
        return any(v for k, v in ss.items() if k.startswith(prefix) and v is True)

    checks = {
        "presentation": lambda: _any_checked("pres_user_") or _any_checked("pres_tool_"),
        "observability": lambda: _any_checked("obs_state_") or _any_checked("obs_tool_") or bool(ss.get("obs_go_no_go")),
        "orchestration": lambda: bool(ss.get("orch_choice")) and ss.get("orch_choice") not in ("Select...", "— Select one —", ""),
        "intent": lambda: _any_checked("intent_dev_") or _any_checked("intent_prov_"),
        "collector": lambda: _any_checked("collector_method_") or _any_checked("collector_auth_"),
        "executor": lambda: _any_checked("exec_"),
    }

    checker = checks.get(section_key)
    if checker:
        try:
            return checker()
        except Exception:
            return False
    return False


def get_completion_state() -> dict[str, bool]:
    """Get the current completion state for all puzzle sections."""
    return {key: check_section_completion(key) for key in PUZZLE_SECTIONS}


# ---------------------------------------------------------------------------
# Completion checks — frame (context / planning) pieces
# ---------------------------------------------------------------------------
def check_frame_completion(section_key: str) -> bool:
    """Check if a frame section has meaningful data in session_state."""
    ss = st.session_state

    def _any_checked(prefix):
        return any(v for k, v in ss.items() if k.startswith(prefix) and v is True)

    checks = {
        "problem_statement": lambda: (
            (bool(ss.get("_wizard_automation_title", "").strip())
             and ss.get("_wizard_automation_title") != "My new network automation project")
            or bool(ss.get("_wizard_problem_statement", "").strip())
        ),
        "stakeholders": lambda: (
            bool(ss.get("stakeholders_choices"))  # non-empty dict
            or bool(ss.get("stakeholders_other_text", "").strip())
        ),
        "dependencies": lambda: _any_checked("dep_"),
        "staffing_timeline": lambda: (
            bool(ss.get("timeline_milestones"))  # has milestone rows
            or (ss.get("timeline_staff_count") or 0) > 0
            or (ss.get("timeline_external_staff_count") or 0) > 0
            or bool(ss.get("timeline_staffing_plan", "").strip())
        ),
    }

    checker = checks.get(section_key)
    if checker:
        try:
            return checker()
        except Exception:
            return False
    return False


def get_frame_completion_state() -> dict[str, bool]:
    """Get the current completion state for all frame sections."""
    return {key: check_frame_completion(key) for key in FRAME_SECTIONS}
