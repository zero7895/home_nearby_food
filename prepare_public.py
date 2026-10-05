"""Build the shareable Site without the editor's precise home address or route origin."""
import json, re
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import urlencode, unquote
ROOT=Path(__file__).resolve().parent
DEST=ROOT/'published-site'/'dist'
DEST.mkdir(parents=True,exist_ok=True)
data=json.loads((ROOT/'restaurants.json').read_text())
# Publish only fields used by the UI; retain full research evidence locally.
data = {'places': data['places'], 'taxonomy': data['taxonomy']}
unused = ['sources','photoSource','routeVia','driveVia','classificationBasis','checkedAt']
for place in data['places']:
    for field in unused:
        place.pop(field, None)
    for field,mode in [('routeUrl','walking'),('driveRouteUrl','driving')]:
        place[field]='https://www.google.com/maps/dir/?'+urlencode({'api':1,'destination':place['name']+' '+place['address'],'travelmode':mode})
(DEST/'data.js').write_text('window.NEARBY_DATA = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
updated=datetime.now(ZoneInfo('Asia/Taipei')).replace(microsecond=0)
source_html=(ROOT/'index.html').read_text()
source_html=re.sub(r'<time id="site-updated"[^>]*>.*?</time>',f'<time id="site-updated" datetime="{updated.isoformat()}">{updated:%Y-%m-%d %H:%M:%S}</time>',source_html)
(ROOT/'index.html').write_text(source_html)
html=source_html.replace('你的出發點','探索區域').replace('板橋區民生路二段240巷68號','板橋・新埔生活圈').replace('↗ 從家出發','↗ 新埔生活圈').replace('僅用於本地預覽','供附近美食參考').replace('LOCAL PREVIEW · 2026','NEIGHBORHOOD BITES · 2026').replace('步行與開車時間以住家所在社區為起點','步行與開車時間以編輯者在新埔生活圈的固定起點為準')
(DEST/'index.html').write_text(html)
js=(ROOT/'app.js').read_text().replace('Google 步行導航 ↗','規劃步行路線 ↗').replace('Google 開車導航 ↗','規劃開車路線 ↗').replace('Google 路線估計以社區地圖起點為準','本頁時間以編輯者固定起點查核；導航由你自行選擇出發地點')
(DEST/'app.js').write_text(js)
(DEST/'style.css').write_text((ROOT/'style.css').read_text())
public=''.join(unquote(p.read_text()) for p in DEST.iterdir() if p.suffix in ['.js','.css','.html'])
assert '240巷68' not in public and '欣璞綻' not in public
assert not any('origin=' in p[field] for p in data['places'] for field in ['routeUrl','driveRouteUrl'])
assert len(data['places'])==500+len(json.loads((ROOT/'expansion-more-metadata.json').read_text()))+len(json.loads((ROOT/'expansion-next-metadata.json').read_text()))
print(f'Prepared public Site: {len(data["places"])} stores, {sum(len(p["photos"]) for p in data["places"])} photos; private address and navigation origin removed.')
