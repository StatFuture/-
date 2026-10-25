from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
dest=ROOT/'_site/v2'
dest.mkdir(parents=True,exist_ok=True)
(dest/'index.html').write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>团队网站已迁移</title><link rel="canonical" href="https://statfuture.github.io/hao-team/"><script>location.replace(\'https://statfuture.github.io/hao-team/\'+location.search+location.hash)</script></head><body><p>团队网站已迁移至<a href="https://statfuture.github.io/hao-team/">新网址</a>。</p></body></html>',encoding='utf-8')
