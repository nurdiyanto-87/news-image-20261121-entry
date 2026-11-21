# The World in One Day — Saturday 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/nurdiyanto-87/news-image-20261121-entry/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/nurdiyanto-87/news-image-20261121-entry/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

Entry for the [make.fun competition `news-image-20261121`](https://make.fun/bounty/news-image-20261121): one image summing
up the world news of Saturday 21 November 2026.

`main.py` (Python 3.13, standard library only) draws a newspaper front page
programmatically — masthead with the date, six story panels with simple
vector pictograms, and a footer ticker — and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). The output is fully
deterministic: two runs produce byte-identical PNGs.

## Stories pictured

1. **War** — Russia's biggest strike on Ukraine (400+ drones, 110 missiles),
   with two missiles landing in Poland.
2. **Markets** — AI stock sell-off: S&P 500 −3.7%, Nasdaq −5.3%, into
   correction.
3. **Justice** — ICJ finds Myanmar responsible for genocide against the
   Rohingya.
4. **Europe** — UK and EU sign their biggest post-Brexit agreements.
5. **Climate** — COP31 talks in Antalya run past deadline over fossil fuels.
6. **Disaster** — Magnitude 6.9 earthquake in the Peruvian Andes.

Footer ticker: Houthi missiles at Riyadh intercepted, FBI crime-database
hack, pancreatic-cancer trial pill, Gen Z protests across 25 European
countries.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see `LICENSE`.
