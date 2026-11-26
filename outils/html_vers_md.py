#!/usr/bin/env python3
"""Régénère le markdown du cours à partir de la page HTML.

Usage : python3 outils/html_vers_md.py
- lit Deroulement-cours-opencode.html
- écrit « Cours - Développement d'une application par la voie agentique.md »
- exporte chaque schéma SVG de la page dans schemas/*.svg (thème clair)

Le markdown suit le plan de la page. Chaque section existe en deux blocs :
le titre ### suivi de la balise #informaticien ou #généraliste.
"""
import html
import re
from html.parser import HTMLParser
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PAGE = RACINE / "Deroulement-cours-opencode.html"
MD = RACINE / "Cours - Développement d'une application par la voie agentique.md"
SCHEMAS = RACINE / "schemas"

VIDES = {"meta", "link", "img", "br", "hr", "input", "rect", "line", "polygon",
         "path", "circle", "polyline", "source"}


class Noeud:
    def __init__(self, tag, attrs, parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.enfants = []

    def cls(self):
        return self.attrs.get("class", "").split()

    def texte(self):
        return "".join(e if isinstance(e, str) else e.texte() for e in self.enfants)

    def trouver(self, pred):
        for e in self.enfants:
            if isinstance(e, Noeud):
                if pred(e):
                    yield e
                yield from e.trouver(pred)


class Arbre(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.racine = Noeud("racine", [])
        self.cur = self.racine
        self.nb_svg = 0
        self.dans_svg = 0
        self.dans_style = False

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.dans_style = True
            return
        if self.dans_svg:
            if tag == "svg":
                self.dans_svg += 1
            return
        n = Noeud(tag, attrs, self.cur)
        self.cur.enfants.append(n)
        if tag == "svg":
            n.attrs["_index"] = self.nb_svg
            self.nb_svg += 1
            self.dans_svg = 1
            return
        if tag not in VIDES:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        if self.dans_svg or self.dans_style:
            return
        self.cur.enfants.append(Noeud(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.dans_style = False
            return
        if self.dans_svg:
            if tag == "svg":
                self.dans_svg -= 1
            return
        n = self.cur
        while n is not self.racine and n.tag != tag:
            n = n.parent
        if n is not self.racine:
            self.cur = n.parent

    def handle_data(self, data):
        if self.dans_svg or self.dans_style:
            return
        self.cur.enfants.append(data)


# ---------------------------------------------------------------- SVG
def jetons_clairs(source):
    bloc = re.search(r":root\{(.*?)\}", source, re.S).group(1)
    return dict(re.findall(r"--([\w-]+):([^;]+);", bloc))


def css_svg(source, jetons):
    regles = re.findall(r"^svg(?:\.patron)? ([^{]+\{[^}]*\})", source, re.M)
    patron = re.findall(r"^svg\.patron ([^{]+\{[^}]*\})", source, re.M)
    css = "svg{font-family:" + jetons["f-body"] + "}\ntext{fill:" + jetons["fg"] + ";font-size:13px}\n"
    for r in regles:
        css += r + "\n"
    css = re.sub(r"var\(--([\w-]+)\)", lambda m: jetons[m.group(1)].strip(), css)
    return css, set(patron)


def exporter_svgs(source):
    jetons = jetons_clairs(source)
    css, _ = css_svg(source, jetons)
    css_patron = re.sub(r"var\(--([\w-]+)\)", lambda m: jetons[m.group(1)].strip(),
                        "\n".join("." + r for r in re.findall(r"^svg\.patron ([^{]+\{[^}]*\})", source, re.M)))
    blocs = re.findall(r"<svg\b.*?</svg>", source, re.S)
    defs = re.search(r"<defs>.*?</defs>", blocs[0], re.S).group(0)
    return blocs, defs, css, css_patron


def svg_autonome(bloc, defs, css, css_patron):
    ouvrante = re.match(r"<svg\b[^>]*>", bloc).group(0)
    corps = bloc[len(ouvrante):-len("</svg>")]
    patron = 'class="patron"' in ouvrante
    style = css + ("\n" + css_patron.replace(".text", ".patron text") if patron else "")
    if patron:
        style += "\ntext{font-size:5.5px}"
    ouvrante = ouvrante.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    return (f'{ouvrante}\n<style>\n{style}\n</style>\n<rect width="100%" height="100%" fill="#ffffff"/>\n'
            f"{defs}\n{corps}</svg>\n")


# ---------------------------------------------------------------- Markdown
class Rendu:
    def __init__(self, blocs_svg, defs, css, css_patron):
        self.blocs_svg, self.defs, self.css, self.css_patron = blocs_svg, defs, css, css_patron
        self.section = "page"
        self.compteur = {}
        self.fichiers = {}

    # -- en ligne
    def inline(self, n):
        if isinstance(n, str):
            return re.sub(r"\s+", " ", n)
        t = n.tag
        dedans = "".join(self.inline(e) for e in n.enfants)
        if t in ("b", "strong"):
            return f"**{dedans.strip()}**" if dedans.strip() else ""
        if t in ("i", "em"):
            return f"*{dedans.strip()}*" if dedans.strip() else ""
        if t == "code":
            return "`" + n.texte().replace("\n", " ") + "`"
        if t == "kbd":
            return f"<kbd>{n.texte()}</kbd>"
        if t == "a":
            href = n.attrs.get("href", "")
            if href.startswith("#"):
                return dedans
            return f"[{dedans.strip()}]({href})"
        if t == "br":
            return "<br>"
        if t == "img":
            return f"![[{n.attrs.get('src')}]]"
        return dedans

    def ligne(self, n):
        return re.sub(r"[ \t]+", " ", "".join(self.inline(e) for e in n.enfants)).strip()

    # -- blocs
    def blocs(self, noeud, niveau):
        out = []
        for e in noeud.enfants:
            if isinstance(e, str):
                if e.strip():
                    out.append(re.sub(r"\s+", " ", e).strip())
                continue
            out.extend(self.bloc(e, niveau))
        return out

    def bloc(self, n, niveau):
        t, c = n.tag, n.cls()
        if t in ("h2", "h3", "h4"):
            if n.attrs.get("id"):
                self.section = n.attrs["id"]
            lv = {"h2": niveau, "h3": niveau + 1, "h4": niveau + 2}[t]
            if lv > 5:
                return ["**" + self.ligne(n) + "**"]
            return ["#" * lv + " " + self.ligne(n)]
        if t == "p":
            s = self.ligne(n)
            return [s] if s else []
        if t in ("ul", "ol"):
            return ["\n".join(self.liste(n, t, 0))]
        if t == "table":
            return [self.table(n)]
        if t == "pre":
            code = n.texte().strip("\n")
            return ["```\n" + code + "\n```"]
        if t == "figure":
            return self.figure(n)
        if t == "details":
            return self.details(n, niveau)
        if t == "div" and "ex" in c:
            return self.exercice(n, niveau)
        if t == "div" and "goals" in c:
            titre = next(n.trouver(lambda x: x.tag == "h4"), None)
            corps = Noeud("div", [])
            corps.enfants = [e for e in n.enfants if e is not titre]
            return [self.callout("abstract", self.ligne(titre) if titre else "", self.blocs(corps, niveau))]
        if t == "div" and "note" in c:
            return [self.callout("note", "", self.blocs(n, niveau))]
        if t in ("div", "section", "header", "main", "span"):
            return self.blocs(n, niveau)
        return []

    def liste(self, n, t, prof):
        lignes = []
        for i, li in enumerate([e for e in n.enfants if isinstance(e, Noeud) and e.tag == "li"], 1):
            puce = f"{i}." if t == "ol" else "-"
            texte = "".join(self.inline(e) for e in li.enfants
                            if not (isinstance(e, Noeud) and e.tag in ("ul", "ol")))
            lignes.append("    " * prof + f"{puce} " + re.sub(r"\s+", " ", texte).strip())
            for sous in li.enfants:
                if isinstance(sous, Noeud) and sous.tag in ("ul", "ol"):
                    lignes.extend(self.liste(sous, sous.tag, prof + 1))
        return lignes

    def table(self, n):
        lignes = []
        for tr in n.trouver(lambda x: x.tag == "tr"):
            cells = [self.ligne(c).replace("|", "\\|") or " " for c in tr.enfants
                     if isinstance(c, Noeud) and c.tag in ("td", "th")]
            span = [int(c.attrs.get("colspan", 1)) for c in tr.enfants
                    if isinstance(c, Noeud) and c.tag in ("td", "th")]
            cells2 = []
            for cel, s in zip(cells, span):
                cells2 += [cel] + [" "] * (s - 1)
            lignes.append(cells2)
        if not lignes:
            return ""
        larg = max(len(l) for l in lignes)
        lignes = [l + [" "] * (larg - len(l)) for l in lignes]
        a_entete = next(n.trouver(lambda x: x.tag == "thead"), None) is not None
        if not a_entete:
            lignes.insert(0, [" "] * larg)
        md = ["| " + " | ".join(lignes[0]) + " |", "|" + "---|" * larg]
        md += ["| " + " | ".join(l) + " |" for l in lignes[1:]]
        return "\n".join(md)

    def figure(self, n):
        out = []
        svgs = list(n.trouver(lambda x: x.tag == "svg"))
        base = n.attrs.get("id", self.section).replace("fig-", "figure-")
        for e in n.trouver(lambda x: x.tag in ("svg", "img")):
            if e.tag == "img":
                out.append(f"![[{e.attrs['src']}]]")
                continue
            k = self.compteur.get(base, 0) + 1
            self.compteur[base] = k
            nom = f"{base}{'abcdef'[k - 1] if len(svgs) > 1 else ''}.svg"
            bloc = self.blocs_svg[e.attrs["_index"]]
            self.fichiers[nom] = svg_autonome(bloc, self.defs, self.css, self.css_patron)
            out.append(f"![[schemas/{nom}]]")
        cap = next(n.trouver(lambda x: x.tag == "figcaption"), None)
        if cap:
            out.append(self.ligne(cap))
        return ["\n".join(out)]

    def callout(self, genre, titre, blocs, replie=False):
        tete = f"> [!{genre}]{'-' if replie else ''} {titre}".rstrip()
        corps = []
        for b in blocs:
            if corps:
                corps.append(">")
            corps += ["> " + l if l else ">" for l in b.split("\n")]
        return "\n".join([tete] + corps)

    def details(self, n, niveau):
        som = next(n.trouver(lambda x: x.tag == "summary"), None)
        corps = Noeud("div", [])
        corps.enfants = [e for e in n.enfants if e is not som]
        return [self.callout("success", self.ligne(som) if som else "Correction", self.blocs(corps, niveau), True)]

    def exercice(self, n, niveau):
        h4 = next(n.trouver(lambda x: x.tag == "h4"), None)
        titre = ""
        if h4:
            ident = next(h4.trouver(lambda x: "id" in x.cls()), None)
            lvl = next(h4.trouver(lambda x: "lvl" in x.cls()), None)
            reste = Noeud("h4", [])
            reste.enfants = [e for e in h4.enfants if e is not ident and e is not lvl]
            titre = " · ".join(x for x in [ident.texte().strip() if ident else "", self.ligne(reste)] if x)
            if lvl:
                titre += f" ({lvl.texte().strip()})"
        if n.attrs.get("id"):
            self.section = n.attrs["id"]
        corps = Noeud("div", [])
        corps.enfants = [e for e in n.enfants if e is not h4]
        return [self.callout("question", titre, self.blocs(corps, niveau + 2))]


def sections(conteneur):
    """Découpe un conteneur de version en sections h2 : [(id, [noeuds])]."""
    res, cur = [], None
    for e in conteneur.enfants:
        if isinstance(e, Noeud) and e.tag == "h2":
            cur = (e.attrs.get("id"), [e])
            res.append(cur)
        elif cur is not None:
            cur[1].append(e)
    return res


PAIRES = [
    ("Plan général", "plan", "gp-plan"),
    ("Infrastructure", "infra", "gp-infra"),
    ("Séance 1", "s1", "gp-s1"),
    ("Séance 2", "s2", "gp-s2"),
    ("Séance 3", "s3", "gp-s3"),
    ("Séance 4", "s4", "gp-s4"),
    ("Mini-projets", "projets", "gp-projets"),
    ("Points à retenir", "retenir", "gp-retenir"),
    ("Catalogue des exercices", "catalogue", None),
    ("Lexique", None, "gp-lexique"),
    ("Mémo des commandes", "memo", "gp-memo"),
]


def main():
    source = PAGE.read_text(encoding="utf-8")
    arbre = Arbre()
    arbre.feed(source)
    blocs_svg, defs, css, css_patron = exporter_svgs(source)
    r = Rendu(blocs_svg, defs, css, css_patron)

    main_ = next(arbre.racine.trouver(lambda x: x.tag == "main"))
    header = next(main_.trouver(lambda x: x.tag == "header"))
    meta = next(header.trouver(lambda x: x.tag == "ul" and "meta" in x.cls()))
    versions = {n.attrs["data-v"]: n for n in main_.enfants
                if isinstance(n, Noeud) and n.tag == "div" and "data-v" in n.attrs}

    def du_header(v):
        meta_v = [li for li in meta.enfants if isinstance(li, Noeud) and li.attrs.get("data-v") == v]
        return meta_v + [e for e in header.enfants if isinstance(e, Noeud) and e.attrs.get("data-v") == v]

    titre = r.ligne(next(header.trouver(lambda x: x.tag == "h1")))
    commun = [li for li in meta.enfants if isinstance(li, Noeud) and li.tag == "li" and "data-v" not in li.attrs]

    out = [f"# {titre}", "",
           "<!-- Fichier généré depuis Deroulement-cours-opencode.html par outils/html_vers_md.py. -->",
           "<!-- Balises : #informaticien, #généraliste (portée : la section ### qui les précède), #tous, #note. -->",
           "", "#tous"]
    out += ["- " + r.ligne(li) for li in commun]
    out.append("")

    out += ["## Présentation et prérequis", ""]
    for v, balise, nom in (("expert", "#informaticien", "Version Informaticien"), ("gp", "#généraliste", "Version Généraliste")):
        out += [f"### {nom}", balise, ""]
        for e in du_header(v):
            if e.tag == "li":
                out.append("- " + r.ligne(e))
                continue
            for b in r.bloc(e, 4):
                out += [b, ""]
        out.append("")

    secs = {v: dict(sections(versions[v])) for v in ("expert", "gp")}
    for nom, ide, idg in PAIRES:
        out += [f"## {nom}", ""]
        for v, ident, balise in (("expert", ide, "#informaticien"), ("gp", idg, "#généraliste")):
            if not ident:
                continue
            noeuds = secs[v][ident]
            h2, reste = noeuds[0], noeuds[1:]
            r.section = ident
            out += [f"### {r.ligne(h2)}", balise, ""]
            for e in reste:
                if isinstance(e, str):
                    if e.strip():
                        out += [e.strip(), ""]
                    continue
                for b in r.bloc(e, 3):
                    out += [b, ""]
    texte = "\n".join(out)
    texte = re.sub(r"\n{3,}", "\n\n", texte).rstrip() + "\n"
    MD.write_text(texte, encoding="utf-8")

    SCHEMAS.mkdir(exist_ok=True)
    for f in SCHEMAS.glob("*.svg"):
        if f.name not in r.fichiers:
            f.unlink()
    for nom, contenu in r.fichiers.items():
        (SCHEMAS / nom).write_text(contenu, encoding="utf-8")
    print(f"{MD.name} : {len(texte.splitlines())} lignes, {len(r.fichiers)} schémas")


if __name__ == "__main__":
    main()
