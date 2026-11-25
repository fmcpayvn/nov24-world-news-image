# nov24-world-news-image

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/fmcpayvn/nov24-world-news-image/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/fmcpayvn/nov24-world-news-image/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A single newspaper front page that carries the whole of Tuesday 24 November 2026: **45 stories from 6 continents**, each checked against reporting published on 23–24 November 2026. The front page leads with tankers burning in the Strait of Hormuz as Iran tightens the strait, followed by the Huawei guilty verdict in Brooklyn and Senegal getting their Africa Cup of Nations title back at the sports court. Below that, every continent gets its own column of the day's headlines — North America, South America, Europe, Africa, Asia, and Oceania & Science.

![The world in one image, 24 November 2026](entry.png)

## How the page is laid out

Top to bottom: the masthead with the dateline, the lead story in large type, the two second leads side by side, then six continent sections in a three-by-two grid, each with its seven headlines, and a footer counting the coverage. The section text shrinks just enough to fit the page — the renderer measures every headline and picks the largest body size that still leaves the footer clear, so nothing is ever cut off at the bottom edge.

## Checking the entry

```sh
MAKEFUN_OUTPUT_DIR=/tmp/check python3 main.py
```

Copies `entry.png` to `/tmp/check/` and reports its size; it stops with an error if the copy is not a PNG or its size differs from the original.

## Run it

```sh
python3 render.py
```

Redraws `entry.png` (1024×1024) from `stories.json` using Python and Pillow — no network, no external assets, DejaVu fonts only. Pass an output path to write somewhere else instead, e.g. `python3 render.py /tmp/preview.png`.

## Files

- `entry.png` — the submitted front page
- `stories.json` — the 45 verified stories: lead, second leads, and the six continent sections, with sources
- `render.py` — the script that draws the front page from `stories.json`
- `main.py` — the entrypoint: copies `entry.png` into the grader's output directory (`MAKEFUN_OUTPUT_DIR`, default `out`) and checks the copy

---

<sub>Entered on [make.fun](https://make.fun/bounty/news-image-20261124) as @thucthai7814.</sub>
