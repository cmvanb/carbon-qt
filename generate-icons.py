#!/usr/bin/env python3
"""Generate the carbon Qt icon theme for one variant.

Usage: generate-icons.py dark|light DEST

The theme completes Win11: it inherits the variant's Win11 themes and
overrides the names listed in icons/icons.tsv with sources recolored to the
variant's ink.
"""
import re
import shutil
import sys
from pathlib import Path

ICON_ROOT = Path('/usr/share/icons')
HERE = Path(__file__).resolve().parent

# Win11's own monochrome ink, so overrides match the inherited icons.
INK = {'dark': '#dedede', 'light': '#363636'}
INHERITS = {'dark': 'Win11-dark,Win11,hicolor', 'light': 'Win11,hicolor'}

# Monochrome glyph colors across Win11's light, dark and tray-panel art.
GLYPH = re.compile(r'#(?:363636|dedede|f2f2f2|fefefe|ffffff)\b', re.IGNORECASE)


def read_table(path):
    rows = []
    for line in path.read_text().splitlines():
        if line and not line.startswith('#'):
            name, context, source = line.split('\t')
            rows.append((name, context, source))
    return rows


def resolve(source):
    base = ICON_ROOT if source.startswith('Win11') else HERE / 'icons'
    return (base / source).resolve()


def index_theme(variant, contexts):
    directories = ','.join(f'scalable/{c}' for c in contexts)
    sections = ''.join(
        f'\n[scalable/{c}]\nContext={c.capitalize()}\nSize=16\nMinSize=8\nMaxSize=512\nType=Scalable\n'
        for c in contexts
    )
    return (
        f'[Icon Theme]\nName=carbon-{variant}-qt\nComment=Carbon {variant} icons for Qt, completing Win11\n'
        f'Inherits={INHERITS[variant]}\nDirectories={directories}\n{sections}'
    )


def main():
    variant, dest = sys.argv[1], Path(sys.argv[2])
    rows = read_table(HERE / 'icons' / 'icons.tsv')
    contexts = sorted({context for _, context, _ in rows})

    shutil.rmtree(dest, ignore_errors=True)
    for context in contexts:
        (dest / 'scalable' / context).mkdir(parents=True)
    (dest / 'index.theme').write_text(index_theme(variant, contexts))

    for name, context, source in rows:
        svg = GLYPH.sub(INK[variant], resolve(source).read_text())
        (dest / 'scalable' / context / f'{name}.svg').write_text(svg)


if __name__ == '__main__':
    main()
