# -*- coding: utf-8 -*-

"""
AVS COMPUTER ASSISTANT
======================

AVS PORTABLE LAUNCHER

Point d'entrée de la version portable d'AVS.
"""

import sys
from pathlib import Path


def prepare_environment():
    """Prépare l'environnement Python."""

    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parents[2]

    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))


def main():
    """Lance l'interface graphique AVS."""

    prepare_environment()

    from avs.ui.app import AVSApplication

    app = AVSApplication()
    app.mainloop()


if __name__ == "__main__":
    main()