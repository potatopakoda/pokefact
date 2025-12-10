#!/usr/bin/env python3
import argparse, requests, subprocess, random, sys, os
from rich.console import Console, Group
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

base = "https://pokeapi.co/api/v2/"
con = Console()

trivia = {
    "pikachu": "Ash's partner. Hates balls. Beat Tapu Koko.",
    "charizard": "Disobedient. Leon's Ace.",
    "lucario": "Aura master. Beat Cynthia.",
    "greninja": "Ash-Greninja form. Protean beast.",
    "mewtwo": "Destroyed Cinnabar Lab.",
    "rayquaza": "Mega via Dragon Ascent. No stone.",
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
        r = requests.get(u)
        return r.json() if r.status_code == 200 else None
    except: return None

def sound(u):
    if not u: return
    cmd = ["mpv", u, "--no-terminal", "--volume=60"]
    try: subprocess.run(cmd, stderr=subprocess.DEVNULL, shell=(os.name=='nt'))
    except: pass

def read_art(n, s=False, f=None):
    try:
        # Strategy 1: Look relative to script (Dev mode)
        here = os.path.dirname(os.path.realpath(__file__))
        
        # Strategy 2: Look in User Home (Installed mode)
        # This handles the specific Windows install path we used
        home = os.path.expanduser("~")
        install_path = os.path.join(home, ".pokefact", "pokemon-colorscripts", "colorscripts")
        
        # Check dev path first, then install path
        dev_path = os.path.join(here, "../pokemon-colorscripts/colorscripts")
        
        if os.path.exists(dev_path):
            root = dev_path
        elif os.path.exists(install_path):
            root = install_path
        else:
            return None # Can't find art folder

        mode = "shiny" if s else "regular"
        tgt = f"{n}-{f}" if f else n
        path = os.path.join(root, mode, tgt)
        
        if not os.path.exists(path) and f:
            path = os.path.join(root, mode, f"{f}-{n}")
            
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as x: return x.read()
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

def make_gal(name, sd):
    a1 = read_art(name) or f"\n\n[dim]No Art[/]\n\n"
    a2 = read_art(name, True) or f"\n\n[dim]No Shiny[/]\n\n"
    
    top = Columns([
        Panel(Text.from_ansi(a1), title="Normal", box=box.MINIMAL),
        Panel(Text.from_ansi(a2), title="Shiny", box=box.MINIMAL)
    ], equal=True)
    
    megas = []
    for v in sd.get('varieties', []):
        vn = v['pokemon']['name']
        if 'mega' in vn:
            cln = vn.replace(name+"-", "").replace("-", " ").title()
            form = vn.replace(f"{name}-", "")
            art = read_art(name, form=form)
            if art: megas.append(Panel(Text.from_ansi(art), title=cln, box=box.MINIMAL))
            
    grp = [top]
    if megas:
        grp.append(Text("\nMEGA FORMS", style="bold magenta", justify="center"))
        grp.append(Columns(megas, equal=True))
    return Panel(Group(*grp), box=box.MINIMAL)

def make_stats(d, sd):
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
    
    if d['name'] in trivia: g.add_row("TRIVIA:", f"[gold1]{trivia[d['name']]}[/]")
    
    g.add_row("", "")
    g.add_row("[underline]Stats[/]", "")
    for s in d['stats']:
        val = s['base_stat']
        fill = int((val/255)*20)
        bar = "█"*fill + "░"*(20-fill)
        sn = s['stat']['name'].replace("special-","Sp.").replace("attack","Atk").replace("defense","Def").title()
        g.add_row(sn, f"[bold {c}]{val}[/bold {c}] {bar}")
        
    return Panel(g, title=f"[bold {c}] {nm} [/]", border_style=c)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", type=str)
    p.add_argument("-s", action="store_true")
    p.add_argument("-a", action="store_true")
    args = p.parse_args()
    
    t = args.p.lower() if args.p else str(random.randint(1, 1025))
    
    with con.status(f"[green]Scanning {t}..."):
        d = grab(f"{base}pokemon/{t}")
        if not d: sys.exit(print(f"Err: {t} not found"))
        sd = grab(f"{base}pokemon-species/{d['id']}")
        
    if args.a: sound(d.get('cries', {}).get('latest'))
    
    con.print(Columns([make_gal(d['name'], sd), make_stats(d, sd)]))

if __name__ == "__main__":
    try: main()
    except: pass
