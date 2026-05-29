"""
NAF Framework Puzzle Progress Component

Interlocking jigsaw puzzle pieces as an animated progress indicator.
Each piece has classic mushroom-shaped nubs and matching indents.
Icons match the NAF Framework architecture diagram.

Usage:
    from puzzle_progress import render_puzzle_progress, get_completion_state
    render_puzzle_progress(get_completion_state())
"""

import streamlit as st
import streamlit.components.v1 as components

# Section definitions with colors matching the NAF framework legend
PUZZLE_SECTIONS = {
    "presentation":  {"label": "Presentation",  "color": "#E8B817", "row": 0, "col": 0},
    "observability": {"label": "Observability", "color": "#2ECC40", "row": 0, "col": 1},
    "orchestration": {"label": "Orchestration", "color": "#00BFFF", "row": 0, "col": 2},
    "intent":        {"label": "Intent",        "color": "#FF6B35", "row": 1, "col": 0},
    "collector":     {"label": "Collector",     "color": "#DC143C", "row": 1, "col": 1},
    "executor":      {"label": "Executor",      "color": "#7B68EE", "row": 1, "col": 2},
}

_SCATTER = {
    "presentation":  {"x": -80,  "y": 15,   "rot": -12},
    "observability": {"x": 30,   "y": -45,  "rot": 8},
    "orchestration": {"x": 110,  "y": -35,  "rot": -10},
    "intent":        {"x": -65,  "y": 35,   "rot": 10},
    "collector":     {"x": 50,   "y": 40,   "rot": -12},
    "executor":      {"x": 140,  "y": 30,   "rot": 8},
}


def render_puzzle_progress(
    completed_sections: dict[str, bool],
    height: int = 520,
    clickable: bool = True,
) -> None:
    """Render interlocking jigsaw puzzle progress widget.

    Args:
        completed_sections: dict mapping section keys to completion booleans
        height: pixel height for the component
        clickable: if True, clicking a piece tries to click a matching
                   Streamlit button in the parent DOM. Set False for
                   display-only mode.
    """

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

    total = len(PUZZLE_SECTIONS)
    done_count = sum(1 for v in completed_sections.values() if v)
    all_done = done_count == total

    html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;700&display=swap');
        .pzw {{
            font-family: 'Inter', sans-serif;
            max-width: 750px;
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
            max-width: 320px;
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
            max-width: 700px;
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
        <h3>NAF Framework Progress &mdash; {done_count} of {total} complete</h3>
        <div class="pbar"><div class="pfill" id="pfill"></div></div>
        <div class="psvg">
            <svg id="pzSvg" viewBox="-50 -50 700 420" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;"></svg>
        </div>
        <div class="cmsg" id="cmsg">
            {"All sections complete! Your solution design is ready." if all_done else ""}
        </div>
    </div>

    <script>
    (function() {{
        const NS = 'http://www.w3.org/2000/svg';
        const CLICKABLE = {'true' if clickable else 'false'};
        const pieces = {pieces_json};
        const svg = document.getElementById('pzSvg');

        const W = 185, H = 90;
        const PAD = 25;
        const COLS = [PAD, PAD + W, PAD + 2*W];
        const ROWS = [PAD, PAD + H];

        // Nub parameters for classic mushroom shape
        const NZ = 14;   // half-length of nub zone on edge
        const NK = 5;    // neck offset from piece edge
        const NH = 8;    // half-distance between arc endpoints along edge
        const HR = 11;   // head arc radius (> NH for mushroom bulge)

        // Edge config: [top, right, bottom, left]
        // 1 = nub out, -1 = indent in, 0 = flat
        const edges = {{
            '0,0': [0, 1, 1, 0],   '0,1': [0, 1, 1, -1],   '0,2': [0, 0, 1, -1],
            '1,0': [-1, 1, 0, 0],  '1,1': [-1, 1, 0, -1],  '1,2': [-1, 0, 0, -1]
        }};

        // SVG icon templates (drawn at origin, will be translated)
        const ICONS = {{
            presentation: `
                <rect x="-11" y="-9" width="22" height="14" rx="1.5" fill="none" stroke="#1a1a1a" stroke-width="1.6"/>
                <line x1="-3" y1="5" x2="-5" y2="9" stroke="#1a1a1a" stroke-width="1.5"/>
                <line x1="3" y1="5" x2="5" y2="9" stroke="#1a1a1a" stroke-width="1.5"/>
                <line x1="-6" y1="9" x2="6" y2="9" stroke="#1a1a1a" stroke-width="1.5"/>
            `,
            observability: `
                <circle cx="-2" cy="-2" r="6" fill="none" stroke="#1a1a1a" stroke-width="1.6"/>
                <line x1="2.3" y1="2.3" x2="8" y2="8" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round"/>
            `,
            orchestration: `
                <circle cx="0" cy="-7" r="3" fill="#1a1a1a"/>
                <circle cx="-9" cy="5" r="3" fill="#1a1a1a"/>
                <circle cx="9" cy="5" r="3" fill="#1a1a1a"/>
                <line x1="0" y1="-4" x2="-7" y2="3" stroke="#1a1a1a" stroke-width="1.5"/>
                <line x1="0" y1="-4" x2="7" y2="3" stroke="#1a1a1a" stroke-width="1.5"/>
            `,
            intent: `
                <path d="M0,-10 L10,0 L0,10 L-10,0 Z" fill="none" stroke="#1a1a1a" stroke-width="1.6"/>
                <path d="M0,-5 L5,0 L0,5 L-5,0 Z" fill="none" stroke="#1a1a1a" stroke-width="1.1" stroke-dasharray="2,2"/>
            `,
            collector: `
                <path d="M0,-10 L6,-3 L-6,-3 Z" fill="#1a1a1a" opacity="0.8"/>
                <path d="M0,-4 L8,4 L-8,4 Z" fill="#1a1a1a" opacity="0.65"/>
                <path d="M0,2 L9,10 L-9,10 Z" fill="#1a1a1a" opacity="0.5"/>
            `,
            executor: `
                <path d="M-8,-8 L0,-2 L8,-8" fill="none" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M-8,-2 L0,4 L8,-2" fill="none" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M-8,4 L0,10 L8,4" fill="none" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            `
        }};

        function jigsawPath(x, y, w, h, top, right, bottom, left) {{
            let d = 'M ' + x + ' ' + y;

            // TOP edge (left to right)
            if (top === 0) {{
                d += ' L ' + (x+w) + ' ' + y;
            }} else {{
                var mx = x + w/2;
                d += ' L ' + (mx - NZ) + ' ' + y;
                d += ' L ' + (mx - NH) + ' ' + (y + NK);
                d += ' A ' + HR + ' ' + HR + ' 0 1 1 ' + (mx + NH) + ' ' + (y + NK);
                d += ' L ' + (mx + NZ) + ' ' + y;
                d += ' L ' + (x+w) + ' ' + y;
            }}

            // RIGHT edge (top to bottom)
            if (right === 0) {{
                d += ' L ' + (x+w) + ' ' + (y+h);
            }} else {{
                var my = y + h/2;
                d += ' L ' + (x+w) + ' ' + (my - NZ);
                d += ' L ' + (x+w+NK) + ' ' + (my - NH);
                d += ' A ' + HR + ' ' + HR + ' 0 1 1 ' + (x+w+NK) + ' ' + (my + NH);
                d += ' L ' + (x+w) + ' ' + (my + NZ);
                d += ' L ' + (x+w) + ' ' + (y+h);
            }}

            // BOTTOM edge (right to left)
            if (bottom === 0) {{
                d += ' L ' + x + ' ' + (y+h);
            }} else {{
                var mx = x + w/2;
                d += ' L ' + (mx + NZ) + ' ' + (y+h);
                d += ' L ' + (mx + NH) + ' ' + (y+h+NK);
                d += ' A ' + HR + ' ' + HR + ' 0 1 0 ' + (mx - NH) + ' ' + (y+h+NK);
                d += ' L ' + (mx - NZ) + ' ' + (y+h);
                d += ' L ' + x + ' ' + (y+h);
            }}

            // LEFT edge (bottom to top)
            if (left === 0) {{
                d += ' Z';
            }} else {{
                var my = y + h/2;
                d += ' L ' + x + ' ' + (my + NZ);
                d += ' L ' + (x+NK) + ' ' + (my + NH);
                d += ' A ' + HR + ' ' + HR + ' 0 1 0 ' + (x+NK) + ' ' + (my - NH);
                d += ' L ' + x + ' ' + (my - NZ);
                d += ' Z';
            }}

            return d;
        }}

        function addIcon(parent, svgStr, tx, ty) {{
            var g = document.createElementNS(NS, 'g');
            g.setAttribute('transform', 'translate(' + tx + ',' + ty + ')');
            var tmp = document.createElementNS(NS, 'svg');
            tmp.innerHTML = svgStr;
            while (tmp.firstChild) g.appendChild(tmp.firstChild);
            parent.appendChild(g);
        }}

        pieces.forEach(function(p) {{
            var key = p.row + ',' + p.col;
            var e = edges[key];
            var bx = COLS[p.col], by = ROWS[p.row];
            var pathD = jigsawPath(bx, by, W, H, e[0], e[1], e[2], e[3]);

            var g = document.createElementNS(NS, 'g');
            g.classList.add('pg');
            if (!p.done) g.classList.add('sc');

            // Piece shape
            var path = document.createElementNS(NS, 'path');
            path.setAttribute('d', pathD);
            path.setAttribute('fill', p.color);
            path.classList.add('pp');
            g.appendChild(path);

            // Center of piece
            var cx = bx + W/2;
            var cy = by + H/2;

            // Icon (offset above center)
            if (ICONS[p.key]) {{
                addIcon(g, ICONS[p.key], cx, cy - 10);
            }}

            // Label text below icon
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

            // Check mark for completed pieces
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

            // Transform: scatter or assembled
            g.style.transformOrigin = cx + 'px ' + cy + 'px';
            if (p.done) {{
                g.style.transform = 'translate(0,0) rotate(0deg)';
            }} else {{
                g.style.transform = 'translate(' + p.sx + 'px,' + p.sy + 'px) rotate(' + p.sr + 'deg)';
            }}

            // Click handler — only active when clickable is true
            if (CLICKABLE) {{
                g.style.cursor = 'pointer';
                g.addEventListener('click', function() {{
                    try {{
                        var btns = window.parent.document.querySelectorAll('button[kind="secondary"], button[kind="primary"]');
                        var target = p.label;
                        for (var b = 0; b < btns.length; b++) {{
                            var txt = btns[b].textContent.trim();
                            // Match buttons like "🧩 Presentation" or "✅ Presentation"
                            // Use endsWith to avoid partial matches between section names
                            if (txt === target || txt.endsWith(' ' + target)) {{
                                btns[b].click();
                                break;
                            }}
                        }}
                    }} catch(e) {{
                        window.parent.postMessage({{
                            type: 'streamlit:puzzle_click',
                            section: p.key
                        }}, '*');
                    }}
                }});
            }}

            svg.appendChild(g);
        }});
    }})();
    </script>
    """

    components.html(html, height=height, scrolling=False)


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
