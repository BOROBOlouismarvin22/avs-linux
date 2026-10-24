# AVS Computer Assistant (version Linux / WSL 2)

Outil de diagnostic informatique avec interface graphique (Python et Tkinter). Il examine une machine (mémoire, processeur, stockage, processus, réseau, programmes au démarrage), cherche les causes probables d'un problème, recommande des actions et produit un rapport.

À l'origine, l'outil analysait **Windows**. Ce dépôt contient la version adaptée pour **Linux** (Ubuntu sous WSL 2), avec la même base de code : seules les « sondes » qui lisent la machine ont été réécrites pour Linux.

## Ce que fait l'outil

- **Tableau de bord** : mémoire, processeur, stockage et processus, avec un état global.
- **Diagnostic complet** : enchaîne toutes les analyses.
- **Mémoire, processeur, stockage** : mesures et jugement (OK, faible, critique).
- **Processus** : les 10 processus les plus gourmands.
- **Réseau** : test de connexion (ping), résolution DNS, latence et perte de paquets.
- **Réseau détaillé** : interfaces (état, IP, MAC), passerelle, serveurs DNS et ports TCP en écoute.
- **Programmes au démarrage**.
- **Causes probables et actions recommandées**.
- **Informations système** : processeur, machine, carte graphique.
- **Rapport technique** au format texte.

## État du projet

Testé avec : Windows 11, WSL 2, Ubuntu 26.04, Python 3.14, psutil 7.2.2, processeur Intel Pentium 6405U.

- Chaque page de l'interface a été vérifiée à la main sous Linux, et un rapport complet est généré.
- Linux tourne ici dans une **machine virtuelle** : les mesures décrivent cette machine virtuelle (par exemple la mémoire allouée à WSL), pas le PC Windows entier. Certaines informations matérielles (modèle de disque, carte graphique, batterie) sont limitées.
- Le code Windows d'origine est conservé et reste utilisé sous Windows, mais il n'a pas été retesté après l'adaptation.

### Limites connues

- Le mot « ATTENTION » du tableau de bord est affiché en vert : à vérifier.
- L'outil juge « limitée » la mémoire de Linux (1,8 Go), qui n'est que la part prêtée par Windows : il devrait détecter qu'il tourne dans une machine virtuelle.
- Les programmes au démarrage sont lus dans les fichiers d'autostart ; les services `systemd` sont à ajouter.
- La sonde batterie n'a pas encore été examinée pour Linux.
- La page « Réseau détaillé » n'est pas encore intégrée au rapport texte.
- La sonde réseau détaillée prévoit une branche Windows : testée par simulation et vérifiée à la main sur Windows 11 (sonde seule, sans l'interface).

## Installation

```bash
sudo apt update
sudo apt install python3-venv python3-tk git
git clone https://github.com/BOROBOlouismarvin22/avs-linux.git
cd avs-linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

### Affichage de la fenêtre sous WSL 2

Normalement, WSL 2 affiche seul les fenêtres Linux (WSLg). Sur ma machine, l'affichage intégré plantait au démarrage (`couldn't connect to display ":0"`). J'ai contourné le problème avec un serveur d'affichage Windows, **VcXsrv** :

1. Installer VcXsrv (`winget install --id marha.VcXsrv -e --source winget`).
2. Le lancer avec XLaunch : fenêtres multiples, affichage 0, aucun client, presse-papiers activé, OpenGL natif désactivé, contrôle d'accès désactivé (le pare-feu reste actif).
3. Dans Ubuntu, avant de lancer l'outil :

```bash
export DISPLAY=$(ip route show default | awk '{print $3}'):0.0
python main.py
```

## Architecture

```
avs/
  ui/             interface graphique (Tkinter)
  orchestrator/   enchaîne les analyses
  diagnostics/    interprète les mesures (CPU, RAM, disque, réseau, processus...)
  decision/       actions recommandées
  reporting/      rapport texte
  system/         sondes : lecture de la machine (seule partie propre à l'OS)
tests/            tests automatiques
tools/            scripts utilisés pour le portage vers Linux
main.py           point d'entrée
```

Principe : le code qui lit la machine est isolé dans `avs/system/`. L'interface et les diagnostics ne changent pas. Sous Linux, `avs/system/linux_compat.py` fournit les mêmes résultats que les sondes Windows.

| Donnée | Windows | Linux |
|---|---|---|
| Charge du processeur, mémoire, disque | API Windows (ctypes) | `psutil` |
| Nom du processeur | Registre Windows | `/proc/cpuinfo` |
| Machine (fabricant, modèle) | Registre Windows | `/sys/class/dmi/id`, ou « WSL 2 » si absent |
| Carte graphique | Registre Windows | `lspci`, ou `/dev/dxg` sous WSL |
| Programmes au démarrage | Clés Run du registre | Fichiers `.desktop` d'autostart |
| Test réseau | `ping -n` | `ping -c -W` |
| Passerelle et DNS | `route print`, PowerShell | `/proc/net/route`, `/etc/resolv.conf` |

Les scripts `tools/patch_linux.py` et `tools/patch_reseau.py` ont servi à appliquer ces changements sur une copie du projet. Ils sont déjà appliqués dans ce dépôt.

## Tests

Le dossier `tests/` contient des tests automatiques de la logique de diagnostic (`pytest`). Les 100 tests passent sous Linux (Python 3.14), dont 17 pour la sonde réseau détaillée. Pour les lancer :

```bash
pip install pytest
python -m pytest tests -q
```

## Méthode de travail

Projet réalisé étape par étape, avec l'aide d'un assistant d'IA (Claude) pour guider le diagnostic et préparer des scripts. Chaque commande a été exécutée et chaque résultat vérifié par moi.
