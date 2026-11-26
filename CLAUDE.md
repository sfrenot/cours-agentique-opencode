# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Nature du dépôt

Ce n'est pas un dépôt de code : c'est un dépôt git de supports de cours, servant à préparer un cours/TP de l'INSA de Lyon sur le **développement agentique avec opencode** (4 séances). Pas de build, lint ni tests. Le dépôt est `/Users/sfrenot/cours/Agentique`. Le dossier Obsidian `~/Documents/Obsidian Vault/IA/Cours Agentique` est un lien symbolique vers ce dépôt, pour que Stéphane continue à éditer le markdown dans Obsidian. Ne pousser vers GitHub qu'avec son accord.

## Fichiers sources (NE PAS MODIFIER)

- `Instruction.md` — la commande de travail : rôle (enseignant-chercheur INSA), objectifs, moyens, plan attendu.
- `Cours - Développement d'une application par la voie agentique.md` — le contenu de référence du cours (niveaux d'interaction prompt → prompt engineering → RAG → harness/context engineering, boucle agentique, harnais vs contexte, briques d'opencode : outils, contexte, mémoire, permissions, undo/redo, orchestration par agents).

Consigne explicite : **ne jamais modifier ces fichiers initiaux**. Toute production va dans de nouveaux fichiers.

## Livrables attendus (d'après `Instruction.md`)

1. Un plan précis du cours sur 4 séances.
2. Des schémas explicatifs, en réutilisant ceux déjà présents dans le cours (diagrammes Mermaid `sequenceDiagram`/`flowchart`, schéma ASCII de la boucle, tableau Harnais vs Contexte).
3. Un document **HTML autonome** visualisable dans un navigateur, décrivant le déroulé des séances avec exercices d'appui et **liste d'exercices types avec corrections**.

Objectifs pédagogiques à couvrir : programmer des applications simples mais démonstratives par la voie agentique ; interagir avec le CLI opencode ; comprendre l'architecture fonctionnelle d'opencode ; comprendre la maintenance et la réinitialisation d'opencode (sessions, `/resume`, `/sessions`, `/fork`, `/clear`, `/compact`, `/undo`, `/redo`, base de sessions en tâche de fond).

## Contraintes techniques du cours

- Outil : **opencode**, sur une machine distante (la machine d'accès). Pour la préparation, Stéphane donne le compte et le nom de la machine (voir `Instruction.md`).
- LLM disponibles uniquement via un serveur **LiteLLM** (réseau INSA) :
  - `ll-qwen3.8:27b-mlx` pour le raisonnement (fenêtre déclarée 110k tokens dans opencode, sortie max 8 192) ;
  - `litellm/ll_wired-qwen3.5:0.8b` pour démontrer des agents/sous-agents légers.
- Ces modèles sont peu puissants : **exemples et exercices doivent rester simples** (petits scripts, petites tâches, peu d'étapes).
- Les exercices prévus dans le cours incluent : comparaison `test1`/`test2` (prompt direct vs `@greeting.md` + `/export`), un sous-agent d'exécution Python distante (machine indiquée dans le fichier de description de l'agent), un fichier agent d'exploration web utilisant le modèle 0.8b.

## Page HTML produite

`Deroulement-cours-opencode.html` contient deux versions du cours, basculées par un bouton : version informatique (éléments `data-v="expert"`) et version « Autre », destinée aux non-informaticiens (éléments `data-v="gp"`, ids préfixés `gp-`). Elle est publiée comme artifact : https://claude.ai/artifact/Rx2FmVLM7Y9pthaLLGaowN (republier avec le même `file_path` après chaque modification).

## Corrections de Stéphane : balises dans le markdown source

Stéphane corrige directement `Cours - Développement d'une application par la voie agentique.md` (lui seul le modifie, Claude ne le modifie jamais) et signale chaque correction. Le texte est balisé :
- `#autre` → à reporter dans la version « Autre » (`data-v="gp"`) ; l'ancienne balise `#grandpublic` a le même sens ;
- `#informaticien` → à reporter dans la version informatique (`data-v="expert"`) ;
- `#tous` → à reporter dans les deux versions.

Une balise placée sous un titre vaut pour toute la section, jusqu'au titre suivant de même niveau ou de niveau supérieur. Une balise en fin de ligne ne vaut que pour cette ligne. Un passage sans balise reste sans effet sur la page, sauf demande explicite. Relire le HTML avant de l'éditer, puis republier.

## Dépôt public : noms de machines

Le dépôt est public. Ne jamais écrire les vrais noms des machines internes dans la page HTML ni dans les fichiers produits : la passerelle LiteLLM s'appelle `gatewayllm` (port 4000), le serveur des modèles (Mac Studio) s'appelle `serveurllm`. La machine de TP n'est pas nommée non plus : on écrit « la machine d'accès » et `<machine-acces>` dans les commandes (son nom est communiqué aux participants avec leur accès), et le bureau virtuel est cité sans son adresse. Les noms de modèles `litellm/ll_wired-…` sont des identifiants réels et restent inchangés.

## Conventions de réponse

- Rédiger en français.
- Inclure le prénom **Stéphane** dans les réponses.
- La capture citée par le markdown (`![[Capture d’écran 2026-11-19 à 11.26.11.png]]`) a été copiée à la racine du dépôt ; elle n'est pas utilisée dans le HTML.
