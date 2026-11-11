from gevent import monkey
monkey.patch_all()

import sql
import re
import math
import time
import calendar
import flask
import requests
from flask import request, jsonify
from flask_cors import CORS
from sql import create_connection, execute_read_query, close_connection, Creds

app = flask.Flask(__name__)
app.config["DEBUG"] = False
app.json.sort_keys = False
CORS(app)

myCreds = sql.Creds()
_VEHICLE_FILTER_CACHE = {}
_VEHICLE_FILTER_CACHE_TTL = 300

def build_creation_date_cond(date_str, mode=None):
    s = (date_str or '').strip()
    if mode == 'yearly' or (mode is None and len(s) == 4):
        yr = s[:4]
        return "o.creation_date >= %s AND o.creation_date <= %s", [f"{yr}-01-01", f"{yr}-12-31"]
    if mode == 'monthly' or (mode is None and len(s) == 7):
        ym = s[:7]
        try:
            y_int, m_int = int(ym[:4]), int(ym[5:7])
            last_day = calendar.monthrange(y_int, m_int)[1]
        except Exception:
            last_day = 31
        return "o.creation_date >= %s AND o.creation_date <= %s", [f"{ym}-01", f"{ym}-{last_day:02d}"]
    return "o.creation_date = %s", [s[:10]]


STATE_NAMES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia', 'PR': 'Puerto Rico', 'GU': 'Guam', 'VI': 'Virgin Islands',
    'AB': 'Alberta', 'BC': 'British Columbia', 'MB': 'Manitoba', 'NB': 'New Brunswick',
    'NL': 'Newfoundland and Labrador', 'NF': 'Newfoundland', 'NS': 'Nova Scotia',
    'NT': 'Northwest Territories', 'NU': 'Nunavut', 'ON': 'Ontario',
    'PE': 'Prince Edward Island', 'QC': 'Quebec', 'PQ': 'Quebec', 'SK': 'Saskatchewan', 'YT': 'Yukon'
}

def parse_dealer_location(location_str):
    if not location_str or not isinstance(location_str, str):
        return 'OTHER', 'UNKNOWN', ''
    loc = location_str.strip().rstrip('.')
    if not loc:
        return 'OTHER', 'UNKNOWN', ''
    parts = loc.split(',')
    if len(parts) > 2:
        city = parts[-2].strip().upper() if parts[-2] else 'UNKNOWN'
    else:
        city = parts[0].strip().upper() if parts[0] else 'UNKNOWN'
    city = re.sub(r'[^\w\s]', '', city).strip()
    state = 'OTHER'
    zip_code = ''
    if len(parts) > 1:
        last_part = parts[-1].strip().rstrip('.')
        tokens = last_part.split()
        if tokens:
            state = re.sub(r'[^\w]', '', tokens[0]).strip().upper()
            if len(tokens) > 1:
                zip_code = ' '.join(tokens[1:]).strip().rstrip('.')
    elif len(parts) == 1:
        tokens = loc.split()
        if len(tokens) > 1:
            zip_code = ' '.join(tokens[1:]).strip().rstrip('.')
        elif loc.isdigit():
            zip_code = loc
    return state, city, zip_code

def normalize_dealer_name(name):
    if not name:
        return ''
    s = name.strip()
    s = re.sub(r'&', ' AND ', s)
    s = re.sub(r"['’]", "", s)
    s = re.sub(r'[^\w\s]', ' ', s)
    return ' '.join(s.split()).upper()

def normalize_location_key(state_code, city_name, zip_code, raw_loc):
    base_zip = zip_code.split('-')[0].strip() if '-' in zip_code else zip_code.strip()
    norm_city = ' '.join(re.sub(r'[^\w\s]', ' ', city_name).split()).upper()
    if base_zip:
        return f"{state_code}:{norm_city}:{base_zip}"
    norm_raw = ' '.join(re.sub(r'[^\w\s]', ' ', raw_loc).split()).upper()
    return f"{state_code}:{norm_city}:{norm_raw}"
 
def format_percent(count, total):
    if not count or not total or total <= 0 or count <= 0:
        return 0
    raw = (100.0 * count) / total
    if raw >= 0.01:
        return round(raw, 2)
    decimals = -int(math.floor(math.log10(raw)))
    val = round(raw, decimals)
    if val >= 0.01:
        return round(val, 2)
    return f"{val:.{decimals}f}".rstrip('0').rstrip('.')

OLLAMA_URL = "http://192.168.1.126:11434/api/generate"
AI_MODEL = "qwen2.5-coder:7b"
AI_SQL_CACHE = {}
AI_SQL_CACHE_TTL = 3600

VEHICLE_SELECT_SQL = (
    "SELECT v.vin AS `VIN`, v.modelYear AS `Year`, v.model AS `Model`, "
    "v.body AS `Body`, v.trim AS `Trim`, e.engine_type AS `Engine`, "
    "t.transmission_type AS `Trans`, d.drivetrain_type AS `Drivetrain`, "
    "c.color_name AS `Exterior_Color`, v.msrp AS `MSRP`, "
    "IFNULL((SELECT GROUP_CONCAT(se.special_desc) FROM SpecialEditions se WHERE se.vehicle_id = v.vehicle_id), '') AS `Package_Option`, "
    "o.country AS `Country`"
)

VEHICLE_BASE_JOINS_SQL = (
    "FROM Vehicles v\n"
    "LEFT JOIN Colors c ON v.color_id = c.color_id\n"
    "LEFT JOIN Engines e ON v.engine_id = e.engine_id\n"
    "LEFT JOIN Transmissions t ON v.transmission_id = t.transmission_id\n"
    "LEFT JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id\n"
    "LEFT JOIN Orders o ON v.order_id = o.order_id"
)

# Compact, fast-decode schema context for Ollama fallback
DB_SCHEMA_CONTEXT = """You are a MySQL query generator for GM vehicle build counts.
Output ONLY raw SQL on a single line. No markdown, no backticks around the query, no semicolon, no explanation.
- For vehicle listing queries, output ONLY: WHERE <conditions> (the SELECT and LEFT JOINs are added automatically).
- For count queries ("how many..."), output: SELECT COUNT(*) AS `Count` FROM Vehicles v <needed LEFT JOINs> WHERE <conditions>
- For DISTINCT column queries, output: SELECT DISTINCT <columns> FROM Vehicles v <needed LEFT JOINs> WHERE <conditions> LIMIT 500

Aliases & Tables:
v = Vehicles (vehicle_id, vin, modelYear, model, body, trim, engine_id, transmission_id, drivetrain_id, color_id, msrp, dealer_id, order_id)
c = Colors (color_id, color_name, rpo_code)
e = Engines (engine_id, engine_type, engine_rpo)
t = Transmissions (transmission_id, transmission_type)
d = Drivetrains (drivetrain_id, drivetrain_type)
dealer = Dealers (dealer_id, dealer_name, location, sitedealer_code)
o = Orders (order_id, order_number, creation_date, mmc_code_id, sell_source, country)
m = MMC_Codes (mmc_code_id, mmc_code)
SpecialEditions (special_id, vehicle_id, special_desc)
Options (option_id, vehicle_id, option_code)

Rules:
1. Year: `v.modelYear = 2022`.
2. Model (`v.model`): 'CAMARO', 'CT4', 'CT5', 'CT6', 'ESCALADE', 'ESCALADE IQ', 'HUMMER EV SUV', 'HUMMER EV PICKUP', 'SIERRA EV', 'SILVERADO EV', 'CORVETTE STINGRAY', 'CORVETTE Z06', 'CORVETTE E-RAY', 'CORVETTE ZR1', 'CORVETTE ZR1X', 'CORVETTE GRAND SPORT'. Use `v.model LIKE 'CORVETTE%'` ONLY for generic Corvette requests.
3. Trim (`v.trim`): ONLY the trim ('1LS', '1LT', '2LT', '3LT', '1SS', '2SS', 'ZL1', 'LT1', '1LZ', '2LZ', '3LZ', 'V-SERIES', 'V-SERIES BLACKWING', 'LUXURY', 'PREMIUM LUXURY', 'SPORT', '3X'). Never put packages (1LE, Z51) or transmissions (A10, M6) in `v.trim`. "CT5V Blackwing" => `v.model = 'CT5' AND v.trim = 'V-SERIES BLACKWING'`.
4. Transmission (`t.transmission_type`): 'A10', 'A8', 'M6', 'M7', or `LIKE 'A%'` (automatic), `LIKE 'M%'` (manual).
5. Drivetrain (`d.drivetrain_type`): 'RWD', 'AWD', '4WD'. Body (`v.body`): 'COUPE', 'CONVERTIBLE', 'SEDAN', 'SUV'. Country (`o.country`): 'USA', 'CANADA', 'MEXICO'.
6. Color (`c.color_name`): `c.color_name LIKE '%SUMMIT WHITE%'`. Matte/frost: `(c.color_name LIKE '%MATTE%' OR c.color_name LIKE '%FROST%')`.
7. SpecialEditions: `EXISTS (SELECT 1 FROM SpecialEditions se WHERE se.vehicle_id = v.vehicle_id AND se.special_desc LIKE '%Keyword%')`.
8. Options (3-char RPO): `EXISTS (SELECT 1 FROM Options opt WHERE opt.vehicle_id = v.vehicle_id AND opt.option_code = 'E60')`.

Examples:
User Request: 2022 Camaro 2SS 1LE A10 in Summit White
SQL Query: WHERE v.modelYear = 2022 AND v.model = 'CAMARO' AND v.trim = '2SS' AND t.transmission_type = 'A10' AND c.color_name LIKE '%SUMMIT WHITE%' AND EXISTS (SELECT 1 FROM SpecialEditions se WHERE se.vehicle_id = v.vehicle_id AND se.special_desc LIKE '%1LE%')

User Request: Show me all CT5V Blackwing in matte paint
SQL Query: WHERE v.model = 'CT5' AND v.trim = 'V-SERIES BLACKWING' AND (c.color_name LIKE '%MATTE%' OR c.color_name LIKE '%FROST%')

User Request: How many green Corvette ZR1s are there
SQL Query: SELECT COUNT(*) AS `Count` FROM Vehicles v LEFT JOIN Colors c ON v.color_id = c.color_id WHERE v.model = 'CORVETTE ZR1' AND c.color_name LIKE '%GREEN%'
"""

SPECIAL_EDITION_PATTERNS = [
    (r"\bcurated\s+by\s+cadillac\b|\bwox\b", "Curated by Cadillac", None),
    (r"\bcollector'?s?\s+edition\b", "Collectors Edition", None),
    (r"\bgarage\s*56(?:\s+special\s+edition)?\b", "Garage 56", None),
    (r"\bhertz\b|\bhendrick(?:\s+motorsports)?(?:\s+edition)?\b", "Hendrick", None),
    (r"\b2026\s+indianapolis\s+500\b|\bindy\s*500\s+festival\b", "2026 Indianapolis 500 Festival Vehicle", None),
    (r"\bindy\s*500\s+pace\s+car\b", None, "Z4Z"),
    (r"\bredline(?:\s+edition)?\b", None, "WBL"),
    (r"\bshock\s+(?:and|&)\s+steel(?:\s+edition)?\b", None, "B2E"),
    (r"\bc8\.?r(?:\s+edition)?\b|\bimsa\s+gtlm\b", "C8.R", None),
    (r"\bztk(?:\s+track)?(?:\s+performance)?(?:\s+package)?\b", "ZTK", None),
    (r"\bz07(?:\s+performance)?(?:\s+package)?\b", "Z07", None),
    (r"\bz51(?:\s+performance)?(?:\s+package)?\b", "Z51", None),
    (r"\bz52\s+sport\b", "Z52 Sport", None),
    (r"\bz52\s+track\b", "Z52 Track", None),
    (r"\bz52\b", "Z52", None),
    (r"\bgrand\s+sport\s+launch(?:\s+edition)?\b", "Grand Sport Launch", None),
    (r"\b70th\s+anniversary(?:\s+edition)?\b", "70th Anniversary", None),
    (r"\bstars\s+(?:and|&)\s+steel(?:\s+limited)?(?:\s+edition)?\b", "Stars & Steel", None),
    (r"\bquail\s+silver(?:\s+limited)?(?:\s+edition)?\b", "Quail Silver", None),
    (r"\bwatkins\s+glen(?:\s+imsa)?(?:\s+edition)?\b", "Watkins Glen", None),
    (r"\bsebring\s+imsa(?:\s+edition)?\b", "Sebring IMSA", None),
    (r"\broad\s+atlanta(?:\s+imsa)?(?:\s+edition)?\b", "Road Atlanta", None),
    (r"\barrival\s+edition\b", "Arrival Edition", None),
    (r"\bimpact\s+edition\b", "Impact Edition", None),
    (r"\belevation\s+edition\b", "Elevation Edition", None),
    (r"\bpetit\s+pataud(?:\s+special)?(?:\s+edition)?\b", "Petit Pataud", None),
    (r"\ble\s+monstre(?:\s+special)?(?:\s+edition)?\b", "Le Monstre", None),
    (r"\b120th\s+anniversary(?:\s+edition)?\b", "120th Anniversary", None),
    (r"\b20th\s+anniversary(?:\s+of\s+v-series)?(?:\s+special)?(?:\s+edition)?\b", "20th Anniversary", None),
    (r"\bprecision\s+package\b", "Precision Package", None),
    (r"\bdeep\s+ocean\s+appearance(?:\s+package)?\b", "Deep Ocean Appearance", None),
    (r"\bomega\s+edition\b", "Omega Edition", None),
    (r"\bextreme\s+off[\s-]*road(?:\s+package)?\b", "Extreme Off-Road", None),
    (r"\bpre[\s-]*production(?:\s+vehicle)?\b", "Pre-Production Vehicle", None),
    (r"\bshow\s+vehicle\b", "Show Vehicle", None),
    (r"\bfront\s+lift\b", None, "E60"),
    (r"\b1le(?:\s+extreme)?(?:\s+track)?(?:\s+performance)?(?:\s+package)?\b", "1LE", None),
]

SPECIFIC_COLOR_PHRASES = [
    "PANTHER BLACK MATTE", "PANTHER BLACK METALLIC TINTCOAT", "WHITE PEARL METALLIC TRICOAT",
    "LONG BEACH RED METALLIC TINTCOAT", "CORVETTE RACING YELLOW TINTCOAT", "SATIN STEEL GRAY METALLIC",
    "CERAMIC MATRIX GRAY METALLIC", "ACCELERATE YELLOW METALLIC", "COMPETITION YELLOW TINTCOAT",
    "ELKHART LAKE BLUE METALLIC", "MAGNUS GRAY MATTE METALLIC", "RED MIST METALLIC TINTCOAT",
    "WATKINS GLEN GRAY METALLIC", "ZEPHYR BLUE MATTE METALLIC", "AMPLIFY ORANGE TINTCOAT",
    "HYPERSONIC GRAY METALLIC", "HYSTERIA PURPLE METALLIC", "MANHATTAN NOIR METALLIC",
    "MERCURY SILVER METALLIC", "MIDNIGHT STEEL METALLIC", "RADIANT SILVER METALLIC",
    "RIVERSIDE BLUE METALLIC", "SEBRING ORANGE TINTCOAT", "STELLAR BLACK METALLIC",
    "ARGENT SILVER METALLIC", "BLACK DIAMOND TRICOAT", "BLADE SILVER METALLIC",
    "BLAZE ORANGE METALLIC", "CARBON FLASH METALLIC", "COASTAL BLUE METALLIC",
    "CRYSTAL WHITE TRICOAT", "CYBER YELLOW METALLIC", "DARK MOON METALLIC",
    "DEEP AMETHYST METALLIC", "EMERALD ISLE METALLIC", "GARNET RED TINTCOAT",
    "MIDNIGHT SKY METALLIC", "MOONSHOT GREEN MATTE", "MOSAIC BLACK METALLIC",
    "NITRO YELLOW METALLIC", "RADIANT RED TINTCOAT", "RALLY GREEN METALLIC",
    "RED HORIZON TINTCOAT", "RED OBSESSION TINTCOAT", "RIPTIDE BLUE METALLIC",
    "ROSWELL GREEN METALLIC", "ROYAL SPICE METALLIC", "SATIN STEEL METALLIC",
    "SEA WOLF GRAY TRICOAT", "SHADOW GRAY METALLIC", "SILVER FLARE METALLIC",
    "VIBRANT WHITE TRICOAT", "VIVID ORANGE METALLIC", "WILD CHERRY TINTCOAT",
    "ZEUS BRONZE METALLIC", "ADMIRAL BLUE METALLIC", "AFTERBURNER TINTCOAT",
    "BARBED WIRE METALLIC", "BLACK CHERRY TINTCOAT", "BLADE SILVER MATTE",
    "BLUE SMOKE METALLIC", "BOYSENBERRY METALLIC", "BRONZE DUNE METALLIC",
    "CARNELLIAN METALLIC", "CARNELIAN METALLIC", "DARK EMBER TINTCOAT",
    "DARK EMERALD FROST", "DEEP AURORA METALLIC", "DEEP OCEAN METALLIC",
    "DEEP OCEAN TINTCOAT", "DEEP SPACE METALLIC", "GALACTIC GRAY METALLIC",
    "GRAPHITE BLUE METALLIC", "INTERSTELLAR WHITE", "KINGFISHER METALLIC",
    "LIQUID STEEL TRICOAT", "MAGNUS METAL FROST", "MANHATTAN METALLIC",
    "MAVERICK NOIR FROST", "METEORITE METALLIC", "MIDNIGHT STEEL FROST",
    "NEPTUNE BLUE MATTE", "PITCH GRAY METALLIC", "POLAR WHITE TRICOAT",
    "SILVER ICE METALLIC", "SLATE GRAY METALLIC", "SUPERNOVA METALLIC",
    "ARC BLUE METALLIC", "BARBED WIRE FROST", "BLACK RAVEN FROST",
    "BLUE GLO METALLIC", "CAFFEINE METALLIC", "CELESTIAL METALLIC",
    "DEEP SEA METALLIC", "EVERGREEN METALLIC", "FITZ GRAY TRICOAT",
    "HYDRANGEA METALLIC", "INFRARED TINTCOAT", "SEA WOLF TRICOAT",
    "SHARKSKIN METALLIC", "SHIBORI METALLIC", "THUNDER METALLIC",
    "THUNDERSTORM GRAY", "TYPHOON METALLIC", "VERMILLION METALLIC",
    "AMPLIFY ORANGE", "SEBRING ORANGE", "HABANERO ORANGE", "MONARCH ORANGE",
    "SOLAR ORANGE", "SUMMIT WHITE", "ARCTIC WHITE", "ABALONE WHITE",
    "WHITE SANDS", "DEEP NOIR FROST", "ARC BLUE FROST", "ROSE GOLD FROST",
    "SHIBORI FROST", "ADOBE FROST", "MOONLIGHT MATTE", "KOMODO METALLIC",
    "GARNET METALLIC", "SHADOW METALLIC", "VIXEN METALLIC", "WILDER METALLIC",
    "DRIFT METALLIC", "FLARE METALLIC", "LATTE METALLIC", "LUNA METALLIC",
    "MAUI METALLIC", "MOSS METALLIC", "TIDE METALLIC", "WAVE METALLIC",
    "RIFT METALLIC", "CAROLINA BLUE", "ELECTRIC BLUE", "RAPID BLUE",
    "BLACK RAVEN", "ONYX BLACK", "VOID BLACK", "TORCH RED", "VELOCITY RED",
    "RED HOT", "CACTI GREEN", "CASPIA TRICOAT", "SIKU TRICOAT",
    "MAVERICK NOIR", "AEGEAN STONE", "SANDSTONE", "SHIBORI", "CAYMAN",
    "LAGOON", "PLUTO", "VENOM", "CRUSH", "SHOCK"
]

GENERIC_COLOR_WORDS = [
    "WHITE", "BLACK", "BLUE", "RED", "GREEN", "ORANGE", "YELLOW",
    "GRAY", "GREY", "SILVER", "PURPLE", "BRONZE", "BROWN", "GOLD"
]

DISTINCT_COLUMN_MAP = {
    "vin": ("v.vin AS `VIN`", "v"),
    "year": ("v.modelYear AS `Year`", "v"),
    "modelyear": ("v.modelYear AS `Year`", "v"),
    "model": ("v.model AS `Model`", "v"),
    "body": ("v.body AS `Body`", "v"),
    "trim": ("v.trim AS `Trim`", "v"),
    "engine": ("e.engine_type AS `Engine`", "e"),
    "trans": ("t.transmission_type AS `Trans`", "t"),
    "transmission": ("t.transmission_type AS `Trans`", "t"),
    "drivetrain": ("d.drivetrain_type AS `Drivetrain`", "d"),
    "color": ("c.color_name AS `Exterior_Color`", "c"),
    "exterior_color": ("c.color_name AS `Exterior_Color`", "c"),
    "msrp": ("v.msrp AS `MSRP`", "v"),
    "country": ("o.country AS `Country`", "o"),
    "dealer": ("dealer.dealer_name AS `Dealer`", "dealer"),
}

QUERY_STOPWORDS = {
    "show", "me", "all", "the", "cars", "car", "vehicles", "vehicle", "built",
    "made", "produced", "with", "in", "and", "or", "that", "which", "have",
    "has", "are", "is", "were", "was", "there", "find", "list", "get", "fetch",
    "give", "for", "of", "from", "a", "an", "to", "on", "at", "by", "paint",
    "painted", "color", "colored", "exterior", "package", "packages", "edition",
    "editions", "special", "option", "options", "transmission", "trans", "trim",
    "model", "models", "year", "years", "only", "return", "values", "value",
    "distinct", "unique", "vin", "vins", "how", "many", "count", "total",
    "number", "cadillac", "chevrolet", "chevy", "gmc", "gm", "series"
}


def build_full_vehicle_sql(where_clause, order_by_clause="", limit=500):
    """Assemble the canonical 12-column vehicle query with only needed extra joins."""
    where_clean = (where_clause or "").strip()
    if where_clean and not re.match(r"^WHERE\b", where_clean, re.IGNORECASE):
        where_clean = f"WHERE {where_clean}"
    joins = [VEHICLE_BASE_JOINS_SQL]
    combined = f"{where_clean} {order_by_clause}"
    if re.search(r"\bdealer\.", combined, re.IGNORECASE):
        joins.append("LEFT JOIN Dealers dealer ON v.dealer_id = dealer.dealer_id")
    if re.search(r"\bm\.", combined, re.IGNORECASE):
        joins.append("LEFT JOIN MMC_Codes m ON o.mmc_code_id = m.mmc_code_id")
    parts = [VEHICLE_SELECT_SQL, "\n".join(joins)]
    if where_clean:
        parts.append(where_clean)
    if order_by_clause:
        parts.append(order_by_clause.strip())
    if limit:
        parts.append(f"LIMIT {int(limit)}")
    return "\n".join(parts)


def parse_nl_query_intent(user_prompt):
    """
    Extract exact database conditions from a natural language query.
    Returns a dict with:
      - conditions: list of SQL WHERE predicates
      - mode: 'vehicles' | 'count' | 'distinct'
      - distinct_cols: list of (select_expr, table_alias)
      - order_by: optional ORDER BY clause
      - is_complete: True if 100% of non-stopword tokens in the prompt were matched
      - summary_hints: human-readable SQL hints for LLM fallback
    """
    raw = (user_prompt or "").strip()
    consumed = [False] * len(raw)

    def mark_span(start, end):
        for i in range(max(0, start), min(len(raw), end)):
            consumed[i] = True

    def span_free(start, end):
        return not any(consumed[i] for i in range(max(0, start), min(len(raw), end)))

    conditions = []
    models_found = []
    trims_found = []
    years_found = []
    order_by = ""

    # 1. Detect query mode (count vs distinct vs vehicle list)
    mode = "vehicles"
    distinct_cols = []

    for m in re.finditer(r"\b(?:how\s+many|total\s+number\s+of|count\s+of)\b", raw, re.IGNORECASE):
        mode = "count"
        mark_span(*m.span())

    distinct_match = re.search(
        r"\b(?:return\s+(?:only\s+)?(?:the\s+)?)?(?:distinct|unique)\s+(?:values?\s+for\s+)?([a-z0-9_,\s]+?)(?:$|\.)",
        raw, re.IGNORECASE
    )
    if distinct_match:
        col_text = distinct_match.group(1)
        parsed_cols = []
        for token in re.findall(r"[a-zA-Z_]+", col_text.lower()):
            if token in ("and", "or", "the", "for", "of"):
                continue
            if token in DISTINCT_COLUMN_MAP and DISTINCT_COLUMN_MAP[token] not in parsed_cols:
                parsed_cols.append(DISTINCT_COLUMN_MAP[token])
        if parsed_cols:
            mode = "distinct"
            distinct_cols = parsed_cols
            mark_span(*distinct_match.span())

    # 2. Detect VIN exact or substring matches (e.g., have "N5RW" in the VIN)
    for m in re.finditer(r"\b([A-HJ-NPR-Z0-9]{17})\b", raw, re.IGNORECASE):
        if span_free(*m.span()):
            vin_val = m.group(1).upper()
            conditions.append(f"v.vin = '{vin_val}'")
            mark_span(*m.span())

    vin_sub_patterns = [
        r'(?:have|has|with|containing|contains|like)\s+["\']([A-Za-z0-9]{2,17})["\']\s+(?:in\s+(?:the\s+)?vin)',
        r'vin\s+(?:containing|contains|with|like|having)\s+["\']?([A-Za-z0-9]{2,17})["\']?',
        r'["\']([A-Za-z0-9]{3,16})["\']\s+in\s+(?:the\s+)?vin',
    ]
    for pat in vin_sub_patterns:
        for m in re.finditer(pat, raw, re.IGNORECASE):
            if span_free(*m.span()):
                sub = m.group(1).upper()
                conditions.append(f"v.vin LIKE '%{sub}%'")
                mark_span(*m.span())

    # 3. Detect Year ranges and individual 4-digit years
    for m in re.finditer(r"\b(?:between\s+)?(20[12]\d)\s*(?:to|through|and|-)\s*(20[12]\d)\b", raw, re.IGNORECASE):
        if span_free(*m.span()):
            y1, y2 = int(m.group(1)), int(m.group(2))
            conditions.append(f"v.modelYear BETWEEN {min(y1, y2)} AND {max(y1, y2)}")
            mark_span(*m.span())

    for m in re.finditer(r"\b(20[12]\d)\b", raw):
        if span_free(*m.span()):
            # Avoid matching "2026 Indianapolis 500" as modelYear if part of Indy 500 festival phrase
            after = raw[m.end():m.end() + 20].lower()
            if after.startswith(" indianapolis 500") or after.startswith(" indy 500"):
                continue
            years_found.append(int(m.group(1)))
            mark_span(*m.span())
    if len(years_found) == 1:
        conditions.append(f"v.modelYear = {years_found[0]}")
    elif len(years_found) > 1:
        yr_list = ", ".join(str(y) for y in sorted(set(years_found)))
        conditions.append(f"v.modelYear IN ({yr_list})")

    # 4. Detect Special Editions & RPO packages before models/trims so multi-word names don't collide
    special_conditions = []
    has_1le = False
    for pat, se_desc, rpo_code in SPECIAL_EDITION_PATTERNS:
        for m in re.finditer(pat, raw, re.IGNORECASE):
            if span_free(*m.span()):
                if se_desc == "1LE":
                    has_1le = True
                elif se_desc:
                    special_conditions.append(
                        f"EXISTS (SELECT 1 FROM SpecialEditions se WHERE se.vehicle_id = v.vehicle_id AND se.special_desc LIKE '%{se_desc}%')"
                    )
                elif rpo_code:
                    special_conditions.append(
                        f"EXISTS (SELECT 1 FROM Options opt WHERE opt.vehicle_id = v.vehicle_id AND opt.option_code = '{rpo_code}')"
                    )
                mark_span(*m.span())

    # Explicit "RPO <3-char>" or "option <3-char>"
    for m in re.finditer(r"\b(?:rpo|option\s+code|option)\s+([A-Z0-9]{3})\b", raw, re.IGNORECASE):
        if span_free(*m.span()):
            code = m.group(1).upper()
            special_conditions.append(
                f"EXISTS (SELECT 1 FROM Options opt WHERE opt.vehicle_id = v.vehicle_id AND opt.option_code = '{code}')"
            )
            mark_span(*m.span())

    # 5. Detect Combined Model+Trim & Models
    combined_model_trim_patterns = [
        (r"\bct5[\s-]*v(?:\s*-?\s*series)?\s+blackwing(?:s)?\b|\bct5\s+blackwing(?:s)?\b", "CT5", "V-SERIES BLACKWING"),
        (r"\bct4[\s-]*v(?:\s*-?\s*series)?\s+blackwing(?:s)?\b|\bct4\s+blackwing(?:s)?\b", "CT4", "V-SERIES BLACKWING"),
        (r"\bct5[\s-]*v(?:\s*-?\s*series)?\b", "CT5", "V-SERIES"),
        (r"\bct4[\s-]*v(?:\s*-?\s*series)?\b", "CT4", "V-SERIES"),
        (r"\bct6[\s-]*v(?:\s*-?\s*series)?\b", "CT6", "V-SERIES"),
    ]
    for pat, mdl, trm in combined_model_trim_patterns:
        for m in re.finditer(pat, raw, re.IGNORECASE):
            if span_free(*m.span()):
                if mdl not in models_found:
                    models_found.append(mdl)
                if trm not in trims_found:
                    trims_found.append(trm)
                mark_span(*m.span())

    model_patterns = [
        (r"\b(?:corvette\s+)?zr1x(?:s)?\b", "exact", "CORVETTE ZR1X"),
        (r"\b(?:corvette(?:s)?\s+)?zr1(?:s)?\b", "exact", "CORVETTE ZR1"),
        (r"\b(?:corvette(?:s)?\s+)?z06(?:s)?\b", "exact", "CORVETTE Z06"),
        (r"\b(?:corvette(?:s)?\s+)?e[\s-]*ray(?:s)?\b", "exact", "CORVETTE E-RAY"),
        (r"\b(?:corvette\s+)?grand\s+sport\s+x\b", "exact", "CORVETTE GRAND SPORT X"),
        (r"\b(?:corvette\s+)?grand\s+sport(?:s)?\b", "cond", "v.model LIKE 'CORVETTE GRAND SPORT%'"),
        (r"\b(?:corvette\s+)?stingray(?:s)?\b", "cond", "v.model LIKE 'CORVETTE STINGRAY%'"),
        (r"\bc8\s+corvette(?:s)?\b|\bcorvette(?:s)?\s+c8\b|\bc8s?\b", "cond", "(v.model LIKE 'CORVETTE%' AND v.modelYear >= 2020)"),
        (r"\bc7\s+corvette(?:s)?\b|\bcorvette(?:s)?\s+c7\b|\bc7s?\b", "cond", "(v.model LIKE 'CORVETTE%' AND v.modelYear <= 2019)"),
        (r"\bcorvette(?:s)?\b", "cond", "v.model LIKE 'CORVETTE%'"),
        (r"\bescalade\s+iql\b", "exact", "ESCALADE IQL"),
        (r"\bescalade\s+iq\b", "exact", "ESCALADE IQ"),
        (r"\bescalade(?:s)?\b", "exact", "ESCALADE"),
        (r"\bhummer(?:\s+ev)?\s+suv(?:s)?\b", "exact", "HUMMER EV SUV"),
        (r"\bhummer(?:\s+ev)?\s+(?:pickup|truck|sut)(?:s)?\b", "exact", "HUMMER EV PICKUP"),
        (r"\bhummer(?:\s+ev)?(?:s)?\b", "cond", "v.model IN ('HUMMER EV SUV', 'HUMMER EV PICKUP')"),
        (r"\bsierra\s+ev(?:s)?\b", "exact", "SIERRA EV"),
        (r"\bsilverado\s+ev(?:s)?\b", "exact", "SILVERADO EV"),
        (r"\bcamaro(?:s)?\b", "exact", "CAMARO"),
        (r"\bct4(?:s)?\b", "exact", "CT4"),
        (r"\bct5(?:s)?\b", "exact", "CT5"),
        (r"\bct6(?:s)?\b", "exact", "CT6"),
    ]
    model_conds = []
    for pat, kind, val in model_patterns:
        for m in re.finditer(pat, raw, re.IGNORECASE):
            if span_free(*m.span()):
                if kind == "exact":
                    if val not in models_found:
                        models_found.append(val)
                else:
                    if val not in model_conds:
                        model_conds.append(val)
                mark_span(*m.span())

    if len(models_found) == 1 and not model_conds:
        conditions.append(f"v.model = '{models_found[0]}'")
    elif len(models_found) > 1 and not model_conds:
        m_list = ", ".join(f"'{m}'" for m in models_found)
        conditions.append(f"v.model IN ({m_list})")
    elif model_conds and not models_found:
        conditions.extend(model_conds)
    elif models_found and model_conds:
        m_list = [f"v.model = '{m}'" for m in models_found] + model_conds
        conditions.append("(" + " OR ".join(m_list) + ")")

    # 6. Detect Trims
    trim_patterns = [
        (r"\bv[\s-]*series\s+blackwing\b|\bblackwing(?:s)?\b", "V-SERIES BLACKWING"),
        (r"\bv[\s-]*series\b", "V-SERIES"),
        (r"\bpremium\s+luxury\b", "PREMIUM LUXURY"),
        (r"\b1ls\b", "1LS"),
        (r"\b1lt\b", "1LT"),
        (r"\b2lt\b", "2LT"),
        (r"\b3lt\b", "3LT"),
        (r"\blt1\b", "LT1"),
        (r"\b1ss\b", "1SS"),
        (r"\b2ss\b", "2SS"),
        (r"\bzl1\b", "ZL1"),
        (r"\b1lz\b", "1LZ"),
        (r"\b2lz\b", "2LZ"),
        (r"\b3lz\b", "3LZ"),
        (r"\b3x\b", "3X"),
        (r"\b2x\b", "2X"),
    ]
    for pat, trm in trim_patterns:
        for m in re.finditer(pat, raw, re.IGNORECASE):
            if span_free(*m.span()):
                if trm not in trims_found:
                    trims_found.append(trm)
                mark_span(*m.span())

    if len(trims_found) == 1:
        conditions.append(f"v.trim = '{trims_found[0]}'")
    elif len(trims_found) > 1:
        t_list = ", ".join(f"'{t}'" for t in trims_found)
        conditions.append(f"v.trim IN ({t_list})")

    # Resolve 1LE after trims are known
    if has_1le:
        if "ZL1" in trims_found:
            special_conditions.append(
                "(EXISTS (SELECT 1 FROM SpecialEditions se WHERE se.vehicle_id = v.vehicle_id AND se.special_desc LIKE '%1LE%') "
                "OR EXISTS (SELECT 1 FROM Options opt WHERE opt.vehicle_id = v.vehicle_id AND opt.option_code = 'A1Z'))"
            )
        else:
            special_conditions.append(
                "EXISTS (SELECT 1 FROM SpecialEditions se WHERE se.vehicle_id = v.vehicle_id AND se.special_desc LIKE '%1LE%')"
            )
    conditions.extend(special_conditions)

    # 7. Detect Transmissions
    trans_patterns = [
        (r"\b(?:a10|10[\s-]*speed(?:\s+auto(?:matic)?)?)\b", "t.transmission_type = 'A10'"),
        (r"\b(?:a8|8[\s-]*speed(?:\s+auto(?:matic)?)?)\b", "t.transmission_type = 'A8'"),
        (r"\b(?:m6|6[\s-]*speed(?:\s+manual)?)\b", "t.transmission_type = 'M6'"),
        (r"\b(?:m7|7[\s-]*speed(?:\s+manual)?)\b", "t.transmission_type = 'M7'"),
        (r"\b(?:manual(?:\s+transmission|\s+trans)?|stick\s+shift|6mt|7mt)\b", "t.transmission_type LIKE 'M%'"),
        (r"\b(?:automatic(?:\s+transmission|\s+trans)?|auto\s+trans(?:mission)?|auto)\b", "t.transmission_type LIKE 'A%'"),
    ]
    for pat, cond in trans_patterns:
        for m in re.finditer(pat, raw, re.IGNORECASE):
            if span_free(*m.span()):
                if cond not in conditions:
                    conditions.append(cond)
                mark_span(*m.span())

    # 8. Detect Drivetrains & Body styles & Countries
    dt_patterns = [
        (r"\b(?:rwd|rear[\s-]*wheel[\s-]*drive)\b", "d.drivetrain_type = 'RWD'"),
        (r"\b(?:awd|all[\s-]*wheel[\s-]*drive)\b", "d.drivetrain_type = 'AWD'"),
        (r"\b(?:4wd|4x4|four[\s-]*wheel[\s-]*drive)\b", "d.drivetrain_type = '4WD'"),
    ]
    for pat, cond in dt_patterns:
        for m in re.finditer(pat, raw, re.IGNORECASE):
            if span_free(*m.span()):
                conditions.append(cond)
                mark_span(*m.span())

    body_patterns = [
        (r"\bcoupe(?:s)?\b", "COUPE"),
        (r"\bconvertible(?:s)?\b|\bcabriolet(?:s)?\b", "CONVERTIBLE"),
        (r"\bsedan(?:s)?\b", "SEDAN"),
        (r"\bsuv(?:s)?\b", "SUV"),
    ]
    bodies_found = []
    for pat, bval in body_patterns:
        for m in re.finditer(pat, raw, re.IGNORECASE):
            if span_free(*m.span()):
                if bval not in bodies_found:
                    bodies_found.append(bval)
                mark_span(*m.span())
    if len(bodies_found) == 1:
        conditions.append(f"v.body = '{bodies_found[0]}'")
    elif len(bodies_found) > 1:
        b_list = ", ".join(f"'{b}'" for b in bodies_found)
        conditions.append(f"v.body IN ({b_list})")

    country_patterns = [
        (r"\b(?:usa|u\.s\.a\.|united\s+states|us\s+market)\b", "o.country = 'USA'"),
        (r"\b(?:canada|canadian)\b", "o.country = 'CANADA'"),
        (r"\b(?:mexico|mexican)\b", "o.country = 'MEXICO'"),
    ]
    for pat, cond in country_patterns:
        for m in re.finditer(pat, raw, re.IGNORECASE):
            if span_free(*m.span()):
                conditions.append(cond)
                mark_span(*m.span())

    # 9. Detect MSRP comparisons & ordering
    for m in re.finditer(r"\b(?:msrp\s+)?(?:over|above|greater\s+than|more\s+than)\s+\$?([\d,]+)(k)?\b", raw, re.IGNORECASE):
        if span_free(*m.span()):
            val = int(m.group(1).replace(",", "")) * (1000 if m.group(2) else 1)
            conditions.append(f"v.msrp > {val}")
            mark_span(*m.span())

    for m in re.finditer(r"\b(?:msrp\s+)?(?:under|below|less\s+than)\s+\$?([\d,]+)(k)?\b", raw, re.IGNORECASE):
        if span_free(*m.span()):
            val = int(m.group(1).replace(",", "")) * (1000 if m.group(2) else 1)
            conditions.append(f"v.msrp < {val}")
            mark_span(*m.span())

    for m in re.finditer(r"\b(?:most\s+expensive|highest\s+msrp|highest\s+price)\b", raw, re.IGNORECASE):
        if span_free(*m.span()):
            order_by = "ORDER BY v.msrp DESC"
            mark_span(*m.span())

    for m in re.finditer(r"\b(?:least\s+expensive|cheapest|lowest\s+msrp|lowest\s+price)\b", raw, re.IGNORECASE):
        if span_free(*m.span()):
            order_by = "ORDER BY v.msrp ASC"
            mark_span(*m.span())

    # 10. Detect Colors (specific multi-word colors first, then matte/frost, then generic color words)
    colors_matched = []
    for phrase in SPECIFIC_COLOR_PHRASES:
        pat = r"\b" + re.escape(phrase) + r"\b"
        for m in re.finditer(pat, raw, re.IGNORECASE):
            if span_free(*m.span()):
                colors_matched.append(phrase.upper())
                mark_span(*m.span())

    matte_frost_matched = False
    for m in re.finditer(r"\b(?:matte|frost)(?:\s+paint|\s+finish|\s+color)?\b", raw, re.IGNORECASE):
        if span_free(*m.span()):
            matte_frost_matched = True
            mark_span(*m.span())

    generic_colors_matched = []
    for cword in GENERIC_COLOR_WORDS:
        pat = r"\b" + cword + r"\b"
        for m in re.finditer(pat, raw, re.IGNORECASE):
            if span_free(*m.span()):
                norm = "GRAY" if cword == "GREY" else cword
                if norm not in generic_colors_matched:
                    generic_colors_matched.append(norm)
                mark_span(*m.span())

    if len(colors_matched) == 1:
        conditions.append(f"c.color_name LIKE '%{colors_matched[0]}%'")
    elif len(colors_matched) > 1:
        c_or = " OR ".join(f"c.color_name LIKE '%{c}%'" for c in colors_matched)
        conditions.append(f"({c_or})")

    if matte_frost_matched:
        conditions.append("(c.color_name LIKE '%MATTE%' OR c.color_name LIKE '%FROST%')")

    if len(generic_colors_matched) == 1:
        c = generic_colors_matched[0]
        if c == "GRAY":
            conditions.append("(c.color_name LIKE '%GRAY%' OR c.color_name LIKE '%GREY%')")
        else:
            conditions.append(f"c.color_name LIKE '%{c}%'")
    elif len(generic_colors_matched) > 1:
        c_or = " OR ".join(f"c.color_name LIKE '%{c}%'" for c in generic_colors_matched)
        conditions.append(f"({c_or})")

    # Check if any unrecognized non-stopword tokens remain
    unconsumed_chars = "".join(ch if not consumed[i] else " " for i, ch in enumerate(raw))
    leftover_tokens = [
        tok.lower() for tok in re.findall(r"[a-zA-Z0-9]+", unconsumed_chars)
        if tok.lower() not in QUERY_STOPWORDS
    ]
    is_complete = (len(leftover_tokens) == 0) and (len(conditions) > 0 or bool(order_by))

    return {
        "conditions": conditions,
        "mode": mode,
        "distinct_cols": distinct_cols,
        "order_by": order_by,
        "is_complete": is_complete,
        "leftover_tokens": leftover_tokens,
        "models_found": models_found,
        "trims_found": trims_found,
        "years_found": years_found,
    }


def build_sql_from_intent(intent):
    """Construct complete SQL from a fully resolved intent dict."""
    where_clause = "WHERE " + " AND ".join(intent["conditions"]) if intent["conditions"] else ""
    if intent["mode"] == "count":
        joins = []
        if "c." in where_clause:
            joins.append("LEFT JOIN Colors c ON v.color_id = c.color_id")
        if "e." in where_clause:
            joins.append("LEFT JOIN Engines e ON v.engine_id = e.engine_id")
        if "t." in where_clause:
            joins.append("LEFT JOIN Transmissions t ON v.transmission_id = t.transmission_id")
        if "d." in where_clause:
            joins.append("LEFT JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id")
        if "o." in where_clause:
            joins.append("LEFT JOIN Orders o ON v.order_id = o.order_id")
        if "dealer." in where_clause:
            joins.append("LEFT JOIN Dealers dealer ON v.dealer_id = dealer.dealer_id")
        if "m." in where_clause:
            if "o." not in where_clause:
                joins.append("LEFT JOIN Orders o ON v.order_id = o.order_id")
            joins.append("LEFT JOIN MMC_Codes m ON o.mmc_code_id = m.mmc_code_id")
        join_sql = ("\n" + "\n".join(joins)) if joins else ""
        return f"SELECT COUNT(*) AS `Count`\nFROM Vehicles v{join_sql}\n{where_clause}".strip()

    if intent["mode"] == "distinct" and intent["distinct_cols"]:
        select_exprs = ", ".join(expr for expr, _ in intent["distinct_cols"])
        needed_aliases = {alias for _, alias in intent["distinct_cols"]}
        for alias in ("c", "e", "t", "d", "o", "dealer", "m"):
            if f"{alias}." in where_clause:
                needed_aliases.add(alias)
        joins = []
        if "c" in needed_aliases:
            joins.append("LEFT JOIN Colors c ON v.color_id = c.color_id")
        if "e" in needed_aliases:
            joins.append("LEFT JOIN Engines e ON v.engine_id = e.engine_id")
        if "t" in needed_aliases:
            joins.append("LEFT JOIN Transmissions t ON v.transmission_id = t.transmission_id")
        if "d" in needed_aliases:
            joins.append("LEFT JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id")
        if "o" in needed_aliases or "m" in needed_aliases:
            joins.append("LEFT JOIN Orders o ON v.order_id = o.order_id")
        if "dealer" in needed_aliases:
            joins.append("LEFT JOIN Dealers dealer ON v.dealer_id = dealer.dealer_id")
        if "m" in needed_aliases:
            joins.append("LEFT JOIN MMC_Codes m ON o.mmc_code_id = m.mmc_code_id")
        join_sql = ("\n" + "\n".join(joins)) if joins else ""
        return f"SELECT DISTINCT {select_exprs}\nFROM Vehicles v{join_sql}\n{where_clause}\nLIMIT 500".strip()

    return build_full_vehicle_sql(where_clause, intent["order_by"], limit=500)


def sanitize_and_repair_ai_sql(raw_sql, intent):
    """Clean LLM output, expand WHERE-only responses, and repair common 7B hallucinations."""
    text = (raw_sql or "").strip()
    fence_match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()
    text = re.sub(r"^(?:SQL\s*Query|SQL)\s*:\s*", "", text, flags=re.IGNORECASE).strip()
    text = text.rstrip("; \n\t")

    # If the model output a compact WHERE clause, expand it to full vehicle SQL
    if re.match(r"^WHERE\b", text, re.IGNORECASE):
        text = re.sub(r"\s+LIMIT\s+\d+\s*$", "", text, flags=re.IGNORECASE)
        text = build_full_vehicle_sql(text, intent.get("order_by", ""), limit=500)

    # Auto-repair common 7B mistakes using extracted intent
    if intent.get("models_found"):
        # Fix hallucinated CORVETTE% when a non-Corvette model was explicitly requested
        non_corvette = [m for m in intent["models_found"] if not m.startswith("CORVETTE")]
        if non_corvette and re.search(r"v\.model\s+LIKE\s+'CORVETTE%'", text, re.IGNORECASE):
            if len(non_corvette) == 1:
                text = re.sub(r"v\.model\s+LIKE\s+'CORVETTE%'", f"v.model = '{non_corvette[0]}'", text, flags=re.IGNORECASE)
            else:
                m_list = ", ".join(f"'{m}'" for m in non_corvette)
                text = re.sub(r"v\.model\s+LIKE\s+'CORVETTE%'", f"v.model IN ({m_list})", text, flags=re.IGNORECASE)

    if len(intent.get("trims_found", [])) == 1:
        exact_trim = intent["trims_found"][0]
        # Fix stuffed trim like v.trim LIKE '%2SS 1LE A10%'
        text = re.sub(r"v\.trim\s+(?:LIKE|=)\s+'[^']*'", f"v.trim = '{exact_trim}'", text, flags=re.IGNORECASE)

    if len(intent.get("years_found", [])) == 1 and "modelYear" not in text:
        yr = intent["years_found"][0]
        text = re.sub(r"\bWHERE\s+", f"WHERE v.modelYear = {yr} AND ", text, count=1, flags=re.IGNORECASE)

    return text


@app.route('/ai-query', methods=['POST'])
def natural_language_query():
    data = request.json or {}
    user_prompt = data.get('prompt', '').strip()
    
    if not user_prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    cache_key = user_prompt.lower()
    now = time.time()
    cached_entry = AI_SQL_CACHE.get(cache_key)
    if cached_entry and (now - cached_entry['time'] < AI_SQL_CACHE_TTL):
        generated_sql = cached_entry['sql']
    else:
        intent = parse_nl_query_intent(user_prompt)

        if intent["is_complete"]:
            # Fast-path: 100% of tokens mapped to exact schema predicates (< 1ms)
            generated_sql = build_sql_from_intent(intent)
        else:
            # Fallback to Ollama with pre-resolved entity hints and compact WHERE output
            hint_block = ""
            if intent["conditions"]:
                hint_block = "\nMatched Filter Hints (MUST include in WHERE): " + " AND ".join(intent["conditions"])
            system_combined_prompt = f"{DB_SCHEMA_CONTEXT}{hint_block}\nUser Request: {user_prompt}\nSQL Query:"

            payload = {
                "model": AI_MODEL,
                "prompt": system_combined_prompt,
                "stream": False,
                "keep_alive": -1,
                "options": {
                    "temperature": 0.0,
                    "num_ctx": 2048,
                    "num_predict": 256,
                    "stop": [";", "\n\n", "User Request:"]
                }
            }

            try:
                response = requests.post(OLLAMA_URL, json=payload, timeout=120)
                response.raise_for_status()
                generated_sql = sanitize_and_repair_ai_sql(response.json().get('response', ''), intent)
            except Exception as e:
                app.logger.error("Failed to communicate with AI model: %s", e)
                return jsonify({'error': 'Failed to communicate with AI model'}), 500

        AI_SQL_CACHE[cache_key] = {'time': now, 'sql': generated_sql}

    unquoted_sql = re.sub(r"'(?:\\.|''|[^'])*'", "''", generated_sql)
    destructive_pattern = re.compile(
        r"\b(drop|delete|truncate|update|alter|insert|grant|create|replace|call|exec)\b",
        re.IGNORECASE
    )
    if not re.match(r"^(SELECT|WITH)\b", generated_sql, re.IGNORECASE) or ";" in unquoted_sql or destructive_pattern.search(unquoted_sql):
        return jsonify({'error': 'Security restriction: Only single read-only SELECT queries are permitted', 'generated_sql': generated_sql}), 403

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    try:
        db_results = execute_read_query(conn, generated_sql)
        if db_results is None:
            close_connection(conn)
            return jsonify({
                'error': 'AI generated invalid SQL syntax or execution failed.', 
                'generated_sql': generated_sql
            }), 400
            
    except Exception as e:
        app.logger.error("AI SQL execution error: %s", e)
        close_connection(conn)
        return jsonify({
            'error': 'Execution error', 
            'generated_sql': generated_sql, 
            'details': 'An error occurred while executing the generated SQL query.'
        }), 400
    
    close_connection(conn)

    return jsonify({
        'generated_sql': generated_sql,
        'results': db_results
    })

#========================= View Pages #=========================

@app.route('/search', methods=['GET'])
def search_inv():
    vin = request.args.get('vin')
    join_clause = """
        JOIN Engines e ON v.engine_id = e.engine_id
        JOIN Transmissions t ON v.transmission_id = t.transmission_id
        JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
        JOIN Colors c ON v.color_id = c.color_id
        JOIN Orders o ON v.order_id = o.order_id
        JOIN Dealers dl ON v.dealer_id = dl.dealer_id
        LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id
        LEFT JOIN Options opt ON v.vehicle_id = opt.vehicle_id
        LEFT JOIN MMC_Codes mc ON o.mmc_code_id = mc.mmc_code_id
    """
    sqlStatement = f"""
        SELECT v.vin, v.modelYear, v.model, v.body, v.trim, e.engine_type,
               t.transmission_type, d.drivetrain_type, c.color_name, v.msrp,
               o.country, o.order_number, mc.mmc_code,
               UPPER(DATE_FORMAT(o.creation_date, '%%W, %%d %%M %%Y')) AS formatted_date,
               dl.dealer_name, dl.location,
               se.special_desc,
               opt.option_code
        FROM Vehicles v
        {join_clause}
        WHERE v.vin = %s
    """
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    rows = execute_read_query(conn, sqlStatement, (vin,))
    close_connection(conn)

    if not rows:
        return jsonify([])

    vehicle = {}
    rpo_codes = []
    special_descs = []

    for row in rows:
        if not vehicle:
            vehicle = {
                'vin': row['vin'],
                'modelYear': row['modelYear'],
                'model': row['model'],
                'body': row['body'],
                'trim': row['trim'],
                'engine_type': row['engine_type'],
                'transmission_type': row['transmission_type'],
                'drivetrain_type': row['drivetrain_type'],
                'color_name': row['color_name'],
                'msrp': row['msrp'],
                'country': row['country'],
                'order_number': row['order_number'],
                'mmc_code': row['mmc_code'],
                'formatted_date': row['formatted_date'],
                'dealer_name': row['dealer_name'],
                'location': row['location']
            }

        if row['option_code']:
            rpo_codes.append(row['option_code'])
        if row['special_desc']:
            special_descs.append(row['special_desc'])

    vehicle['rpo_codes'] = sorted(set(rpo_codes))
    vehicle['special_descs'] = ', '.join(sorted(set(special_descs))) if special_descs else 'NA'

    return jsonify([vehicle])

@app.route('/vehicles', methods=['GET'])
def sort_price():
    year = request.args.get('year')
    body = request.args.get('body')
    trim = request.args.get('trim')
    engine = request.args.get('engine')
    trans = request.args.get('trans')
    drivetrain = request.args.get('drivetrain')
    models_list = request.args.getlist('model') or request.args.getlist('model[]')
    rpo = request.args.get('rpo')
    color = request.args.get('color')
    country = request.args.get('country')
    date = request.args.get('date')
    order = request.args.get('order')
    page = request.args.get('page', 1)
    state = request.args.get('state')
    city = request.args.get('city')
    dealer = request.args.get('dealer')
    dealer_id = request.args.get('dealer_id')
    dealer_name = request.args.get('dealer_name')
    
    limit = 100
    try:
        page = int(page)
        offset = (page - 1) * limit
    except (ValueError, TypeError):
        page = 1
        offset = 0

    rpo_list = []
    rpo_list_for_filtering = []
    rpo_n = 0
    conditions = []
    params = []

    country_map = {
        "CAN": "CANADA",
        "MEX": "MEXICO"
    }

    if year:
        conditions.append("v.modelYear = %s")
        params.append(year)
    if models_list:
        if "CORVETTE (C8)" in models_list:
            models_list.remove("CORVETTE (C8)")
            c8_cond = "(v.model LIKE 'CORVETTE%%' AND v.modelYear >= '2020')"
            if models_list:
                placeholders = ', '.join(['%s'] * len(models_list))
                conditions.append(f"({c8_cond} OR v.model IN ({placeholders}))")
                params.extend(models_list)
            else:
                conditions.append(c8_cond)
        else:
            placeholders = ', '.join(['%s'] * len(models_list))
            conditions.append(f"v.model IN ({placeholders})")
            params.extend(models_list)
    if body:
        conditions.append("v.body = %s")
        params.append(body)
    if trim:
        conditions.append("v.trim = %s")
        params.append(trim)
    if engine:
        conditions.append("v.engine_id = (SELECT engine_id FROM Engines WHERE engine_type = %s LIMIT 1)")
        params.append(engine)
    if trans:
        conditions.append("v.transmission_id = (SELECT transmission_id FROM Transmissions WHERE transmission_type = %s LIMIT 1)")
        params.append(trans)
    if drivetrain:
        conditions.append("v.drivetrain_id = (SELECT drivetrain_id FROM Drivetrains WHERE drivetrain_type = %s LIMIT 1)")
        params.append(drivetrain)
    if color:
        conditions.append("v.color_id = (SELECT color_id FROM Colors WHERE color_name = %s LIMIT 1)")
        params.append(color)
    if country:
        conditions.append("o.country = %s")
        params.append(country_map.get(country, 'USA'))
    if date:
        d_cond, d_params = build_creation_date_cond(date)
        conditions.append(d_cond)
        params.extend(d_params)

    if state:
        if state.upper() == 'OTHER':
            conditions.append("(dl.location IS NULL OR dl.location NOT LIKE '%%,%%')")
        else:
            conditions.append("TRIM(SUBSTRING_INDEX(TRIM(SUBSTRING_INDEX(dl.location, ',', -1)), ' ', 1)) = %s")
            params.append(state.strip().upper())

    if city:
        if city.upper() == 'UNKNOWN':
            conditions.append("(dl.location IS NULL OR TRIM(dl.location) = '')")
        else:
            conditions.append("TRIM(SUBSTRING_INDEX(dl.location, ',', 1)) = %s")
            params.append(city.strip().upper())

    if dealer_id:
        d_ids = [int(x.strip()) for x in str(dealer_id).split(',') if x.strip().isdigit()]
        if len(d_ids) == 1:
            conditions.append("v.dealer_id = %s")
            params.append(d_ids[0])
        elif len(d_ids) > 1:
            placeholders = ', '.join(['%s'] * len(d_ids))
            conditions.append(f"v.dealer_id IN ({placeholders})")
            params.extend(d_ids)
    elif dealer:
        if str(dealer).strip().isdigit():
            conditions.append("v.dealer_id = %s")
            params.append(int(dealer))
        elif ',' in str(dealer) and all(x.strip().isdigit() for x in str(dealer).split(',') if x.strip()):
            d_ids = [int(x.strip()) for x in str(dealer).split(',') if x.strip().isdigit()]
            placeholders = ', '.join(['%s'] * len(d_ids))
            conditions.append(f"v.dealer_id IN ({placeholders})")
            params.extend(d_ids)
        else:
            conditions.append("dl.dealer_name = %s")
            params.append(dealer.strip())
    elif dealer_name:
        conditions.append("dl.dealer_name = %s")
        params.append(dealer_name.strip())

    if rpo:
        rpo_list = rpo.split(',') if ',' in rpo else [rpo]
        
        rpo_conditions = {
            "Z4B": ["v.modelYear = '2024'", "v.model = 'CAMARO'", "v.color_id IN (SELECT color_id FROM Colors WHERE color_name IN ('PANTHER BLACK MATTE', 'PANTHER BLACK METALLIC TINTCOAT'))"],
            "ZL4B": ["v.modelYear = '2024'", "v.model = 'CAMARO'", "v.trim = 'ZL1'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'PANTHER BLACK MATTE' LIMIT 1)"],
            "X56": ["v.modelYear = '2024'", "v.model = 'CAMARO'", "v.body = 'COUPE'", "v.trim = 'ZL1'", "v.transmission_id = (SELECT transmission_id FROM Transmissions WHERE transmission_type = 'M6' LIMIT 1)", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'RIPTIDE BLUE METALLIC' LIMIT 1)", "v.msrp = '89185'"],
            "A1Z": ["v.model = 'CAMARO'", "v.body = 'COUPE'", "v.trim = 'ZL1'"],
            "A1Y": ["v.model = 'CAMARO'", "v.body = 'COUPE'", "v.trim IN ('1SS', '2SS')"],
            "A1X": ["v.modelYear IN ('2019', '2020', '2021')", "v.model = 'CAMARO'", "v.body = 'COUPE'", "v.trim IN ('1LT', '2LT', '3LT')"],
            "H40": ["((v.modelYear = '2024' AND v.model = 'CAMARO' AND v.trim = '2SS' AND v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'RADIANT RED TINTCOAT' LIMIT 1) AND opt.option_code = 'SL1') OR v.vin IN ('1G1FK1R65R0117449', '1G1FK3D62R0118478'))"],
            "PEH": ["v.modelYear = '2020'", "v.model = 'CAMARO'", "v.body = 'COUPE'", "v.trim IN ('2SS', 'ZL1')", "v.transmission_id = (SELECT transmission_id FROM Transmissions WHERE transmission_type = 'A10' LIMIT 1)", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'BLACK' LIMIT 1)"],
            "INDY26": ["EXISTS (SELECT 1 FROM SpecialEditions se WHERE se.vehicle_id = v.vehicle_id AND se.special_desc = '2026 Indianapolis 500 Festival Vehicle')"],
            "Z4Z": ["v.model = 'CAMARO'", "v.body = 'CONVERTIBLE'", "v.trim = '2SS'", "v.color_id IN (SELECT color_id FROM Colors WHERE color_name IN ('WILD CHERRY TINTCOAT', 'SUMMIT WHITE', 'SHARKSKIN METALLIC', 'SATIN STEEL GRAY METALLIC'))"],
            "WBL": ["v.modelYear IN ('2020', '2021', '2022', '2023', '2024')", "v.model = 'CAMARO'", "v.trim NOT IN ('ZL1', '1LS')", "v.color_id IN (SELECT color_id FROM Colors WHERE color_name IN ('BLACK', 'SUMMIT WHITE', 'SHARKSKIN METALLIC', 'SATIN STEEL GRAY METALLIC'))"],
            "B2E": ["v.model = 'CAMARO'", "v.trim IN ('2LT', '2SS', '3LT')", "v.modelYear IN ('2020', '2021', '2022', '2023')", "v.color_id IN (SELECT color_id FROM Colors WHERE color_name IN ('BLACK', 'SUMMIT WHITE', 'RAPID BLUE', 'SHARKSKIN METALLIC', 'SATIN STEEL GRAY METALLIC', 'SHOCK'))"],
            "ZCR": ["v.model = 'CORVETTE STINGRAY'", "v.modelYear = '2022'", "v.trim = '3LT'", "v.color_id IN (SELECT color_id FROM Colors WHERE color_name IN ('HYPERSONIC GRAY METALLIC', 'ACCELERATE YELLOW METALLIC'))"],
            "ZTK": ["v.model IN ('CORVETTE ZR1', 'CORVETTE ZR1X')", "v.modelYear IN ('2019', '2025', '2026', '2027')"],
            "Z07": ["v.model = 'CORVETTE Z06'"],
            "Z51": ["v.model = 'CORVETTE STINGRAY'"],
            "Z25": ["v.model = 'CORVETTE GRAND SPORT'"],
            "FEB": ["v.model = 'CORVETTE GRAND SPORT'"],
            "FEY": ["v.model = 'CORVETTE GRAND SPORT'"],
            "Y70": ["v.model IN ('CORVETTE STINGRAY', 'CORVETTE Z06')", "v.modelYear = '2023'", "v.trim IN ('3LT', '3LZ')", "v.color_id IN (SELECT color_id FROM Colors WHERE color_name IN ('WHITE PEARL METALLIC TRICOAT', 'CARBON FLASH METALLIC'))"],
            "I26": ["v.model = 'CORVETTE E-RAY'", "v.modelYear = '2026'", "v.trim = '3LZ'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'ARCTIC WHITE' LIMIT 1)", "o.country = 'USA'", "v.body = 'CONVERTIBLE'", "v.msrp = '160835'"],
            "USA": ["v.model IN ('CORVETTE STINGRAY', 'CORVETTE Z06', 'CORVETTE E-RAY', 'CORVETTE ZR1', 'CORVETTE ZR1X')", "v.modelYear = '2026'", "v.trim IN ('3LT', '3LZ')", "v.color_id IN (SELECT color_id FROM Colors WHERE color_name IN ('ARCTIC WHITE', 'BLACK'))"],
            "ZRA": ["v.model = 'CORVETTE ZR1X'", "v.modelYear = '2026'", "v.trim = '3LZ'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'BLADE SILVER MATTE' LIMIT 1)"],
            "ZLE": ["v.modelYear = '2023'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'ELECTRIC BLUE' LIMIT 1)"],
            "ZLD": ["v.modelYear = '2023'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'MAVERICK NOIR FROST' LIMIT 1)"],
            "ZLG": ["v.modelYear = '2023'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'RIFT METALLIC' LIMIT 1)"],
            "ZLK": ["v.modelYear = '2024'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'MERCURY SILVER METALLIC' LIMIT 1)"],
            "ZLJ": ["v.modelYear = '2024'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'BLACK RAVEN' LIMIT 1)"],
            "ZLR": ["v.modelYear = '2024'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'VELOCITY RED' LIMIT 1)"],
            "ZLZ4": ["v.modelYear = '2025'", "v.model ='CT4'", "v.trim = 'V-SERIES BLACKWING'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'MAGNUS METAL FROST' LIMIT 1)"],
            "ZLZ5": ["v.modelYear = '2025'", "v.model ='CT5'", "v.trim = 'V-SERIES BLACKWING'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'MAGNUS METAL FROST' LIMIT 1)"],
            "WOX": ["v.modelYear = '2026'", "v.model ='CT5'", "v.trim = 'V-SERIES BLACKWING'"],
            "ABQ": ["v.modelYear = '2023'", "v.model = 'CT5'", "v.trim = 'V-SERIES BLACKWING'", "v.msrp > '118000'"],
            "ZLT": ["v.modelYear = '2024'", "v.model = 'CT5'", "v.trim = 'V-SERIES BLACKWING'", "opt.option_code IN ('ZLT', 'ZLV')"],
            "V8V": ["v.model = 'CT5'", "v.trim = 'V-SERIES BLACKWING'"],
            "PCK1": ["v.modelYear = '2026'", "v.model = 'CT5'", "v.trim = 'V-SERIES BLACKWING'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'DEEP OCEAN TINTCOAT' LIMIT 1)"],
            "Z6X": ["v.model IN ('HUMMER EV SUV', 'HUMMER EV PICKUP')"],
            "WFP": ["v.modelYear = '2024'", "v.model = 'HUMMER EV SUV'", "v.trim = '3X'", "v.color_id = (SELECT color_id FROM Colors WHERE color_name = 'NEPTUNE BLUE MATTE' LIMIT 1)"],
        }

        for rpo_code in rpo_list:
            if rpo_code in rpo_conditions:
                conditions.extend(rpo_conditions[rpo_code])

        substitution_map = {
            'ZL4B': 'Z4B',
            'ZLZ4': 'ZLZ',
            'ZLZ5': 'ZLZ',
            'PCK1': 'PCK',
            "I26": "R7V",
        }

        for code in rpo_list:
            if code in substitution_map:
                rpo_list_for_filtering.append(substitution_map[code])
            elif code not in ['H40', 'ZLT']:
                rpo_list_for_filtering.append(code)

        rpo_list_for_filtering = list(set(rpo_list_for_filtering))
        rpo_n = len(rpo_list_for_filtering)

        if len(rpo_list_for_filtering) > 1:
            placeholders = ', '.join(['%s'] * len(rpo_list_for_filtering))
            conditions.append(f"opt.option_code IN ({placeholders})")
            params.extend(rpo_list_for_filtering)
        elif len(rpo_list_for_filtering) == 1:
            conditions.append("opt.option_code = %s")
            params.append(rpo_list_for_filtering[0])

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    needs_group_by = bool(rpo and (rpo_n > 1 or 'ZLT' in rpo_list or 'H40' in rpo_list))
    if rpo_n > 1 and 'H40' not in rpo_list:
        rpo_clause = f"HAVING COUNT(DISTINCT opt.option_code) = {rpo_n}"
    else:
        rpo_clause = ""

    if any(code in ["ZL4B", "X56", "PEH"] for code in rpo_list) and order not in ["ASC", "DESC"]:
        order_clause = "ORDER BY SUBSTRING(v.vin, -6)"
    elif order in ["ASC", "DESC"]:
        order_clause = f"ORDER BY v.msrp {'ASC' if order == 'ASC' else 'DESC'}"
    elif order in ["vinASC", "vinDESC"]:
        order_clause = f"ORDER BY SUBSTRING(v.vin, -6) {'DESC' if order == 'vinDESC' else 'ASC'}, v.modelYear ASC"
    else:
        order_clause = "ORDER BY v.vehicle_id DESC"

    # Build minimal joins containing ONLY tables actually referenced in where_clause
    minimal_joins = []
    if "o." in where_clause:
        minimal_joins.append("JOIN Orders o ON v.order_id = o.order_id")
    if "dl." in where_clause:
        minimal_joins.append("JOIN Dealers dl ON v.dealer_id = dl.dealer_id")
    if "opt." in where_clause or rpo_clause:
        minimal_joins.append("JOIN Options opt ON v.vehicle_id = opt.vehicle_id")
    minimal_join_clause = "\n        ".join(minimal_joins)
    inner_group_by = "GROUP BY v.vehicle_id" if needs_group_by else ""

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

    def get_all_distinct_values(db_conn, current_where, current_params, current_rpo_clause):
        if not current_where:
            veh_distinct = execute_read_query(db_conn, "SELECT DISTINCT modelYear, model, body, trim FROM Vehicles") or []
            engines = execute_read_query(db_conn, "SELECT engine_rpo AS rpo, engine_type AS name FROM Engines ORDER BY engine_rpo ASC")
            trans = execute_read_query(db_conn, "SELECT DISTINCT transmission_type FROM Transmissions ORDER BY transmission_type ASC")
            drivetrains = execute_read_query(db_conn, "SELECT DISTINCT drivetrain_type FROM Drivetrains ORDER BY drivetrain_type ASC")
            colors = execute_read_query(db_conn, "SELECT DISTINCT color_name FROM Colors ORDER BY color_name ASC")
            countries = execute_read_query(db_conn, "SELECT DISTINCT country FROM Orders ORDER BY country ASC")

            years_set = {r['modelYear'] for r in veh_distinct if r.get('modelYear') is not None}
            models_set = {r['model'] for r in veh_distinct if r.get('model') is not None}
            bodies_set = {r['body'] for r in veh_distinct if r.get('body') is not None}
            trims_set = {r['trim'] for r in veh_distinct if r.get('trim') is not None}

            return {
                'modelYear': sorted(years_set, reverse=True),
                'model': sorted(models_set),
                'body': sorted(bodies_set),
                'trim': sorted(trims_set),
                'transmission_type': [r['transmission_type'] for r in trans],
                'drivetrain_type': [r['drivetrain_type'] for r in drivetrains],
                'color_name': [r['color_name'] for r in colors],
                'country': [r['country'] for r in countries]
            }, engines

        else:
            columns = ['modelYear', 'body', 'trim', 'transmission_type', 'drivetrain_type', 'model', 'color_name', 'country']
            distinct_values = {col: set() for col in columns}
            distinct_engines = set()

            if needs_group_by:
                sqlStatement = f"""
                    SELECT DISTINCT v.modelYear, v.model, v.body, v.trim, e.engine_type, e.engine_rpo,
                                    t.transmission_type, d.drivetrain_type, c.color_name, o.country
                    FROM (
                        SELECT v.vehicle_id
                        FROM Vehicles v
                        {minimal_join_clause}
                        {current_where}
                        GROUP BY v.vehicle_id
                        {current_rpo_clause}
                    ) AS filtered_ids
                    JOIN Vehicles v ON v.vehicle_id = filtered_ids.vehicle_id
                    JOIN Engines e ON v.engine_id = e.engine_id
                    JOIN Transmissions t ON v.transmission_id = t.transmission_id
                    JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
                    JOIN Colors c ON v.color_id = c.color_id
                    JOIN Orders o ON v.order_id = o.order_id
                """
                results = execute_read_query(db_conn, sqlStatement, current_params) or []
                for result in results:
                    for col in columns:
                        if result.get(col) is not None:
                            distinct_values[col].add(result[col])
                    if result.get('engine_type') is not None:
                        distinct_engines.add((result['engine_rpo'], result['engine_type']))
            else:
                sqlStatement = f"""
                    SELECT
                        vc.modelYear, vc.model, vc.body, vc.trim,
                        e.engine_type, e.engine_rpo,
                        t.transmission_type, d.drivetrain_type, c.color_name
                    FROM (
                        SELECT DISTINCT v.modelYear, v.model, v.body, v.trim,
                                        v.engine_id, v.transmission_id, v.drivetrain_id, v.color_id
                        FROM Vehicles v
                        {minimal_join_clause}
                        {current_where}
                    ) AS vc
                    JOIN Engines e ON vc.engine_id = e.engine_id
                    JOIN Transmissions t ON vc.transmission_id = t.transmission_id
                    JOIN Drivetrains d ON vc.drivetrain_id = d.drivetrain_id
                    JOIN Colors c ON vc.color_id = c.color_id
                """
                results = execute_read_query(db_conn, sqlStatement, current_params) or []
                for result in results:
                    for col in ['modelYear', 'body', 'trim', 'transmission_type', 'drivetrain_type', 'model', 'color_name']:
                        if result.get(col) is not None:
                            distinct_values[col].add(result[col])
                    if result.get('engine_type') is not None:
                        distinct_engines.add((result['engine_rpo'], result['engine_type']))

                if results:
                    if country:
                        distinct_values['country'].add(country_map.get(country, 'USA'))
                    elif "o.country = 'USA'" in current_where:
                        distinct_values['country'].add('USA')
                    else:
                        non_order_joins = "\n                            ".join([j for j in minimal_joins if "Orders o" not in j])
                        country_sql = f"""
                            (SELECT 'CANADA' AS country
                             FROM Vehicles v
                             {non_order_joins}
                             STRAIGHT_JOIN Orders o ON v.order_id = o.order_id
                             {current_where}
                             AND o.country = 'CANADA'
                             LIMIT 1)
                            UNION ALL
                            (SELECT 'MEXICO' AS country
                             FROM Orders o
                             STRAIGHT_JOIN Vehicles v ON v.order_id = o.order_id
                             {non_order_joins}
                             {current_where}
                             AND o.country = 'MEXICO'
                             LIMIT 1)
                            UNION ALL
                            (SELECT 'USA' AS country
                             FROM Vehicles v
                             {non_order_joins}
                             STRAIGHT_JOIN Orders o ON v.order_id = o.order_id
                             {current_where}
                             AND o.country = 'USA'
                             LIMIT 1)
                        """
                        c_rows = execute_read_query(db_conn, country_sql, current_params * 3) or []
                        for r in c_rows:
                            if r.get('country') is not None:
                                distinct_values['country'].add(r['country'])

            sorted_values = {
                'modelYear': sorted(list(distinct_values['modelYear']), reverse=True),
                **{col: sorted(list(distinct_values[col])) for col in columns if col != 'modelYear'}
            }
            sorted_engines = [
                {'rpo': rpo, 'name': name}
                for rpo, name in sorted(list(distinct_engines), key=lambda x: x[0] or "")
            ]
            return sorted_values, sorted_engines

    cache_key = (where_clause, tuple(params), rpo_clause)
    now_ts = time.time()
    cached_meta = _VEHICLE_FILTER_CACHE.get(cache_key)
    if cached_meta and (now_ts - cached_meta[0]) < _VEHICLE_FILTER_CACHE_TTL:
        distinct_values, engine_list, total_items = cached_meta[1], cached_meta[2], cached_meta[3]
    else:
        distinct_values, engine_list = get_all_distinct_values(conn, where_clause, params, rpo_clause)
        if where_clause:
            if needs_group_by:
                totalSql = f"""
                    SELECT COUNT(*) AS total FROM (
                        SELECT v.vehicle_id 
                        FROM Vehicles v {minimal_join_clause}
                        {where_clause}
                        GROUP BY v.vehicle_id {rpo_clause}
                    ) AS filtered_vehicles
                """
            else:
                totalSql = f"""
                    SELECT COUNT(v.vehicle_id) AS total
                    FROM Vehicles v {minimal_join_clause}
                    {where_clause}
                """
            total_items = execute_read_query(conn, totalSql, params)[0]['total']
        else:
            total_items = execute_read_query(conn, "SELECT COUNT(vehicle_id) AS total FROM Vehicles")[0]['total']

        if len(_VEHICLE_FILTER_CACHE) > 256:
            _VEHICLE_FILTER_CACHE.clear()
        _VEHICLE_FILTER_CACHE[cache_key] = (now_ts, distinct_values, engine_list, total_items)

    year_list = distinct_values['modelYear']
    body_list = distinct_values['body']
    trim_list = distinct_values['trim']
    trans_list = distinct_values['transmission_type']
    drivetrain_list = distinct_values['drivetrain_type']
    model_list = distinct_values['model']
    color_list = distinct_values['color_name']
    country_list = distinct_values['country']
    
    inner_sql = f"""
        SELECT v.vehicle_id
        FROM Vehicles v {minimal_join_clause}
        {where_clause}
        {inner_group_by}
        {rpo_clause}
        {order_clause}
        LIMIT %s OFFSET %s
    """

    select = f"""
        SELECT STRAIGHT_JOIN
            v.vehicle_id, v.vin, v.modelYear, v.model, v.body, v.trim,
            e.engine_type, t.transmission_type, d.drivetrain_type,
            c.color_name, v.msrp, o.country, dl.dealer_name, dl.location,
            (SELECT GROUP_CONCAT(se.special_desc ORDER BY se.special_desc ASC SEPARATOR ', ')
             FROM SpecialEditions se
             WHERE se.vehicle_id = v.vehicle_id) AS special_desc
        FROM (
            {inner_sql}
        ) AS page_keys
        JOIN Vehicles v ON v.vehicle_id = page_keys.vehicle_id
        JOIN Engines e ON v.engine_id = e.engine_id
        JOIN Transmissions t ON v.transmission_id = t.transmission_id
        JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
        JOIN Colors c ON v.color_id = c.color_id
        JOIN Orders o ON v.order_id = o.order_id
        LEFT JOIN Dealers dl ON v.dealer_id = dl.dealer_id
        {order_clause}
    """

    query_params = params + [limit, offset]
    viewTable = execute_read_query(conn, select, query_params)

    close_connection(conn)

    return jsonify({
        'data': viewTable,
        'total': total_items,
        'year': year_list,
        'model': model_list,
        'body': body_list,
        'trim': trim_list,
        'engine': engine_list,
        'trans': trans_list,
        'drivetrain': drivetrain_list,
        'color': color_list,
        'country': country_list,
        'limit': limit
    })

@app.route('/calendar-activity', methods=['GET'])
def calendar_activity():
    year = request.args.get('year')
    model_filter = request.args.get('model')
    category = request.args.get('category', 'daily')
    
    if category != 'yearly' and not year:
        return jsonify({'error': 'Year required'}), 400

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    
    params = []
    model_join = ""
    model_cond = ""
    
    if model_filter:
        model_join = "JOIN Vehicles v ON o.order_id = v.order_id"
        if model_filter == 'CORVETTE (C8)':
            model_cond = "AND v.model LIKE %s AND v.modelYear >= '2020'"
            params.append('CORVETTE%')
        else:
            model_cond = "AND v.model = %s"
            params.append(model_filter)

    # --- NEW: Order Type Logic ---
    order_type_filter = request.args.get('orderType')
    order_cond = ""
    if order_type_filter == 'retail':
        order_cond = " AND EXISTS (SELECT 1 FROM Options opt WHERE opt.vehicle_id = v.vehicle_id AND opt.option_code = 'SLL')"
    elif order_type_filter == 'stock':
        order_cond = " AND EXISTS (SELECT 1 FROM Options opt WHERE opt.vehicle_id = v.vehicle_id AND opt.option_code = 'SLM')"
        
    # Ensure Vehicles table is joined if EITHER model_filter OR order_cond is active
    if model_filter or order_cond:
        model_join = "JOIN Vehicles v ON o.order_id = v.order_id"
    # -----------------------------
            
    if category == 'yearly':
        sqlStatement = f"""
            SELECT CAST(YEAR(o.creation_date) AS CHAR) as prod_date, COUNT(o.order_id) as count
            FROM Orders o
            {model_join}
            WHERE o.creation_date IS NOT NULL {model_cond} {order_cond}
            GROUP BY prod_date
        """
    elif category == 'monthly':
        d_cond, d_params = build_creation_date_cond(str(year), 'yearly')
        sqlStatement = f"""
            SELECT DATE_FORMAT(o.creation_date, '%%Y-%%m') as prod_date, COUNT(o.order_id) as count
            FROM Orders o
            {model_join}
            WHERE {d_cond} {model_cond} {order_cond}
            GROUP BY prod_date
        """
        params = d_params + params
    else:
        d_cond, d_params = build_creation_date_cond(str(year), 'yearly')
        sqlStatement = f"""
            SELECT DATE_FORMAT(o.creation_date, '%%Y-%%m-%%d') as prod_date, COUNT(o.order_id) as count
            FROM Orders o
            {model_join}
            WHERE {d_cond} {model_cond} {order_cond}
            GROUP BY prod_date
        """
        params = d_params + params
    
    rows = execute_read_query(conn, sqlStatement, params)
    close_connection(conn)
    
    activity_map = {r['prod_date']: r['count'] for r in rows} if rows else {}
    return jsonify(activity_map)

@app.route('/daily-stats', methods=['GET'])
def daily_stats():
    model_filter = request.args.get('model')
    date_filter = request.args.get('date')
    category = request.args.get('category', 'daily')
    model_year_filter = request.args.get('modelYear') # NEW: Capture modelYear param
    trim_filter = request.args.get('trim') # NEW: Capture trim param
    
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    from datetime import date
    
    # NEW: Get all available model years for the dropdown
    my_sql = "SELECT DISTINCT modelYear FROM Vehicles WHERE modelYear IS NOT NULL ORDER BY modelYear DESC"
    my_rows = execute_read_query(conn, my_sql)
    available_model_years = [str(r['modelYear']) for r in my_rows] if my_rows else []

    bounds_params = []
    if model_filter:
        if model_filter == 'CORVETTE (C8)':
            bounds_sql = "SELECT DATE_FORMAT(MIN(o.creation_date), '%%Y-%%m-%%d') as min_date, DATE_FORMAT(MAX(o.creation_date), '%%Y-%%m-%%d') as max_date FROM Orders o JOIN Vehicles v ON o.order_id = v.order_id WHERE v.model LIKE %s AND v.modelYear >= '2020' AND o.creation_date IS NOT NULL"
            bounds_params.append('CORVETTE%')
        else:
            bounds_sql = "SELECT DATE_FORMAT(MIN(o.creation_date), '%%Y-%%m-%%d') as min_date, DATE_FORMAT(MAX(o.creation_date), '%%Y-%%m-%%d') as max_date FROM Orders o JOIN Vehicles v ON o.order_id = v.order_id WHERE v.model = %s AND o.creation_date IS NOT NULL"
            bounds_params.append(model_filter)
    else:
        bounds_sql = "SELECT DATE_FORMAT(MIN(creation_date), '%Y-%m-%d') as min_date, DATE_FORMAT(MAX(creation_date), '%Y-%m-%d') as max_date FROM Orders WHERE creation_date IS NOT NULL"
        bounds_params = None
    
    bounds_rows = execute_read_query(conn, bounds_sql, bounds_params)
    min_date = bounds_rows[0]['min_date'] if bounds_rows else None
    max_date = bounds_rows[0]['max_date'] if bounds_rows else None

    curr_date_str = date_filter or max_date or date.today().strftime('%Y-%m-%d')
    
    # --- NEW: Order Type Filter Logic ---
    order_type_filter = request.args.get('orderType')
    order_cond = ""
    if order_type_filter == 'retail':
        order_cond = " AND EXISTS (SELECT 1 FROM Options opt WHERE opt.vehicle_id = v.vehicle_id AND opt.option_code = 'SLL')"
    elif order_type_filter == 'stock':
        order_cond = " AND EXISTS (SELECT 1 FROM Options opt WHERE opt.vehicle_id = v.vehicle_id AND opt.option_code = 'SLM')"
    # ------------------------------------

    if model_year_filter:
        date_condition = "v.modelYear = %s"
        base_params = [model_year_filter]
    else:
        if category == 'monthly':
            date_condition, base_params = build_creation_date_cond(curr_date_str, 'monthly')
        elif category == 'yearly':
            date_condition, base_params = build_creation_date_cond(curr_date_str, 'yearly')
        else:
            date_condition, base_params = build_creation_date_cond(curr_date_str, 'daily')

    models_sql = f"""
        SELECT DISTINCT v.model 
        FROM Vehicles v 
        JOIN Orders o ON v.order_id = o.order_id 
        WHERE {date_condition} AND v.model IS NOT NULL {order_cond}
        ORDER BY v.model ASC
    """
    model_rows = execute_read_query(conn, models_sql, base_params)
    available_models = [r['model'] for r in model_rows] if model_rows else []

    sqlStatement = f"""
        SELECT v.modelYear, v.model, v.body, v.trim, e.engine_type, e.engine_rpo,
               t.transmission_type, d.drivetrain_type, c.color_name, c.rpo_code,
               (SELECT GROUP_CONCAT(se.special_desc SEPARATOR ', ')
                FROM SpecialEditions se
                WHERE se.vehicle_id = v.vehicle_id) AS special_desc
        FROM Vehicles v
        JOIN Orders o ON v.order_id = o.order_id
        LEFT JOIN Engines e ON v.engine_id = e.engine_id
        LEFT JOIN Transmissions t ON v.transmission_id = t.transmission_id
        LEFT JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
        LEFT JOIN Colors c ON v.color_id = c.color_id
        WHERE {date_condition}
    """
    
    params = list(base_params)

    if model_filter:
        if model_filter == 'CORVETTE (C8)':
            sqlStatement += " AND v.model LIKE %s AND v.modelYear >= '2020'"
            params.append('CORVETTE%')
        else:
            sqlStatement += " AND v.model = %s"
            params.append(model_filter)

    if trim_filter:
        sqlStatement += " AND v.trim = %s"
        params.append(trim_filter)

    sqlStatement += order_cond

    
    if params:
        rows = execute_read_query(conn, sqlStatement, params)
    else:
        rows = execute_read_query(conn, sqlStatement)
        
    close_connection(conn)

    stats = {
        'total': len(rows) if rows else 0,
        'current_date': curr_date_str,
        'min_date': min_date,
        'max_date': max_date,
        'available_models': available_models,
        'available_model_years': available_model_years, # NEW: Send to frontend
        'modelYear': {}, 'model': {}, 'body': {}, 'trim': {},
        'engine': {}, 'trans': {}, 'drivetrain': {}, 'color': {}, 'specialedition': {}
    }

    if rows:
        for r in rows:
            my = str(r['modelYear']) if r['modelYear'] else 'Unknown'
            mod = r['model'] or 'Unknown'
            bdy = r['body'] or 'Unknown'
            trm = r['trim'] or 'Unknown'
            
            eng_type = r['engine_type'] or 'Unknown'
            eng_rpo = r['engine_rpo']
            eng = f"{eng_rpo} - {eng_type}" if eng_rpo and eng_rpo != 'N/A' else eng_type
            
            clr_name = r['color_name'] or 'Unknown'
            clr_rpo = r['rpo_code']
            clr = f"{clr_rpo} - {clr_name}" if clr_rpo and clr_rpo != 'N/A' else clr_name

            trn = r['transmission_type'] or 'Unknown'
            drv = r['drivetrain_type'] or 'Unknown'

            stats['modelYear'][my] = stats['modelYear'].get(my, 0) + 1
            stats['model'][mod] = stats['model'].get(mod, 0) + 1
            stats['body'][bdy] = stats['body'].get(bdy, 0) + 1
            stats['trim'][trm] = stats['trim'].get(trm, 0) + 1
            stats['engine'][eng] = stats['engine'].get(eng, 0) + 1
            stats['trans'][trn] = stats['trans'].get(trn, 0) + 1
            stats['drivetrain'][drv] = stats['drivetrain'].get(drv, 0) + 1
            stats['color'][clr] = stats['color'].get(clr, 0) + 1
            
            if r['special_desc']:
                for sp in r['special_desc'].split(', '):
                    stats['specialedition'][sp] = stats['specialedition'].get(sp, 0) + 1

    for key in stats:
        if key not in ['total', 'current_date', 'min_date', 'max_date', 'available_models', 'available_model_years']:
            stats[key] = dict(sorted(stats[key].items(), key=lambda item: item[1], reverse=True))

    return jsonify(stats)

@app.route('/stats', methods=['GET'])
def stats():
    category = request.args.get('category', '').strip() or None
    year = request.args.get('year', '').strip() or None
    model = request.args.get('model', '').strip() or None
    body = request.args.get('body', '').strip() or None
    trim = request.args.get('trim', '').strip() or None
    engine = request.args.get('engine', '').strip() or None
    trans = request.args.get('trans', '').strip() or None
    drivetrain = request.args.get('drivetrain', '').strip() or None
    conditions = []
    year_cond = None
    params = []

    if model == "CORVETTE (C8)" and year and int(year) < 2020:
        year = None
        target_year = "2026"
    else:
        target_year = year if year else "2026"

    if year:
        year_cond = "v.modelYear = %s"
        conditions.append(year_cond)
        params.append(year)

    if model:
        if model == "CORVETTE (C8)":
            conditions.append("v.model LIKE 'CORVETTE%%'")
            conditions.append("v.modelYear >= '2020'")
        else:
            conditions.append("v.model = %s")
            params.append(model)

    if body: conditions.append("v.body = %s"); params.append(body)
    if trim: conditions.append("v.trim = %s"); params.append(trim)
    if engine: conditions.append("e.engine_type = %s"); params.append(engine)
    if trans: conditions.append("t.transmission_type = %s"); params.append(trans)
    if drivetrain: conditions.append("d.drivetrain_type = %s"); params.append(drivetrain)
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    filter_only_joins = []
    if engine:
        filter_only_joins.append("JOIN Engines e ON v.engine_id = e.engine_id")
    if trans:
        filter_only_joins.append("JOIN Transmissions t ON v.transmission_id = t.transmission_id")
    if drivetrain:
        filter_only_joins.append("JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id")
    filter_only_join_clause = "\n        ".join(filter_only_joins)

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

    if category == 'color':
        sqlStatement = f"""
            WITH VehColorCounts AS (
                SELECT v.color_id, (v.modelYear >= 2026) AS is_2026_plus, COUNT(*) AS cnt
                FROM Vehicles v
                {filter_only_join_clause}
                {where_clause}
                GROUP BY v.color_id, is_2026_plus
            ),
            ColorCounts AS (
                SELECT
                    CASE
                        WHEN c.color_name = 'BLADE SILVER METALLIC' AND vc.is_2026_plus THEN 'GKA'
                        WHEN c.rpo_code = 'N/A' THEN c.color_name
                        ELSE c.rpo_code
                    END AS rpo_code,
                    CAST(SUM(vc.cnt) AS UNSIGNED) AS total_count,
                    GROUP_CONCAT(DISTINCT c.color_name ORDER BY c.color_name SEPARATOR ', ') AS color_names
                FROM VehColorCounts vc
                JOIN Colors c ON vc.color_id = c.color_id
                GROUP BY 1
            ),
            Ranked AS (
                SELECT
                    DENSE_RANK() OVER (ORDER BY total_count DESC) AS `rank`,
                    rpo_code AS label,
                    rpo_code,
                    total_count,
                    color_names,
                    ROUND(100.0 * total_count / SUM(total_count) OVER (), 5) AS percent
                FROM ColorCounts
            )
            SELECT * FROM Ranked;
        """
    elif category == 'interior':
        interior_rpos_param = request.args.get('interiorRPOs', '')
        interior_rpos = [
            x.strip().upper()
            for x in interior_rpos_param.split(',')
            if re.fullmatch(r'[A-Z0-9]{1,10}', x.strip().upper())
        ] if interior_rpos_param else []
        if not interior_rpos:
            interior_rpos = ['__NONE__']
        placeholders = ", ".join(["%s"] * len(interior_rpos))
        interior_params = params + interior_rpos
        
        # If where_clause is empty, we must start it with WHERE instead of AND
        rpo_where = f" AND opt.option_code IN ({placeholders})"
        if not where_clause:
            rpo_where = f"WHERE opt.option_code IN ({placeholders})"

        sqlStatement = f"""
            WITH InteriorCounts AS (
                SELECT
                    opt.option_code AS rpo_code,
                    COUNT(*) AS total_count
                FROM Vehicles v
                JOIN Options opt ON v.vehicle_id = opt.vehicle_id
                {filter_only_join_clause}
                {where_clause}
                {rpo_where}
                GROUP BY opt.option_code
            ),
            Ranked AS (
                SELECT
                    DENSE_RANK() OVER (ORDER BY total_count DESC) AS `rank`,
                    rpo_code AS label,
                    rpo_code,
                    total_count,
                    '' AS color_names,
                    ROUND(100.0 * total_count / SUM(total_count) OVER (), 5) AS percent
                FROM InteriorCounts
            )
            SELECT * FROM Ranked;
        """
    elif category == 'engine':
        sqlStatement = f"""
            WITH VehEngineCounts AS (
                SELECT v.engine_id, COUNT(*) AS cnt
                FROM Vehicles v
                {filter_only_join_clause}
                {where_clause}
                GROUP BY v.engine_id
            ),
            EngineCounts AS (
                SELECT
                    e.engine_rpo,
                    e.engine_type,
                    CAST(SUM(vc.cnt) AS UNSIGNED) AS total_count
                FROM VehEngineCounts vc
                JOIN Engines e ON vc.engine_id = e.engine_id
                GROUP BY e.engine_rpo, e.engine_type
            ),
            Ranked AS (
                SELECT
                    DENSE_RANK() OVER (ORDER BY total_count DESC) AS `rank`,
                    CONCAT(IFNULL(engine_rpo, ''), IF(engine_rpo IS NOT NULL, ' - ', ''), engine_type) AS label,
                    IFNULL(engine_rpo, '') AS engine_rpo,
                    engine_type,
                    total_count,
                    ROUND(100.0 * total_count / SUM(total_count) OVER (), 5) AS percent
                FROM EngineCounts
            )
            SELECT * FROM Ranked;
        """
    elif category == 'production':
        prod_conditions = conditions.copy()
        prod_params = params.copy()
        if not any("v.modelYear" in c for c in prod_conditions):
            prod_conditions.append("v.modelYear = %s")
            prod_params.append(target_year)

        full_where = f"WHERE {' AND '.join(prod_conditions)}"
        sqlStatement = f"""
            SELECT DATE_FORMAT(o.creation_date, '%%Y-%%m-%%d') AS label, COUNT(*) AS total_count
            FROM Vehicles v
            JOIN Orders o ON v.order_id = o.order_id
            {filter_only_join_clause}
            {full_where}
            GROUP BY label ORDER BY label ASC;
        """
    elif category == 'dealers':
        sqlStatement = f"""
            SELECT 
                dl.dealer_id,
                dl.dealer_name,
                dl.location,
                dl.sitedealer_code,
                vc.total_count
            FROM (
                SELECT v.dealer_id, COUNT(*) AS total_count
                FROM Vehicles v
                {filter_only_join_clause}
                {where_clause}
                GROUP BY v.dealer_id
            ) AS vc
            JOIN Dealers dl ON vc.dealer_id = dl.dealer_id
            ORDER BY vc.total_count DESC;
        """
    else:
        close_connection(conn)
        return jsonify([])


    states_list = []
    dealer_summary = {}

    if category == 'production':
        viewTable = execute_read_query(conn, sqlStatement, prod_params)
    elif category == 'interior':
        viewTable = execute_read_query(conn, sqlStatement, interior_params)
    elif category == 'dealers':
        raw_dealers = execute_read_query(conn, sqlStatement, params) or []
        states_map = {}
        total_vehicles = 0
        unique_dealers = set()
        unique_cities = set()

        for row in raw_dealers:
            count = row.get('total_count') or 0
            total_vehicles += count
            raw_dealer_id = str(row.get('dealer_id') or '')
            raw_name = (row.get('dealer_name') or 'Unknown Dealer').strip()
            raw_loc = (row.get('location') or '').strip()
            raw_code = str(row.get('sitedealer_code') or '').strip()

            state_code, city_name, zip_code = parse_dealer_location(raw_loc)
            unique_cities.add(f"{state_code}:{city_name}")

            norm_name = normalize_dealer_name(raw_name)
            loc_key = normalize_location_key(state_code, city_name, zip_code, raw_loc)
            dealer_key = (norm_name, loc_key)
            unique_dealers.add(dealer_key)

            if state_code not in states_map:
                states_map[state_code] = {
                    'state': state_code,
                    'state_name': STATE_NAMES.get(state_code, state_code),
                    'total_count': 0,
                    'dealers_set': set(),
                    'cities_map': {}
                }

            state_obj = states_map[state_code]
            state_obj['total_count'] += count
            state_obj['dealers_set'].add(dealer_key)

            if city_name not in state_obj['cities_map']:
                state_obj['cities_map'][city_name] = {
                    'city': city_name,
                    'state': state_code,
                    'total_count': 0,
                    'dealers_map': {}
                }

            city_obj = state_obj['cities_map'][city_name]
            city_obj['total_count'] += count

            clean_display_name = raw_name.rstrip('.').rstrip(',').strip()

            if dealer_key not in city_obj['dealers_map']:
                city_obj['dealers_map'][dealer_key] = {
                    'dealer_ids': [x.strip() for x in raw_dealer_id.split(',') if x.strip()],
                    'dealer_name': clean_display_name,
                    'location': raw_loc,
                    'zip': zip_code,
                    'sitedealer_codes': [x.strip() for x in raw_code.split(',') if x.strip()],
                    'total_count': count,
                    'max_count': count
                }
            else:
                existing = city_obj['dealers_map'][dealer_key]
                existing['total_count'] += count
                for x in raw_dealer_id.split(','):
                    x = x.strip()
                    if x and x not in existing['dealer_ids']:
                        existing['dealer_ids'].append(x)
                for x in raw_code.split(','):
                    x = x.strip()
                    if x and x not in existing['sitedealer_codes']:
                        existing['sitedealer_codes'].append(x)
                if len(zip_code) > len(existing['zip']):
                    existing['zip'] = zip_code
                if len(raw_loc) > len(existing['location']):
                    existing['location'] = raw_loc
                if count > existing['max_count']:
                    existing['dealer_name'] = clean_display_name
                    existing['max_count'] = count

        for state_code, s_info in states_map.items():
            cities_list = []
            for city_name, c_info in s_info['cities_map'].items():
                dealers_list = []
                for d_key, d_obj in c_info['dealers_map'].items():
                    dealers_list.append({
                        'dealer_id': ','.join(d_obj['dealer_ids']),
                        'dealer_name': d_obj['dealer_name'],
                        'location': d_obj['location'],
                        'zip': d_obj['zip'],
                        'sitedealer_code': ', '.join(d_obj['sitedealer_codes']),
                        'total_count': d_obj['total_count']
                    })
                dealers_list.sort(key=lambda d: d['total_count'], reverse=True)
                cities_list.append({
                    'city': city_name,
                    'state': state_code,
                    'total_count': c_info['total_count'],
                    'dealer_count': len(dealers_list),
                    'dealers': dealers_list
                })
            cities_list.sort(key=lambda c: c['total_count'], reverse=True)
            states_list.append({
                'state': state_code,
                'state_name': s_info['state_name'],
                'total_count': s_info['total_count'],
                'dealer_count': len(s_info['dealers_set']),
                'city_count': len(cities_list),
                'cities': cities_list
            })

        states_list.sort(key=lambda s: s['total_count'], reverse=True)

        for s in states_list:
            s['percent'] = format_percent(s['total_count'], total_vehicles)
            for c in s['cities']:
                c['percent_of_state'] = format_percent(c['total_count'], s['total_count'])
                c['percent_of_total'] = format_percent(c['total_count'], total_vehicles)
                for d in c['dealers']:
                    d['percent_of_city'] = format_percent(d['total_count'], c['total_count'])
                    d['percent_of_total'] = format_percent(d['total_count'], total_vehicles)

        dealer_summary = {
            'total_vehicles': total_vehicles,
            'total_states': len(states_list),
            'total_cities': len(unique_cities),
            'total_dealers': len(unique_dealers)
        }

        viewTable = [
            {
                'label': f"{s['state_name']} ({s['state']})",
                'rpo_code': s['state'],
                'state': s['state'],
                'total_count': s['total_count'],
                'percent': s['percent']
            }
            for s in states_list[:15]
        ]
    elif category:
        viewTable = execute_read_query(conn, sqlStatement, params)
    else:
        viewTable = []

    year_agnostic_conds = [c for c in conditions if c != year_cond]
    
    year_agnostic_params = []
    if model and model != "CORVETTE (C8)": year_agnostic_params.append(model)
    if body: year_agnostic_params.append(body)
    if trim: year_agnostic_params.append(trim)
    if engine: year_agnostic_params.append(engine)
    if trans: year_agnostic_params.append(trans)
    if drivetrain: year_agnostic_params.append(drivetrain)

    year_where = f"WHERE {' AND '.join(year_agnostic_conds)}" if year_agnostic_conds else ""

    year_sql = f"SELECT DISTINCT v.modelYear FROM Vehicles v {filter_only_join_clause} {year_where} ORDER BY v.modelYear DESC"
    all_years_raw = execute_read_query(conn, year_sql, year_agnostic_params) or []
    all_years = [r['modelYear'] for r in all_years_raw if r.get('modelYear')]

    distinct_sql = f"""
        SELECT DISTINCT vc.model, vc.body, vc.trim, e.engine_type, t.transmission_type, d.drivetrain_type
        FROM (
            SELECT DISTINCT v.model, v.body, v.trim, v.engine_id, v.transmission_id, v.drivetrain_id
            FROM Vehicles v
            {filter_only_join_clause}
            {where_clause}
        ) AS vc
        JOIN Engines e ON vc.engine_id = e.engine_id
        JOIN Transmissions t ON vc.transmission_id = t.transmission_id
        JOIN Drivetrains d ON vc.drivetrain_id = d.drivetrain_id
    """
    distinct_results = execute_read_query(conn, distinct_sql, params) or []

    close_connection(conn)

    if model == "CORVETTE (C8)":
        all_years = [y for y in all_years if y and int(y) >= 2020]

    response_payload = {
        'stats_data': viewTable,
        'year': all_years,
        'selectedYear': target_year,
        'model': sorted(set(r['model'] for r in distinct_results if r.get('model'))),
        'body': sorted(set(r['body'] for r in distinct_results if r.get('body'))),
        'trim': sorted(set(r['trim'] for r in distinct_results if r.get('trim'))),
        'engine': sorted(set(r['engine_type'] for r in distinct_results if r.get('engine_type'))),
        'trans': sorted(set(r['transmission_type'] for r in distinct_results if r.get('transmission_type'))),
        'drivetrain': sorted(set(r['drivetrain_type'] for r in distinct_results if r.get('drivetrain_type'))),
        'category': category
    }
    if category == 'dealers':
        response_payload['dealers_data'] = states_list
        response_payload['dealer_summary'] = dealer_summary

    return jsonify(response_payload)

@app.route('/wheels', methods=['GET'])
def wheel_stats():
    model = request.args.get('model', '').strip() or None

    conditions = []
    params = []
    if model:
        if model == "CORVETTE (ALL)":
            corvette_models = ["CORVETTE STINGRAY", "CORVETTE STINGRAY W/ Z51", "CORVETTE GRAND SPORT", "CORVETTE GRAND SPORT X", "CORVETTE E-RAY", "CORVETTE Z06", "CORVETTE ZR1", "CORVETTE ZR1X"]
            corvette_list = ", ".join(['%s'] * len(corvette_models))
            conditions.append(f"model IN ({corvette_list})")
            params.extend(corvette_models)
        else:
            conditions.append("model = %s")
            params.append(model)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    distinct_sql = f"""
        SELECT DISTINCT model
        FROM Vehicles
        {where_clause}
    """

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    distinct_results = execute_read_query(conn, distinct_sql, params)
    model_list = sorted(set(r['model'] for r in distinct_results if r['model']))

    close_connection(conn)

    return jsonify({
        'model': model_list,
    })

@app.route('/about', methods=['GET'])
def about_stats():
    distinct_sql = """
        WITH LatestModelYears AS (
            SELECT v.model, MAX(v.modelYear) AS max_yr
            FROM Vehicles v
            WHERE v.model IS NOT NULL
            GROUP BY v.model
        )
        SELECT
            CASE
                WHEN v.model LIKE 'CORVETTE%' THEN 'CORVETTE'
                WHEN v.model LIKE 'HUMMER EV%' THEN 'HUMMER EV'
                ELSE v.model
            END AS model_group,
            DATE_FORMAT(MAX(o.creation_date), '%M %e, %Y') AS latest_date
        FROM LatestModelYears lmy
        JOIN Vehicles v ON v.model = lmy.model AND v.modelYear >= lmy.max_yr - 1
        JOIN Orders o ON v.order_id = o.order_id
        GROUP BY model_group
    """

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    results = execute_read_query(conn, distinct_sql)
    close_connection(conn)

    stats_map = {r['model_group'].replace(' ', '_'): r['latest_date'] for r in results}
    return jsonify(stats_map)


#========================= View Pages #=========================

def _warm_startup_cache():
    try:
        with app.test_request_context('/vehicles'):
            sort_price()
        with app.test_request_context('/about'):
            about_stats()
    except Exception as e:
        print(f"Startup cache warm-up skipped: {e}")

_warm_startup_cache()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
