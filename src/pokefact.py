#!/usr/bin/env python3
import argparse, requests, subprocess, random, sys, os, urllib3
from rich.console import Console, Group
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# FIX: SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base = "https://pokeapi.co/api/v2/"
con = Console()

# --- THE SUBSTITUTE DOLL (Fallback) ---
SUB = r"""
    _._
   (o o)
   /   \
  (_/ \_)
"""

trivia = {
    "pikachu": "Ash's partner. Hates balls.",
    "charizard": "Disobedient. Leon's Ace.",
    "lucario": "Aura master. Beat Cynthia.",
    "greninja": "Ash-Greninja form.",
    "mewtwo": "Destroyed Cinnabar Lab.",
    "rayquaza": "Mega via Dragon Ascent.",
    "garchomp": "Cynthia's run killer.",
    "infernape": "Blaze ability go brrr.",
    "sceptile": "Beat Darkrai w/ Leaf Blade.",
    "wobbuffet": "Counter/Mirror Coat god.",
    "mimikyu": "Pikachu hater.",
    "meowth": "Talking cat."
}

cols = {
    "fire": "red", "water": "blue", "grass": "green", "electric": "yellow",
    "psychic": "magenta", "ice": "cyan", "dragon": "violet", "dark": "dim white",
    "ghost": "purple", "fairy": "magenta", "normal": "white", "fighting": "orange1",
    "flying": "cyan", "poison": "purple", "ground": "yellow",
    "rock": "white", "bug": "green", "steel": "white"
}

def grab(u):
    try:
        r = requests.get(u, verify=False, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

def sound(u):
    if not u: return
    cmd = ["mpv", u, "--no-terminal", "--volume=60"]
    try: subprocess.run(cmd, stderr=subprocess.DEVNULL, shell=(os.name=='nt'))
    except: pass

def read_art(n, s=False, f=None):
    try:
        here = os.path.dirname(os.path.realpath(__file__))
        home = os.path.expanduser("~")
        
        # SEARCH PATHS
        paths = [
            os.path.join(home, ".local", "share", "pokefact", "pokemon-colorscripts", "colorscripts"),
            os.path.join(home, ".pokefact", "pokemon-colorscripts", "colorscripts"),
            os.path.join(here, "../pokemon-colorscripts/colorscripts")
        ]
        
        root = next((p for p in paths if os.path.exists(p)), None)
        if not root: return None

        # Check subfolders (prioritize small)
        folders = ["small", "regular", "large", "."]
        mode = "shiny" if s else "regular"
        
        # Name candidates
        cands = []
        if f:
            cands.append(f"{n}-{f}"); cands.append(f"{f}-{n}"); cands.append(f"{n}_{f}")
        cands.append(n)
        if n == "nidoran-m": cands.append("nidoran_m")
        if n == "nidoran-f": cands.append("nidoran_f")

        for sub in folders:
            for name_try in cands:
                p1 = os.path.join(root, sub, mode, name_try)
                if os.path.exists(p1):
                    with open(p1, "r", encoding="utf-8") as x: return x.read()
                p2 = os.path.join(root, sub, name_try)
                if os.path.exists(p2):
                    with open(p2, "r", encoding="utf-8") as x: return x.read()
    except: pass
    return None

def get_weak(types):
    w = {}
    for t in types:
        d = grab(f"{base}type/{t}")
        if not d: continue
        rels = d['damage_relations']
        for x in rels['double_damage_from']: w[x['name']] = w.get(x['name'], 1)*2
        for x in rels['half_damage_from']: w[x['name']] = w.get(x['name'], 1)*0.5
        for x in rels['no_damage_from']: w[x['name']] = 0
    x4 = [k.title() for k,v in w.items() if v >= 4]
    x2 = [k.title() for k,v in w.items() if v == 2]
    return x4, x2

def make_gal(d, sd):
    nm = d['name']
    
    # 1. Base Forms (Use SUB if missing)
    a1 = read_art(nm) or SUB
    a2 = read_art(nm, True) or SUB
    
    top = Columns([
        Panel(Text.from_ansi(a1), title="Normal", box=box.MINIMAL),
        Panel(Text.from_ansi(a2), title="Shiny", box=box.MINIMAL)
    ], equal=True)
    
    # 2. Special Forms (Mega, Gmax, Alola, Hisui)
    specials = []
    
    # Filter keywords for interesting forms
    keywords = ['mega', 'gmax', 'alola', 'hisui', 'galar', 'paldea', 'primal', 'origin']
    
    for v in sd.get('varieties', []):
        vn = v['pokemon']['name']
        if vn == nm: continue
        
        if any(k in vn for k in keywords):
            cln = vn.replace(nm+"-", "").replace("-", " ").title()
            form_arg = vn.replace(f"{nm}-", "")
            
            # Try to find art, fallback to SUB immediately if missing
            art = read_art(nm, f=form_arg) or SUB
            
            # ALWAYS append if it matches keywords
            specials.append(Panel(Text.from_ansi(art), title=cln, box=box.MINIMAL))

    grp = [top]
    if specials:
        grp.append(Text("\nFORMS & VARIATIONS", style="bold magenta", justify="center"))
        grp.append(Columns(specials, equal=True))
        
    return Panel(Group(*grp), box=box.MINIMAL)

def get_evo(url):
    d = grab(url)
    if not d: return "?"
    chain = []
    def walk(n):
        nm = n['species']['name'].title()
        dets = []
        if n['evolution_details']:
            ed = n['evolution_details'][0]
            if ed['min_level']: dets.append(f"Lvl {ed['min_level']}")
            if ed['item']: dets.append(ed['item']['name'].replace('-', ' ').title())
            if ed['trigger']['name'] == 'trade': dets.append("Trade")
        txt = f"{nm} ({', '.join(dets)})" if dets else nm
        chain.append(txt)
        for k in n['evolves_to']: walk(k)
    walk(d['chain'])
    return " -> ".join(chain)

def show(d, sd):
    nm = d['name'].capitalize()
    tps = [x['type']['name'] for x in d['types']]
    c = cols.get(tps[0], "white")
    
    g = Table.grid(padding=(0, 1))
    g.add_column(style=f"bold {c}", justify="right"); g.add_column(style="white")
    g.add_row("ID:", str(d['id']))
    g.add_row("Type:", ", ".join([x.title() for x in tps]))
    
    w4, w2 = get_weak(tps)
    if w4: g.add_row("x4 Weak:", f"[bold red]{', '.join(w4)}[/]")
    if w2: g.add_row("x2 Weak:", f"[red]{', '.join(w2)}[/]")
    
    g.add_row("H/W:", f"{d['height']/10}m / {d['weight']/10}kg")
    
    if sd['is_legendary']: g.add_row("STATUS:", "[bold gold1]LEGENDARY[/]")
    elif sd['is_mythical']: g.add_row("STATUS:", "[bold purple]MYTHICAL[/]")
    
    g.add_row("", "")
    g.add_row("[underline]Stats[/]", "")
    for s in d['stats']:
        val = s['base_stat']
        fill = int((val/255)*20)
        bar = "█"*fill + "░"*(20-fill)
        sn = s['stat']['name'].replace("special-","Sp.").replace("attack","Atk").replace("defense","Def").title()
        g.add_row(sn, f"[bold {c}]{val}[/bold {c}] {bar}")

    flavs = []
    for f in sd['flavor_text_entries']:
        if f['language']['name'] == 'en':
            txt = f['flavor_text'].replace("\n", " ").replace("\f", " ")
            if txt not in flavs: flavs.append(txt)
    facts = random.sample(flavs, min(len(flavs), 3)) if flavs else ["No data"]
    
    lore = Text()
    if d['name'] in trivia: lore.append(f"★ ANIME: {trivia[d['name']]}\n", style="bold gold1")
    if 'evolution_chain' in sd and sd['evolution_chain']:
        e_str = get_evo(sd['evolution_chain']['url'])
        lore.append(f"\nEVO: {e_str}\n", style="bold cyan")
    
    lore.append(f"\nINFO:\n", style=f"bold {c}")
    for i, f in enumerate(facts, 1): lore.append(f"{i}. {f}\n", style="dim white")
    
    l_m, t_m = [], []
    for m in d['moves']:
        mn = m['move']['name'].replace('-', ' ').title()
        det = m['version_group_details'][-1]
        if det['move_learn_method']['name'] == 'level-up':
            l_m.append((det['level_learned_at'], mn))
        else:
            t_m.append(mn)
    l_m.sort(key=lambda x: x[0]); t_m.sort()
    
    mt = Table(box=None, show_header=False, padding=(0, 2))
    mt.add_column(style="dim white"); mt.add_column(style=f"bold {c}")
    mt.add_column(style="dim white"); mt.add_column(style="dim white"); mt.add_column(style=f"bold {c}")
    for i in range(0, len(l_m), 2):
        a = l_m[i]
        b = l_m[i+1] if i+1 < len(l_m) else ("", "")
        mt.add_row(f"L{a[0]}", a[1], "│", f"L{b[0]}", b[1] if b[0] != "" else "")

    return Panel(g, title=f"[bold {c}] {nm} [/]", border_style=c, box=box.ROUNDED), \
           Panel(lore, title=f"[bold {c}]Lore & Trivia[/]", border_style=c, box=box.ROUNDED), \
           Panel(mt, title=f"[bold {c}]Natural Moveset[/]", border_style=c, box=box.ROUNDED), \
           Panel(Text(", ".join(t_m), style="dim white"), title=f"[bold {c}]Technical Machines & Tutors[/]", border_style=c, box=box.ROUNDED)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", type=str)
    p.add_argument("-s", action="store_true")
    p.add_argument("-a", action="store_true")
    args = p.parse_args()
    
    t = args.p.lower() if args.p else str(random.randint(1, 1025))
    
    with con.status(f"[green]Scanning {t}..."):
        d = grab(f"{base}pokemon/{t}")
        if not d: sys.exit(print(f"Err: {t} not found (Check Internet)"))
        
        sd = grab(f"{base}pokemon-species/{d['id']}")
        if not sd: 
            sd = {'varieties': [], 'flavor_text_entries': [], 'is_legendary': False, 'is_mythical': False, 'evolution_chain': None}

    if args.a: sound(d.get('cries', {}).get('latest'))

    art = make_gal(d, sd)
    m, l, c, tm = show(d, sd)
    
    con.print(Columns([art, m]))
    con.print(l)
    con.print(c)
    con.print(tm)

if __name__ == "__main__":
    try: main()
    except Exception as e: print(e)
