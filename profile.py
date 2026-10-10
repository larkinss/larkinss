"""
Generates profile.svg - a neofetch-style GitHub profile card.
Edit the CONFIG section below, then run:  python profile.py
In GitHub Actions it also fetches live GitHub stats using GITHUB_TOKEN.
"""
import os, json, datetime, urllib.request
from xml.sax.saxutils import escape

# ============================ CONFIG ============================
USERNAME   = "larkinss"
HEADER     = "izzat@faiz"
CAREER_START = datetime.date(2017, 8, 1)     # used for "Uptime"

INFO = [
    ("OS",                     "Linux, Windows, Unix"),
    ("Uptime",                 "__UPTIME__"),
    ("Host",                   "CIMB Bank Berhad"),
    ("Role",                   "AVP, Data Platform Engineering"),
    ("IDE",                    "VSCode, Databricks Notebooks"),
    None,
    ("Languages.Programming",  "Python, PySpark, SQL, Shell"),
    ("Platforms.Cloud",        "Azure Databricks, ADF, ADLS Gen2, Fabric"),
    ("Platforms.BigData",      "Hadoop, Cloudera, Hive, Spark, Sqoop"),
    ("Data.Architecture",      "Lakehouse, Delta Lake, Medallion"),
    ("Certifications",         "Databricks Certified DE Professional"),
    None,
    "Contact",
    ("Email.Personal",         "aizzatj1@gmail.com"),
    ("LinkedIn",               "izzatfaizj"),
    None,
    "GitHub Stats",
    ("Repos",                  "__REPOS__"),
    ("Stars",                  "__STARS__"),
    ("Followers",              "__FOLLOWERS__"),
    ("Commits (last year)",    "__COMMITS__"),
]

# ASCII art of Izzat's photo, shown on the left
ART = r"""
                           ::::::::::::
                      :::::::::::::::::::
                 -::::::::::::::::::::::::
               :::::::::::::::::::::::::::
             :::::::::::::::::::::::::::::::::::
            :::::::::-::::::::-==+++==-:::::::::
          -:::::=+*##%%***+****########*+::=--::
          ::::+#@@@@@@@@@%%%%%%%%%%%%%%#*=****==
          ::=*%@@@@@@@@@@@@@@@@@@@@@@@@@%%%#####
          ::+#%@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%
           -##%%@@@@@@@@@@@@@@@@@@@@@%%%#######*
           *###**+++++++*+*#%%%%%%%#*==--:::----
        +++==*===-:-::::---=+####*+====-------==
        =---+++*#%#*+--::::=**##**+*=:::-=++****
        +:::+=-:---:::::::-++*%%%*=+-:::::::::::
        #=:+#*=:::::::::-=**+*@@@%***=-:::::::::
        :**#%@@%#**++++*###=*@@@@%#==**++===+++*
        =*#%%@@@@@%%%%%%%#+#@@@@@%#*+*########%%
        %**%%@@@@%@@@@@%###@@@@@@@%#*####%%%%%##
        @**##%@@@@@@@@@@@@@@@@@@@@@@%@%#%%%@@%%%
        @%**##%%@@@@@@@%%*--=***++=--+###%%@@@%%
        @@**###%@@@@@@@%+==-:-=:-::::-=**#%%%%%%
        ===+##%%%@@@@@@@@%@@%%***#####*##%%%%%%%
           =###%%%%@@@@%%%%@@%##%%%###**#%%%#%%#
            +###%%#%######*****#**++**#*******##
            =**##**+=---:::::-==-:::::-=+==++**#
         +#%@#**#*+-::---===---:::::::::::::-+**
      +%@@@@@@@###*++*###*********+++++==++====**
""".strip("\n").splitlines()
# ================================================================

def uptime():
    t = datetime.date.today()
    m = (t.year - CAREER_START.year) * 12 + t.month - CAREER_START.month
    return f"{m // 12} years, {m % 12} months"

def github_stats():
    token = os.environ.get("GITHUB_TOKEN")
    if not token or USERNAME.startswith("YOUR_"):
        return {"__REPOS__": "-", "__STARS__": "-", "__FOLLOWERS__": "-", "__COMMITS__": "-"}
    q = """query($login:String!){ user(login:$login){
      followers{totalCount}
      repositories(ownerAffiliations:OWNER, first:100, privacy:PUBLIC){totalCount nodes{stargazerCount}}
      contributionsCollection{totalCommitContributions} } }"""
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"login": USERNAME}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    try:
        u = json.load(urllib.request.urlopen(req, timeout=30))["data"]["user"]
    except Exception as e:
        print("Could not fetch GitHub stats:", e)
        return {"__REPOS__": "-", "__STARS__": "-", "__FOLLOWERS__": "-", "__COMMITS__": "-"}
    return {"__REPOS__": f"{u['repositories']['totalCount']:,}",
            "__STARS__": f"{sum(r['stargazerCount'] for r in u['repositories']['nodes']):,}",
            "__FOLLOWERS__": f"{u['followers']['totalCount']:,}",
            "__COMMITS__": f"{u['contributionsCollection']['totalCommitContributions']:,}"}

def build():
    subs = {"__UPTIME__": uptime(), **github_stats()}
    W = 60                       # characters in the info column
    CH, LH = 8.4, 20             # char width / line height (px) for 14px monospace
    art_w = max(len(l) for l in ART) * CH + 30
    x_info = 25 + art_w
    lines = []                   # list of list-of-(text, css class)
    lines.append([(HEADER, "hd"), (" " + "-" * (W - len(HEADER) - 1), "dim")])
    for item in INFO:
        if item is None:
            lines.append([])
        elif isinstance(item, str):
            lines.append([(item, "hd"), (" " + "-" * (W - len(item) - 1), "dim")])
        else:
            k, v = item
            v = subs.get(v, v)
            dots = max(1, W - len(k) - len(v) - 3)
            lines.append([(k, "key"), (": ", "dim"), ("." * dots + " ", "dim"), (v, "val")])
    n = max(len(lines), len(ART))
    H = n * LH + 50
    Wpx = x_info + W * CH + 30
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx:.0f}" height="{H}" viewBox="0 0 {Wpx:.0f} {H}">',
           "<style>text{font-family:'Consolas','Courier New',monospace;font-size:14px;white-space:pre}"
           ".art{fill:#c9d1d9}.hd{fill:#c9d1d9;font-weight:bold}.key{fill:#ffa657}.val{fill:#a5d6ff}.dim{fill:#616e7f}</style>",
           f'<rect width="100%" height="100%" rx="12" fill="#161b22"/>']
    top = 35 + max(0, (len(lines) - len(ART)) * LH // 2)
    out.append(f'<text x="25" y="{top}" class="art" xml:space="preserve">')
    for i, l in enumerate(ART):
        out.append(f'<tspan x="25" y="{top + i * LH}">{escape(l)}</tspan>')
    out.append("</text>")
    out.append(f'<text x="{x_info:.0f}" y="35" xml:space="preserve">')
    for i, parts in enumerate(lines):
        if not parts:
            continue
        spans = "".join(f'<tspan class="{c}">{escape(t)}</tspan>' for t, c in parts)
        out.append(f'<tspan x="{x_info:.0f}" y="{35 + i * LH}">{spans}</tspan>')
    out.append("</text></svg>")
    with open("profile.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("profile.svg written")

if __name__ == "__main__":
    build()
