# The World Today — Wednesday 25 November 2026

An entry for make.fun's `news-image-20261125` competition: one image that
sums up the world's news of Wednesday 25 November 2026.

`main.py` (Python 3.13, standard library only) draws the whole page itself
— masthead, six story tiles, footer — and writes it to
`/output/entry.png`. No network, no files read, no fonts on disk: the
letters are a small 5×7 pixel font defined in the code, and every picture
is drawn from rectangles, circles and triangles.

The six stories, as reported on the morning of 25 November 2026:

1. **Ukraine war** — Ukraine hits two Russian ships (Gulf of Finland, off Libya)
2. **Middle East** — Houthi drone hits Riyadh's tallest tower, 11 wounded
3. **Tech on trial** — Huawei convicted in a US court over its Iran business
4. **Markets** — Huang back at Nvidia; shares jump 31% in a day
5. **China** — Shanghai party chief Chen Jining under corruption probe
6. **Weather** — King tides flood the California coast, record tide in San Francisco

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png`: a 1024×1024 PNG, about 21 KB. Run it twice
and the two files are byte-identical (same sha256) — the PNG carries no
timestamps or metadata.

## Note

The story list was picked from the morning's reporting and is refreshed
with the full day's news before the entry is submitted, since the
competition's deadline falls after 25 November has ended everywhere.
