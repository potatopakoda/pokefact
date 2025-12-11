#!/usr/bin/env python3
import argparse, requests, subprocess, random, sys, os, urllib3
from rich.console import Console, Group
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# Try import PIL for sprite generation
try:
    from PIL import Image
    from io import BytesIO
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ssl fix
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base = "https://pokeapi.co/api/v2/"
con = Console()

# --- FALLBACK ART ---
SUB = r"""
    _._
   (o o)
   /   \
  (_/ \_)
"""

# --- MASSIVE TRIVIA DATABASE ---
trivia = {
    "pikachu": [
        "Is the official mascot of the entire Pokémon franchise.",
        "It was one of the earliest designs created, preceding most others.",
        "In the games, it is known as the 'Mouse Pokémon' and stores electricity in its cheeks.",
        "Ash's Pikachu is disobedient at first, but warms up after Ash saves it from a flock of Spearow.",
        "It refuses to stay in its Poké Ball and instead follows the main character around in Pokémon Yellow.",
        "Multiple event distributions have given Pikachu various hats worn by Ash across the seasons.",
        "Has been a playable fighter in all five Super Smash Bros. crossover fighting games.",
        "The word 'Pikachu' comes from the Japanese 'pika' (a small animal) and 'chu' (the sound a mouse makes).",
    ],
    "charizard": [
        "In Japan, Charizard is known as 'Lizardon'.",
        "It is the main Pokémon featured on the game covers for Pokémon Red and FireRed.",
        "Its flame can turn a bright whitish-blue color if it gets extremely angry.",
        "It has two special Mega Evolutions: Mega Charizard X (gaining Dragon typing) and Mega Charizard Y.",
        "The first-ever Charizard Trading Card (1999) became a highly sought-after collector's item.",
        "Ash's Charizard was notoriously disobedient until saving Ash in a blizzard.",
        "The front of its wings is blue, and the back is orange.",
        "It was a playable character in Super Smash Bros. Brawl as part of the Pokémon Trainer's team.",
    ],
    "lucario": [
        "It is known as the 'Aura Pokémon' and is a Fighting/Steel type.",
        "A well-trained Lucario can sense auras and identify feelings of creatures over half a mile away.",
        "In the anime movie, the original Lucario was a servant to Sir Aaron and could speak human languages without psychic powers.",
        "It is based on the mythical creature Anubis, the jackal-headed god of ancient Egypt.",
        "In the Pokémon Mystery Dungeon games, achieving 15,000 Rescue Points earns the player the top rank, the 'Lucario Rank'.",
        "It has a Mega Evolution introduced in Generation 6 games.",
        "Its fighting style in Mega form can be summed up in a single word: heartless.",
    ],
    "garchomp": [
        "It is known as the 'Mach Pokémon'.",
        "It combines the design of a dinosaur, a European dragon, and a hammerhead shark.",
        "It is famous for being the signature Pokémon of Champion Cynthia, contributing to her difficulty as an opponent.",
        "It is often considered one of the top competitive Pokémon due to its high speed and attack power.",
        "Garchomp was one of the few non-legendary Pokémon to be banned in some competitions due to its strength.",
        "Its ability, Rough Skin, hurts foes that hit it with physical moves.",
        "It evolves from Gabite at level 48.",
    ],
    "rayquaza": [
        "It is the trio master of the Weather Trio (with Kyogre and Groudon) and serves as their leader.",
        "It resides high up in the ozone layer and flies endlessly, rarely descending to the ground.",
        "It serves as the mascot legendary for Pokémon Emerald.",
        "It achieves Mega Evolution using the move Dragon Ascent, requiring no Mega Stone.",
        "Lore states it has lived for hundreds of millions of years in the ozone layer.",
        "It feeds on water and particles in the atmosphere and meteoroids for substance.",
        "In the Delta Episode of Omega Ruby/Alpha Sapphire, it destroyed a meteoroid by flying straight through it in its Mega form.",
    ],
    "mewtwo": [
        "It is known as the 'Genetic Pokémon' and was created by genetically modifying Mew's DNA.",
        "It was the strongest Pokémon in the original games in terms of base statistic distribution.",
        "It was one of the earliest Pokémon designs created, preceding even Pikachu.",
        "Mewtwo can use telekinesis for flight, shielding, and throwing opponents.",
        "It is among the very few Pokémon capable of human speech, doing so via telepathy.",
        "It has two Mega Evolved forms, Mega Mewtwo X and Mega Mewtwo Y.",
        "Mewtwo received the signature move 'Psystrike' in Pokémon Black and White.",
        "In the anime, Mewtwo's fury was enraged by the fact that it wasn't created by God (Japanese version lore).",
    ],
    "infernape": [
        "It is the fastest final evolution of the Sinnoh starter Pokémon.",
        "It is based on the ape and has plates of gold covering its shoulders, wrists, knees, and chest.",
        "It uses all its limbs to fight in its own unique style, tossing enemies around with agility.",
        "It has the ability Blaze, which powers up its Fire-type moves when its HP is low.",
        "Ash's Infernape gained control of its powerful Blaze ability to defeat Paul's Electivire.",
    ],
    "sceptile": [
        "It is known as the 'Forest Pokémon'.",
        "Its leaves, which grow on its forelegs, are described as being as sharp as swords.",
        "It is without peer in jungle combat and can slice down thick trees.",
        "Ash's Sceptile famously defeated Tobias' Darkrai during the Sinnoh League semi-finals.",
        "It regulates its body temperature by basking in sunlight.",
        "It has Mega Evolution available using Sceptilite.",
    ],
    "greninja": [
        "Ash-Greninja form was released to games as an empowered form accessible via the Pokémon Sun and Moon Special Demo.",
        "It is introduced as a playable fighter in the Super Smash Bros. series.",
        "It moves with 'a ninja's grace' and is associated with Ninjutsu.",
        "Its unique move, Mat Block, shields the user's side with a flipped-up mat.",
        "Its Protean ability allows it to camouflage to the type of the attack it uses.",
        "Its design was created by Yusuke Ohmura, who also designed the mascots Xerneas and Yveltal.",
        "Ash's Greninja gained considerable power, endurance, and speed in its Ash-Greninja form.",
    ],
    "wobbuffet": [
        "It is usually docile but will counterattack when attacked, inflating its body to initiate the strike.",
        "When multiple Wobbuffet meet, they will try to outlast each other in a battle of endurance.",
        "Jessie's Wobbuffet frequently emerges from its Poké Ball on its own accord, a trait that initially annoyed Jessie.",
        "The female Wobbuffet has a red marking on its mouth that resembles lipstick.",
        "Wobbuffet is very protective of its black tail, to the point where it becomes aggressive if the tail is touched.",
        "It was left at Team Rocket HQ before the trio departed for Unova, but later reunited with Jessie in the Kalos region.",
    ],
    "mimikyu": [
        "Anime: Jessie's Mimikyu has a deep, murderous grudge against Pikachu.",
        "Lore: A scholar who saw under its rag died from shock.",
        "Game: Its 'Disguise' ability lets it take one free hit without damage."
    ],
    "tinkaton": [
        "Lore: It hunts Corviknight to steal their metal for its hammer.",
        "Game: Has a signature move 'Gigaton Hammer' with 160 base power.",
        "Fan Fact: A menace to the Galar taxi service."
    ],
    "arceus": [
        "Lore: It shaped the universe with its 1,000 arms.",
        "Game: Can change its type to anything depending on the Plate it holds.",
        "Anime: Almost destroyed humanity in 'Jewel of Life' due to betrayal."
    ],
    "mew": [
        "Fan Myth: Rumored to be hiding under the truck near the S.S. Anne in Red/Blue.",
        "Game: Contains the DNA of every Pokémon, allowing it to learn every TM/HM.",
        "Anime: Playfully fought Mewtwo in the first movie to prove natural strength vs clones."
    ],
    "magikarp": [
        "Lore: It is said to be able to leap over a mountain using Splash, but it does no damage.",
        "Anime: James bought one from a scam artist, only for it to evolve into Gyarados and attack him.",
        "Game: Requires 400 candies to evolve in Pokémon GO, the highest amount."
    ],
    "gyarados": [
        "Shiny: The Red Gyarados in Lake of Rage is the first shiny many players ever encountered.",
        "Anime: Misty, a water trainer, had a phobia of Gyarados until she bonded with one.",
        "Mega: Becomes Water/Dark type and gains Mold Breaker."
    ],
    "eevee": [
        "Manga: Red's Eevee could mutate into Vaporeon, Jolteon, or Flareon and turn back freely.",
        "Game: The partner Eevee in 'Let's Go' cannot evolve and has perfect stats.",
        "Lore: Its unstable DNA allows it to adapt to any environment."
    ],
    "snorlax": [
        "Anime: Ash's Snorlax had to be fed a year's supply of grapefruit to be caught.",
        "Game: Often blocks key paths (Route 12) and requires a Poké Flute to wake up.",
        "Manga: Red's Snorlax (Snor) served as a makeshift trampoline/shield."
    ],
    "lugia": [
        "Anime: Known as the 'Beast of the Sea' in Pokémon The Movie 2000.",
        "Game: Despite being the guardian of the seas, it is Psychic/Flying, not Water type.",
        "Lore: Its wings pack enough power to blow apart regular houses."
    ],
    "ho-oh": [
        "Anime: Appeared to Ash in the very first episode, years before Gold/Silver released.",
        "Lore: Revived the three legendary beasts (Raikou, Entei, Suicune) from the ashes of the Burned Tower.",
        "Item: Leaves behind a Rainbow Wing to pure-hearted trainers."
    ]
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

def gen_ascii(url):
    if not HAS_PIL or not url: return None
    try:
        r = requests.get(url, verify=False, timeout=5)
        im = Image.open(BytesIO(r.content)).convert("RGBA")
        width = 22
        w_percent = (width / float(im.size[0]))
        h_size = int((float(im.size[1]) * float(w_percent)) * 0.55)
        im = im.resize((width, h_size), Image.Resampling.NEAREST)
        ascii_str = ""
        pixels = im.load()
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                r, g, b, a = pixels[x, y]
                txt = " " if a < 50 else f"\033[38;2;{r};{g};{b}m█\033[0m"
                ascii_str += txt
            ascii_str += "\n"
        return ascii_str
    except: return None

def read_art(n, s=False, f=None, sprite_url=None):
    try:
        here = os.path.dirname(os.path.realpath(__file__))
        home = os.path.expanduser("~")
        paths = [
            os.path.join(home, ".local", "share", "pokefact", "pokemon-colorscripts", "colorscripts"),
            os.path.join(home, ".pokefact", "pokemon-colorscripts", "colorscripts"),
            os.path.join(here, "../pokemon-colorscripts/colorscripts")
        ]
        root = next((p for p in paths if os.path.exists(p)), None)
        
        if root:
            folders = ["small", "regular", "large", "."]
            mode = "shiny" if s else "regular"
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

    if sprite_url: return gen_ascii(sprite_url)
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
    spr = d['sprites']
    front = spr.get('other', {}).get('official-artwork', {}).get('front_default') or spr['front_default']
    shiny = spr.get('other', {}).get('official-artwork', {}).get('front_shiny') or spr['front_shiny']

    a1 = read_art(nm, False, None, front) or "\n[dim]No Data[/]"
    a2 = read_art(nm, True, None, shiny) or "\n[dim]No Data[/]"
    
    top = Columns([
        Panel(Text.from_ansi(a1), title="Normal", box=box.MINIMAL),
        Panel(Text.from_ansi(a2), title="Shiny", box=box.MINIMAL)
    ], equal=True)
    
    megas = []
    for v in sd.get('varieties', []):
        vn = v['pokemon']['name']
        if vn == nm: continue
        if any(x in vn for x in ['mega', 'gmax', 'alola', 'hisui', 'galar', 'paldea']):
            cln = vn.replace(nm+"-", "").replace("-", " ").title()
            form = vn.replace(f"{nm}-", "")
            
            vd = grab(v['pokemon']['url'])
            if vd:
                vf = vd['sprites'].get('other', {}).get('official-artwork', {}).get('front_default') or vd['sprites']['front_default']
                art = read_art(nm, False, form, vf)
                if art: megas.append(Panel(Text.from_ansi(art), title=cln, box=box.MINIMAL))

    grp = [top]
    if megas:
        grp.append(Text("\nFORMS", style="bold magenta", justify="center"))
        grp.append(Columns(megas, equal=True))
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

    all_facts = []
    for f in sd['flavor_text_entries']:
        if f['language']['name'] == 'en':
            txt = f['flavor_text'].replace("\n", " ").replace("\f", " ")
            if txt not in all_facts: all_facts.append(txt)
    
    if d['name'] in trivia:
        for fact in trivia[d['name']]:
            all_facts.append(f"[bold gold1]★ {fact}[/]")

    selected_facts = random.sample(all_facts, min(len(all_facts), 5)) if all_facts else ["No data"]
    
    lore = Text()
    if 'evolution_chain' in sd and sd['evolution_chain']:
        e_str = get_evo(sd['evolution_chain']['url'])
        lore.append(f"\nEVO: {e_str}\n", style="bold cyan")
    
    lore.append(f"\nINFO & LORE:\n", style=f"bold {c}")
    for i, f in enumerate(selected_facts, 1): lore.append(f"{i}. {f}\n", style="dim white")
    
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
