# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Nature du dépôt

Ce n'est pas un dépôt de code : c'est un dépôt git de supports de cours, servant à préparer un cours/TP de l'INSA de Lyon sur le **développement agentique avec opencode** (4 séances). Pas de build, lint ni tests. Le dépôt est `/Users/sfrenot/cours/Agentique`, public sur GitHub (`sfrenot/cours-agentique-opencode`) et servi par GitHub Pages (https://sfrenot.github.io/cours-agentique-opencode/, `index.html` redirige vers la page du cours). Le dossier Obsidian `~/Documents/Obsidian Vault/IA/Cours Agentique` est un lien symbolique vers ce dépôt, pour que Stéphane édite le markdown dans Obsidian.

Stéphane a demandé (26/11/2026) que chaque modification validée soit **commitée et poussée automatiquement** sur `main` : après chaque changement, faire `git commit` puis `git push` sans redemander. Exception : jamais de réécriture d'historique ni de `push --force` sans son accord explicite.

## Fichiers

| Fichier | Rôle |
|---|---|
| `Deroulement-cours-opencode.html` | **Référence** : la page du cours, deux versions basculées par un bouton : « Informaticien » (éléments `data-v="expert"`) et « Généraliste », pour les non-informaticiens (éléments `data-v="gp"`, ids préfixés `gp-`). Publiée aussi comme artifact : https://claude.ai/artifact/Rx2FmVLM7Y9pthaLLGaowN (republier avec le même `file_path`, en joignant `images/opencode-lancement.png` via `files`). |
| `Cours - Développement d'une application par la voie agentique.md` | **Miroir de la page**, généré par `python3 outils/html_vers_md.py` (exercices en callouts Obsidian, schémas dans `schemas/*.svg`). |
| `outils/html_vers_md.py` | Régénère le markdown et `schemas/` à partir de la page. |
| `images/`, `schemas/` | Capture d'écran d'opencode ; schémas SVG exportés de la page (ne pas éditer à la main). |
| `Instruction.md` | Commande de travail de Stéphane. Ne pas modifier. |

## Règle de synchronisation markdown ↔ page (depuis le 26/11/2026)

Le markdown doit **toujours être en phase** avec la page HTML. Claude le maintient à jour.

1. **Stéphane corrige le markdown** (dans Obsidian) et le signale. Lire `git diff` sur le markdown, reporter chaque changement dans la page selon les balises ci-dessous, republier la page, **puis régénérer** le markdown avec `python3 outils/html_vers_md.py`. Vérifier par `git diff` que rien de ce qu'il a écrit n'a disparu dans la régénération (sinon, c'est que le report dans la page est incomplet).
2. **Claude modifie la page** (demande directe) : régénérer le markdown dans la foulée.
3. Dans les deux cas : commit + push des deux fichiers (et de `schemas/`).

Balises du markdown :
- `#généraliste` (ou `#generaliste`, anciennes `#autre`, `#grandpublic`) → version « Généraliste » ;
- `#informaticien` → version « Informaticien » ;
- `#tous` → les deux versions ;
- `#note` en ligne → remarque à ajouter en encadré `<div class="note">` à l'endroit correspondant, dans les deux versions (rédigée simplement pour la Généraliste), sauf autre balise.

Dans le markdown généré, chaque section `##` contient deux sous-sections `###` suivies de leur balise ; la balise vaut pour toute la sous-section `###`. Un texte ajouté sans balise sous une sous-section suit la balise de cette sous-section.

## Livrables attendus (d'après `Instruction.md`)

Un plan précis du cours sur 4 séances ; des schémas explicatifs ; un document HTML autonome avec le déroulé des séances, des exercices d'appui et une liste d'exercices types avec corrections. Objectifs pédagogiques : programmer des applications simples par la voie agentique ; interagir avec le CLI opencode ; comprendre l'architecture fonctionnelle d'opencode ; comprendre sa maintenance et sa réinitialisation.

## Contraintes techniques du cours

- Outil : **opencode** (v2.4.1), sur une machine distante (la machine d'accès). Pour la préparation, Stéphane donne le compte et le nom de la machine.
- Modèles via **LiteLLM** (réseau INSA) : `litellm/ll_wired-qwen3.8:27b-mlx` (raisonnement, 110k tokens, sortie 8 192, 16 Go en mémoire) et `litellm/ll_wired-qwen3.5:0.8b` (agents légers, 500 Mo). `opencode/big-pickle` (OpenCode Zen, hors INSA) est le modèle proposé par défaut.
- Modèles peu puissants : **exemples et exercices simples** (petits scripts, petites tâches, peu d'étapes).

## Dépôt public : noms de machines

Ne jamais écrire les vrais noms des machines internes : la passerelle LiteLLM s'appelle `gatewayllm` (port 4000), le serveur des modèles (Mac Studio) `serveurllm`. La machine de TP n'est pas nommée : « la machine d'accès » et `<machine-acces>` dans les commandes ; le bureau virtuel est cité sans son adresse. Les noms de modèles `litellm/ll_wired-…` restent inchangés. Vérifier toute image ajoutée (barres de titre, invites de shell).

## Conventions de réponse

- Rédiger en français.
- Inclure le prénom **Stéphane** dans les réponses.
