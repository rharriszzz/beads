"""Build the prefix-only lookup table. Run as a module from the repository root."""
import csv
from pathlib import Path

from photo2.alternate_views.analyze import write_csv
from photo2.alternate_views.registration import candidates

OUT = Path(__file__).resolve().parent
WORD = OUT.parents[1] / 'r344/provisional-sequence.txt'
HORIZON = 12
ORIENTATION = {'wood': (7, 6), 'plastic': (-7, -6)}


def readings(file):
    with file.open() as stream:
        for row in csv.DictReader(stream):
            points = []
            for encoded in row['points'].split():
                x, y, color = encoded.split(':')
                points.append((int(x), int(y), color))
            yield (row['view'], int(row['eighth'])), points


def forecast():
    word = WORD.read_text().strip()
    rows = []
    for (view, eighth), points in readings(OUT / 'prefix.csv'):
        if any(x >= 300 for x, _, _ in points):
            raise ValueError('Prefix extends past the visible window')
        down, up = ORIENTATION[view]
        starts = []
        for fit in candidates(points, word):
            if fit['orientation'] != (down, up):
                continue
            if all(obs == '?' or obs == pred
                   for (_, _, obs), pred in zip(points, fit['prediction'], strict=True)):
                starts.append(fit)
        phases = ' '.join(str(fit['phase']) for fit in starts)
        for step in range(1, HORIZON + 1):
            for inward in range(step + 1):
                delta = inward * down + (step - inward) * up
                residues = sorted({(fit['positions'][-1] + delta) % len(word) for fit in starts})
                rows.append(dict(view=view, eighth=eighth, step=step, inward=inward,
                                 phases=phases, residues=' '.join(map(str, residues)),
                                 colors=''.join(sorted({word[k] for k in residues}))))
    return rows


if __name__ == '__main__':
    write_csv(OUT / 'forecast.csv', forecast())
