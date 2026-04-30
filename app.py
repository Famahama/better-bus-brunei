import os
import streamlit as st
import pandas as pd
from collections import defaultdict, deque

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bas Brunei · Route Planner",
    page_icon="🚌",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --yellow: #F5C518;
    --dark:   #0D0D0D;
    --mid:    #1A1A1A;
    --card:   #222222;
    --border: #333333;
    --text:   #E8E8E8;
    --muted:  #888888;
    --green:  #2ECC71;
    --red:    #E74C3C;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--dark);
    color: var(--text);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 720px; }

/* Hero header */
.hero {
    background: var(--yellow);
    color: var(--dark);
    padding: 2rem 2rem 1.5rem;
    border-radius: 4px;
    margin-bottom: 2rem;
}
.hero h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.25rem 0;
    letter-spacing: -1px;
    line-height: 1.1;
}
.hero p {
    font-size: 0.85rem;
    margin: 0;
    opacity: 0.7;
    font-weight: 400;
}

/* Section labels */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--yellow);
    margin-bottom: 0.5rem;
}

/* Input boxes */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text) !important;
}

/* Button */
.stButton > button {
    background: var(--yellow);
    color: var(--dark);
    border: none;
    border-radius: 4px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 1px;
    padding: 0.65rem 2rem;
    transition: opacity 0.15s;
}
.stButton > button:hover { opacity: 0.85; }

/* Result card */
.result-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.5rem;
    margin-top: 1.5rem;
}
.result-card h3 {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--yellow);
    margin: 0 0 1rem 0;
}

/* Route badge */
.route-badge {
    display: inline-block;
    background: var(--yellow);
    color: var(--dark);
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    font-size: 1.1rem;
    padding: 0.2rem 0.6rem;
    border-radius: 3px;
    margin-right: 0.5rem;
    vertical-align: middle;
}

/* Step line */
.step {
    display: flex;
    align-items: flex-start;
    margin-bottom: 1rem;
    gap: 1rem;
}
.step-num {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    min-width: 20px;
    padding-top: 3px;
}
.step-body { flex: 1; }
.step-title {
    font-weight: 600;
    font-size: 1rem;
    color: var(--text);
    margin-bottom: 0.15rem;
}
.step-sub {
    font-size: 0.82rem;
    color: var(--muted);
}
.step-connector {
    width: 1px;
    height: 20px;
    background: var(--border);
    margin-left: 9px;
    margin-bottom: 0;
}

/* Transfer tag */
.transfer-tag {
    display: inline-block;
    background: #2a2a2a;
    border: 1px solid var(--yellow);
    color: var(--yellow);
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 1px;
    padding: 0.15rem 0.5rem;
    border-radius: 2px;
    margin-top: 0.4rem;
}

/* No route */
.no-route {
    text-align: center;
    padding: 2rem;
    color: var(--muted);
    font-size: 0.9rem;
}

/* Stop list */
.stop-list {
    background: var(--mid);
    border-radius: 4px;
    padding: 1rem;
    margin-top: 0.5rem;
    max-height: 300px;
    overflow-y: auto;
}
.stop-item {
    font-size: 0.85rem;
    padding: 0.3rem 0;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.stop-item:last-child { border-bottom: none; }
.stop-name-text { color: var(--text); font-size: 0.85rem; }
.stop-num { color: var(--muted); font-family: 'Space Mono', monospace; font-size: 0.7rem; }

/* Divider */
hr { border-color: var(--border); margin: 1.5rem 0; }

/* Expander */
details summary { cursor: pointer; color: var(--muted); font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
GTFS_DIR = os.path.join(os.path.dirname(__file__), "gtfs_output")

def load_data():
    stops      = pd.read_csv(os.path.join(GTFS_DIR, "stops.txt"))
    routes     = pd.read_csv(os.path.join(GTFS_DIR, "routes.txt"))
    trips      = pd.read_csv(os.path.join(GTFS_DIR, "trips.txt"))
    stop_times = pd.read_csv(os.path.join(GTFS_DIR, "stop_times.txt"))

    df = stop_times.merge(stops[["stop_id", "stop_name"]], on="stop_id", how="left")
    df = df.merge(trips[["trip_id", "route_id", "trip_headsign"]], on="trip_id", how="left")
    df = df.merge(routes[["route_id", "route_short_name", "route_long_name"]], on="route_id", how="left")
    df["stop_name_clean"] = df["stop_name"].str.strip().str.lower()
    return df

df = load_data()

# ── Build graph for routing ───────────────────────────────────────────────────
@st.cache_data
def build_graph(df):
    # stop → list of trips serving it
    stop_routes = defaultdict(list)
    for _, row in df.iterrows():
        stop_routes[row["stop_name_clean"]].append({
            "trip_id":   row["trip_id"],
            "route":     row["route_short_name"],
            "direction": row["trip_headsign"],
            "stop_seq":  row["stop_sequence"],
            "stop_name": row["stop_name"],
            "stop_id":   row["stop_id"],
            "full_route": row["route_long_name"],
        })

    # trip → ordered list of stops
    trip_stops = defaultdict(list)
    for _, row in df.sort_values("stop_sequence").iterrows():
        trip_stops[row["trip_id"]].append({
            "stop_seq":       row["stop_sequence"],
            "stop_name":      row["stop_name"],
            "stop_name_clean": row["stop_name_clean"],
            "stop_id":        row["stop_id"],
        })

    return stop_routes, trip_stops

stop_routes, trip_stops = build_graph(df)

# ── Fuzzy stop search ─────────────────────────────────────────────────────────
def find_stops(query):
    """Return matching stop names (original casing) for a query string."""
    q = query.strip().lower()
    if not q:
        return []
    matches = []
    seen = set()
    for _, row in df.iterrows():
        name = row["stop_name"]
        clean = row["stop_name_clean"]
        if q in clean and name not in seen:
            matches.append(name)
            seen.add(name)
    return sorted(matches)

# ── Route finder ──────────────────────────────────────────────────────────────
def find_route(origin_clean, dest_clean):
    """
    Returns list of journey options, each a dict with:
      type: 'direct' | 'transfer'
      legs: list of leg dicts
    """
    if origin_clean not in stop_routes or dest_clean not in stop_routes:
        return []

    origin_entries = stop_routes[origin_clean]
    dest_entries   = stop_routes[dest_clean]

    origin_trip_keys = {e["trip_id"]: e for e in origin_entries}
    dest_trip_keys   = {e["trip_id"]: e for e in dest_entries}

    results = []

    def make_segment(stops, from_idx, to_idx):
        """Return (segment, stop_count) in travel direction, regardless of trip order."""
        lo, hi = min(from_idx, to_idx), max(from_idx, to_idx)
        seg = stops[lo:hi+1]
        if from_idx > to_idx:
            seg = list(reversed(seg))
        return seg, hi - lo

    # ── Direct routes ──
    for trip_id in origin_trip_keys:
        if trip_id in dest_trip_keys:
            o = origin_trip_keys[trip_id]
            stops = trip_stops[trip_id]
            o_idx = next((i for i, s in enumerate(stops) if s["stop_name_clean"] == origin_clean), None)
            d_idx = next((i for i, s in enumerate(stops) if s["stop_name_clean"] == dest_clean), None)
            if o_idx is not None and d_idx is not None and o_idx != d_idx:
                segment, count = make_segment(stops, o_idx, d_idx)
                results.append({
                    "type": "direct",
                    "legs": [{
                        "trip_id":   trip_id,
                        "route":     o["route"],
                        "direction": o["direction"],
                        "full_route": o["full_route"],
                        "board":  stops[o_idx]["stop_name"],
                        "alight": stops[d_idx]["stop_name"],
                        "stops_count": count,
                        "segment": segment,
                    }]
                })

    if results:
        return results[:3]

    # ── Transfer routes (1 change) ──
    # Collect all stops reachable from origin (either direction on each trip)
    origin_all_stops = set()
    for trip_id, o in origin_trip_keys.items():
        for s in trip_stops[trip_id]:
            origin_all_stops.add(s["stop_name_clean"])

    # Collect all stops from which destination is reachable (either direction)
    dest_all_stops = set()
    for trip_id, d in dest_trip_keys.items():
        for s in trip_stops[trip_id]:
            dest_all_stops.add(s["stop_name_clean"])

    transfer_stops = origin_all_stops & dest_all_stops

    for transfer_clean in transfer_stops:
        if transfer_clean == origin_clean or transfer_clean == dest_clean:
            continue

        for trip_id1, o in origin_trip_keys.items():
            stops1 = trip_stops[trip_id1]
            o_idx = next((i for i, s in enumerate(stops1) if s["stop_name_clean"] == origin_clean), None)
            t_idx = next((i for i, s in enumerate(stops1) if s["stop_name_clean"] == transfer_clean), None)
            if o_idx is None or t_idx is None or o_idx == t_idx:
                continue

            for trip_id2, d in dest_trip_keys.items():
                if trip_id2 == trip_id1:
                    continue
                stops2 = trip_stops[trip_id2]
                t2_idx = next((i for i, s in enumerate(stops2) if s["stop_name_clean"] == transfer_clean), None)
                d_idx  = next((i for i, s in enumerate(stops2) if s["stop_name_clean"] == dest_clean), None)
                if t2_idx is None or d_idx is None or t2_idx == d_idx:
                    continue

                seg1, count1 = make_segment(stops1, o_idx, t_idx)
                seg2, count2 = make_segment(stops2, t2_idx, d_idx)
                results.append({
                    "type": "transfer",
                    "legs": [
                        {
                            "trip_id":   trip_id1,
                            "route":     o["route"],
                            "direction": o["direction"],
                            "full_route": o["full_route"],
                            "board":  stops1[o_idx]["stop_name"],
                            "alight": stops1[t_idx]["stop_name"],
                            "stops_count": count1,
                            "segment": seg1,
                        },
                        {
                            "trip_id":   trip_id2,
                            "route":     d["route"],
                            "direction": d["direction"],
                            "full_route": d["full_route"],
                            "board":  stops2[t2_idx]["stop_name"],
                            "alight": stops2[d_idx]["stop_name"],
                            "stops_count": count2,
                            "segment": seg2,
                        }
                    ]
                })

                if len(results) >= 3:
                    return results[:3]

    return results[:3]

# ── Get all unique stop names for dropdowns ───────────────────────────────────
@st.cache_data
def get_all_stops():
    stops = df["stop_name"].dropna().unique().tolist()
    return sorted(set(stops))

all_stops = get_all_stops()

# ── Translations ──────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "English": {
        "subtitle":        "Public bus route planner · Brunei-Muara & beyond",
        "tab_plan":        "🗺️ Plan a Journey",
        "tab_browse":      "📋 Browse Routes",
        "origin":          "Origin",
        "destination":     "Destination",
        "select_stop":     "— Select stop —",
        "swap":            "⇅  Swap",
        "find_route":      "FIND ROUTE →",
        "warn_select":     "Please select both an origin and destination stop.",
        "warn_same":       "Origin and destination are the same stop.",
        "no_route_1":      "No route found between",
        "no_route_2":      "Try nearby stops or check spelling.",
        "option":          "Option",
        "direct":          "DIRECT ROUTE",
        "transfer":        "1 TRANSFER",
        "board_at":        "Board at",
        "alight_at":       "Alight at",
        "stops_along":     "{n} {noun} along the way",
        "stop_singular":   "stop",
        "stop_plural":     "stops",
        "transfer_at":     "TRANSFER AT",
        "show_stops":      "Show all stops · Leg {j} (Route {r})",
        "select_route":    "Select Route",
        "choose_route":    "— Choose a route —",
        "route_label":     "Route",
        "stops_total":     "stops total",
    },
    "Melayu": {
        "subtitle":        "Perancang laluan bas awam · Brunei-Muara & sekitar",
        "tab_plan":        "🗺️ Rancang Perjalanan",
        "tab_browse":      "📋 Semak Laluan",
        "origin":          "Asal",
        "destination":     "Destinasi",
        "select_stop":     "— Pilih perhentian —",
        "swap":            "⇅  Tukar",
        "find_route":      "CARI LALUAN →",
        "warn_select":     "Sila pilih perhentian asal dan destinasi.",
        "warn_same":       "Asal dan destinasi adalah perhentian yang sama.",
        "no_route_1":      "Tiada laluan ditemui antara",
        "no_route_2":      "Cuba perhentian berdekatan atau semak ejaan.",
        "option":          "Pilihan",
        "direct":          "LALUAN TERUS",
        "transfer":        "1 PERTUKARAN",
        "board_at":        "Naik di",
        "alight_at":       "Turun di",
        "stops_along":     "{n} {noun} sepanjang perjalanan",
        "stop_singular":   "perhentian",
        "stop_plural":     "perhentian",
        "transfer_at":     "PERTUKARAN DI",
        "show_stops":      "Tunjukkan semua perhentian · Kaki {j} (Laluan {r})",
        "select_route":    "Pilih Laluan",
        "choose_route":    "— Pilih laluan —",
        "route_label":     "Laluan",
        "stops_total":     "perhentian keseluruhan",
    },
    "中文": {
        "subtitle":        "公共巴士路线规划 · 文莱及周边地区",
        "tab_plan":        "🗺️ 规划行程",
        "tab_browse":      "📋 浏览路线",
        "origin":          "出发地",
        "destination":     "目的地",
        "select_stop":     "— 请选择站点 —",
        "swap":            "⇅  互换",
        "find_route":      "查找路线 →",
        "warn_select":     "请选择出发站和目的站。",
        "warn_same":       "出发站和目的站相同。",
        "no_route_1":      "未找到路线，出发站与目的站之间：",
        "no_route_2":      "请尝试附近站点或检查拼写。",
        "option":          "方案",
        "direct":          "直达路线",
        "transfer":        "需转乘1次",
        "board_at":        "上车于",
        "alight_at":       "下车于",
        "stops_along":     "途经 {n} 个{noun}",
        "stop_singular":   "站",
        "stop_plural":     "站",
        "transfer_at":     "转乘于",
        "show_stops":      "显示所有站点 · 第{j}段（路线 {r}）",
        "select_route":    "选择路线",
        "choose_route":    "— 选择路线 —",
        "route_label":     "路线",
        "stops_total":     "个站点",
    },
    "বাংলা": {
        "subtitle":        "পাবলিক বাস রুট পরিকল্পনাকারী · ব্রুনাই-মুয়ারা ও তার বাইরে",
        "tab_plan":        "🗺️ যাত্রা পরিকল্পনা",
        "tab_browse":      "📋 রুট ব্রাউজ করুন",
        "origin":          "উৎপত্তিস্থল",
        "destination":     "গন্তব্য",
        "select_stop":     "— স্টপ নির্বাচন করুন —",
        "swap":            "⇅  অদলবদল",
        "find_route":      "রুট খুঁজুন →",
        "warn_select":     "অনুগ্রহ করে উৎস ও গন্তব্য স্টপ নির্বাচন করুন।",
        "warn_same":       "উৎস ও গন্তব্য একই স্টপ।",
        "no_route_1":      "মধ্যে কোনো রুট পাওয়া যায়নি",
        "no_route_2":      "কাছাকাছি স্টপ চেষ্টা করুন বা বানান পরীক্ষা করুন।",
        "option":          "বিকল্প",
        "direct":          "সরাসরি রুট",
        "transfer":        "১টি ট্রান্সফার",
        "board_at":        "উঠুন",
        "alight_at":       "নামুন",
        "stops_along":     "পথে {n}টি {noun}",
        "stop_singular":   "স্টপ",
        "stop_plural":     "স্টপ",
        "transfer_at":     "ট্রান্সফার করুন",
        "show_stops":      "সব স্টপ দেখুন · লেগ {j} (রুট {r})",
        "select_route":    "রুট নির্বাচন করুন",
        "choose_route":    "— রুট বেছে নিন —",
        "route_label":     "রুট",
        "stops_total":     "স্টপ মোট",
    },
    "हिन्दी": {
        "subtitle":        "सार्वजनिक बस रूट योजनाकार · ब्रुनेई-मुआरा और आगे",
        "tab_plan":        "🗺️ यात्रा की योजना",
        "tab_browse":      "📋 रूट ब्राउज़ करें",
        "origin":          "उद्गम",
        "destination":     "गंतव्य",
        "select_stop":     "— स्टॉप चुनें —",
        "swap":            "⇅  बदलें",
        "find_route":      "रूट खोजें →",
        "warn_select":     "कृपया उद्गम और गंतव्य दोनों स्टॉप चुनें।",
        "warn_same":       "उद्गम और गंतव्य एक ही स्टॉप हैं।",
        "no_route_1":      "के बीच कोई रूट नहीं मिला",
        "no_route_2":      "आस-पास के स्टॉप आज़माएं या वर्तनी जांचें।",
        "option":          "विकल्प",
        "direct":          "सीधा रूट",
        "transfer":        "1 स्थानांतरण",
        "board_at":        "चढ़ें",
        "alight_at":       "उतरें",
        "stops_along":     "रास्ते में {n} {noun}",
        "stop_singular":   "स्टॉप",
        "stop_plural":     "स्टॉप",
        "transfer_at":     "यहाँ ट्रांसफर करें",
        "show_stops":      "सभी स्टॉप दिखाएं · लेग {j} (रूट {r})",
        "select_route":    "रूट चुनें",
        "choose_route":    "— एक रूट चुनें —",
        "route_label":     "रूट",
        "stops_total":     "स्टॉप कुल",
    },
}

# ── UI ────────────────────────────────────────────────────────────────────────

# Language selector (top-right via columns)
lang_col, _ = st.columns([2, 5])
with lang_col:
    selected_lang = st.selectbox(
        "🌐",
        list(TRANSLATIONS.keys()),
        key="lang",
        label_visibility="collapsed",
    )

t = TRANSLATIONS[selected_lang]

st.markdown(f"""
<div class="hero">
<h1>🚌 Better Bus Brunei</h1>
<p>{t["subtitle"]}</p>
</div>
""", unsafe_allow_html=True)

# ── Session state for swap ────────────────────────────────────────────────────
_opts = [t["select_stop"]] + all_stops

def swap_stops():
    o = st.session_state.get("origin_sel", _opts[0])
    d = st.session_state.get("dest_sel", _opts[0])
    st.session_state["origin_sel"] = d
    st.session_state["dest_sel"] = o

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs([t["tab_plan"], t["tab_browse"]])

with tab1:
    st.markdown(f'<div class="section-label">{t["origin"]}</div>', unsafe_allow_html=True)
    origin = st.selectbox("", _opts, key="origin_sel", label_visibility="collapsed")

    col_swap, _ = st.columns([2, 6])
    with col_swap:
        st.button(t["swap"], on_click=swap_stops, use_container_width=True)

    st.markdown(f'<div class="section-label">{t["destination"]}</div>', unsafe_allow_html=True)
    dest = st.selectbox("", _opts, key="dest_sel", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    search = st.button(t["find_route"], use_container_width=True)

    if search:
        if origin == t["select_stop"] or dest == t["select_stop"]:
            st.warning(t["warn_select"])
        elif origin == dest:
            st.warning(t["warn_same"])
        else:
            origin_clean = origin.strip().lower()
            dest_clean   = dest.strip().lower()
            results = find_route(origin_clean, dest_clean)

            if not results:
                st.markdown(
                    f'<div class="result-card"><div class="no-route">'
                    f'{t["no_route_1"]}<br>'
                    f'<strong>{origin}</strong> and <strong>{dest}</strong>.<br><br>'
                    f'<span style="font-size:0.75rem">{t["no_route_2"]}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                for i, result in enumerate(results):
                    legs  = result["legs"]
                    label = t["direct"] if result["type"] == "direct" else t["transfer"]

                    parts = [f'<div class="result-card"><h3>{t["option"]} {i+1} · {label}</h3>']
                    for j, leg in enumerate(legs):
                        total = leg["stops_count"]
                        noun  = t["stop_singular"] if total == 1 else t["stop_plural"]
                        stops_text = t["stops_along"].format(n=total, noun=noun)
                        parts.append(
                            f'<div class="step">'
                            f'<div class="step-num">{j+1}</div>'
                            f'<div class="step-body">'
                            f'<div class="step-title">'
                            f'<span class="route-badge">{leg["route"]}</span> {leg["direction"]}'
                            f'</div>'
                            f'<div class="step-sub">'
                            f'{t["board_at"]} <strong>{leg["board"]}</strong> &middot; '
                            f'{t["alight_at"]} <strong>{leg["alight"]}</strong><br>'
                            f'{stops_text}'
                            f'</div>'
                            f'</div>'
                            f'</div>'
                        )
                        if j < len(legs) - 1:
                            xfer = legs[j + 1]["board"].upper()
                            parts.append(
                                f'<div style="margin-left:2rem;margin-bottom:0.75rem">'
                                f'<span class="transfer-tag">&#8596; {t["transfer_at"]} {xfer}</span>'
                                f'</div>'
                            )
                    parts.append('</div>')
                    st.markdown("".join(parts), unsafe_allow_html=True)

                    # Expandable stop list
                    for j, leg in enumerate(legs):
                        label_exp = t["show_stops"].format(j=j+1, r=leg["route"])
                        with st.expander(label_exp):
                            rows = "".join(
                                f'<div class="stop-item">'
                                f'<span class="stop-name-text">{s["stop_name"]}</span>'
                                f'<span class="stop-num">#{s["stop_seq"]}</span>'
                                f'</div>'
                                for s in leg["segment"]
                            )
                            st.markdown(
                                f'<div class="stop-list">{rows}</div>',
                                unsafe_allow_html=True,
                            )

with tab2:
    st.markdown(f'<div class="section-label">{t["select_route"]}</div>', unsafe_allow_html=True)
    route_numbers = sorted(df["route_short_name"].unique().tolist())
    selected_route = st.selectbox("", [t["choose_route"]] + route_numbers, label_visibility="collapsed")

    if not selected_route.startswith("—"):
        route_df = df[df["route_short_name"] == selected_route].sort_values("stop_sequence")
        direction  = route_df.iloc[0]["trip_headsign"]
        full_name  = route_df.iloc[0]["route_long_name"]
        total_stops = len(route_df)

        st.markdown(
            f'<div class="result-card">'
            f'<h3>{t["route_label"]} {selected_route}</h3>'
            f'<div style="margin-bottom:0.5rem">'
            f'<span class="route-badge">{selected_route}</span>'
            f'<strong style="color:var(--text)">{direction}</strong>'
            f'</div>'
            f'<div style="font-size:0.8rem;color:var(--muted);margin-bottom:1rem">{full_name}</div>'
            f'<div style="font-size:0.8rem;color:var(--muted)">{total_stops} {t["stops_total"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        rows = "".join(
            f'<div class="stop-item">'
            f'<span class="stop-name-text">{row["stop_name"]}</span>'
            f'<span class="stop-num">#{int(row["stop_sequence"])}</span>'
            f'</div>'
            for _, row in route_df.iterrows()
        )
        st.markdown(
            f'<div class="stop-list" style="margin-top:1rem">{rows}</div>',
            unsafe_allow_html=True,
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<div style="text-align:center; color:var(--muted); font-size:0.75rem; padding-bottom:2rem">
Data sourced from JPD Brunei · 21 routes · 676 stops (GTFS)<br>
<span style="font-family:'Space Mono',monospace">better-bus-brunei v0.2</span><br><br>
<span style="font-size:0.8rem">
<a href="https://www.instagram.com/famahamaf/" target="_blank"
   style="color:var(--yellow);text-decoration:none;margin-right:1rem">
   📸 Instagram
</a>
<a href="https://www.linkedin.com/in/fahmi-rosli-46709b115/" target="_blank"
   style="color:var(--yellow);text-decoration:none">
   💼 LinkedIn
</a>
</span>
</div>
""", unsafe_allow_html=True)
