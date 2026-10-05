"""Integrate candidates only after observed walking/driving routes and dish evidence."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
read=lambda f:json.loads((ROOT/f).read_text())
shops=read('expansion-next-maps.json')+read('expansion-next-new-maps.json')
routes=read('expansion-next-routes.json'); dishes=read('expansion-next-dishes.json')
lookup={(r['name'],r['mode']):r for r in routes}
rules={};source=(ROOT/'classify_expansion.py').read_text();exec(source[:source.index('route_lookup=')],rules)
# Classification follows each store's observed category and concrete menu evidence.
profiles={
0:('日式','飯類,丼飯','日式定食與飯類主餐，適合日常午晚餐。'),
1:('台式','鐵板燒','鐵板燒與海陸套餐，適合午晚餐或朋友聚餐。'),
2:('泰式','咖啡廳,飯類,甜點店','咖啡、打拋豬飯與手作蛋糕，適合用餐或午後聊天。'),
3:('其他異國料理','餐酒館,飯類','精釀啤酒搭配創意餐點與燉飯，適合晚間朋友聚會。'),
4:('日式','燒肉,餐酒館','日式燒肉與餐酒，適合朋友聚餐或約會。'),
5:('中式','小吃,飯類,麵店','沙縣小吃、煎餃與飯類主餐，適合日常用餐或外帶。'),
6:('台式,義式','餐酒館,義大利麵,披薩','融合台味與義式餐點，適合晚間朋友聚餐。'),
7:('日式','火鍋','鍋物與壽喜燒，適合午晚餐或多人聚餐。'),
8:('日式','壽司,丼飯','日式丼飯與壽司料理，適合午晚餐或一人用餐。'),
9:('日式','拉麵','雞湯拉麵與炸物，適合午晚餐或一人用餐。'),
11:('美式','牛排','牛排套餐與西式料理，適合朋友聚餐或約會。'),
12:('日式','壽司','迴轉壽司與日式配餐，適合日常午晚餐。'),
13:('美式','早午餐','法式吐司與早午餐主餐，適合白天用餐。'),
14:('台式,港式','早午餐','早午餐特餐與漢堡套餐，適合白天用餐。'),
15:('美式','咖啡廳,早午餐','可頌主餐、咖啡與茶飲，適合早午餐或聊天。'),
16:('美式','咖啡廳,早午餐','佛卡夏、濃湯與咖啡，適合白天用餐。'),
17:('台式,美式','早午餐','蛋餅、捲餅與早餐輕食，適合白天用餐。'),
19:('美式','早午餐','雞腿排、漢堡與早午餐，適合白天聚餐。'),
21:('台式,美式','早午餐','三明治與肉餅漢堡，適合早餐、早午餐或外帶。'),
23:('台式','早餐店,麵店','蛋餅、熱壓吐司與肉燥麵，適合早餐或早午餐。'),
24:('不適用（咖啡／茶飲）','咖啡廳,甜點店','特色咖啡與巴斯克蛋糕，適合午後休息。'),
25:('不適用（咖啡／茶飲）','飲料店','紅茶與豆漿紅茶，適合外帶飲品。'),
26:('台式,美式','早餐店,飯類,麵店','蛋餅、炒麵與燉飯，適合早餐或白天用餐。'),
29:('台式','早餐店,小吃','皮蛋瘦肉粥與飲品，適合早餐或外帶。'),
30:('台式','小吃,麵店,飯類','鮮蚵、小卷與飯麵小吃，適合日常午晚餐。'),
33:('台式','咖啡廳,麵店','咖啡與家常輕食，適合用餐或午後聊天。'),
37:('義式','咖啡廳,義大利麵','咖啡與麵疙瘩餐點，適合白天用餐或聊天。'),
38:('其他異國料理','咖啡廳,飯類','咖啡與牛肉飯套餐，適合白天用餐。'),
39:('美式','咖啡廳,甜點店,早午餐','吐司輕食、特色拿鐵與甜點，適合白天聚會。'),
42:('台式,泰式','咖啡廳,飯類','咖啡、飯類主餐與鬆餅，適合用餐或朋友聚會。'),
43:('美式','咖啡廳,甜點店','咖啡、烤吐司與起司蛋糕，適合午後休息。'),
45:('美式','咖啡廳,早午餐','酸種三明治與咖啡，適合白天用餐。'),
48:('不適用（咖啡／茶飲）','咖啡廳','咖啡、嫩蛋堡與小點心，適合外帶或短暫休息。'),
49:('台式','甜點店','芋頭冰品與雪花冰，適合外帶點心。'),
51:('其他異國料理','酒吧','特色調酒，適合晚間小酌與朋友聊天。'),
52:('美式','咖啡廳,早午餐,甜點店','荷蘭小鬆餅、蛋捲與咖啡，適合白天聚會。'),
53:('美式','咖啡廳,早午餐','鹹派、可頌與咖啡，適合輕食或午後休息。'),
54:('台式,韓式','飯類,火鍋','陶飯、焗烤與鍋物，適合午晚餐或朋友聚餐。'),
55:('台式','甜點店','布丁與蛋糕甜點，適合外帶分享。'),
58:('美式,日式','早午餐,飯類','早午餐吐司、炸雞與咖哩飯，適合白天用餐。'),
59:('中式','熱炒','酸菜魚搭配小菜與加料，適合朋友或家庭分食。'),
60:('其他異國料理','餐酒館,酒吧','英式炸魚薯條、蘇格蘭蛋與主餐，適合晚間聚餐。')}
metadata={}
for idx,p in enumerate(shops):
 p['rating']=str(p.get('rating') or 0);p['reviews']=str(p.get('reviews') or 0)
 if idx==22:p['excludedReason']='業主公告手傷休養，10月營業時間另行公布；恢復營業未確認，暫不新增'
 if p.get('excludedReason'):continue
 w=lookup.get((p['name'],'walking'));d=lookup.get((p['name'],'driving'))
 if not w or not d:p['excludedReason']='步行或開車路線尚未查證';continue
 wm=int(re.search(r'(\d+) 分',w['options'][0]).group(1));dm=int(re.search(r'(\d+) 分',d['options'][0]).group(1))
 if wm>20 and dm>15:p['excludedReason']='超過步行20分鐘且開車15分鐘範圍';continue
 assert not p.get('closed') and float(p['rating'])>0 and len({u.split('=')[0] for u in p['photos']})>=5
 m=rules['enrich'](p,rules['classify'](p))
 if idx in profiles:
  c,t,desc=profiles[idx];m.update(cuisines=c.split(','),types=t.split(','),description=desc)
 if idx in [18,20,27,31,32,34,35,36]:m.update(cuisines=['台式'],types=['早餐店'],description='早餐、輕食與飲品，適合白天用餐或外帶。')
 if idx in [40,41,46,47,50,57]:m.update(cuisines=['不適用（咖啡／茶飲）'],types=['咖啡廳']+(['甜點店'] if idx!=40 else []),description='咖啡與甜點，適合午後休息或朋友聊天。')
 if idx in [3,4,6,51,60]:m['periods']=['晚餐']
 elif '早餐店' in m['types'] or '早午餐' in m['types']:m['periods']=['早餐','早午餐','午餐']
 elif any(t in m['types'] for t in ['飯類','麵店','義大利麵','壽司','拉麵','牛排','熱炒','火鍋','燒肉','鐵板燒']):m['periods']=['午餐','晚餐']+(['甜點／飲料'] if '咖啡廳' in m['types'] else [])
 else:m['periods']=['甜點／飲料']
 # Do not infer facilities for children from generic store positioning.
 m.update(childRating='普通',childBasis='資料不足，暫列普通，並非已確認適合兒童')
 if any(t in m['types'] for t in ['餐酒館','酒吧']):m['occasions']=['情侶約會','朋友聚餐','聊天聚會']
 elif any(t in m['types'] for t in ['燒肉','火鍋','熱炒']):m['occasions']=['朋友聚餐','家庭聚餐','多人聚餐']
 elif any(t in m['types'] for t in ['咖啡廳','甜點店','早午餐']):m['occasions']=['一人用餐','情侶約會','聊天聚會']
 else:m['occasions']=['一人用餐','朋友聚餐','快速用餐']
 if p.get('observedPriceRange'):
  match=re.search(r'\$([\d,]+)[–-]([\d,]+)',p['observedPriceRange'])
  if match:
   lo,hi=[int(v.replace(',','')) for v in match.groups()]
   if lo==1:
    lo=min(m['price'][0],hi);m['priceNote']=f'Google Maps 消費者回報區間為 NT${hi} 以下；下限 NT${lo} 為餐點類型的參考預算，非店家公布最低消費。'
   else:m['priceNote']='依 2026-10-05 Google Maps 消費者回報的人均區間，非店家固定套餐價；實際消費依點餐與當日菜單。'
   m['price']=[lo,hi]
 m['dishes']=p.get('dishes') or dishes.get(p['name'],{}).get('dishes',[])
 assert m['dishes'],p['name']
 for s in dishes.get(p['name'],{}).get('sources',[]):
  if not any(x['url']==s['url'] for x in m['sources']):m['sources'].append({'label':s.get('label') or s.get('title') or '推薦品項資料來源','url':s['url']})
 for u in p.get('dishSources',[]):m['sources'].append({'label':'推薦品項公開資料','url':u})
 m.update(id=f'expanded-next-{idx+1:03d}',area='板橋・新埔／府中及周邊')
 if idx==29:m['note']+='快餐車出攤位置與時間請先查看店家公告。'
 if idx==49:m['note']+='店名標示無內用。'
 if idx==50:m['note']+='甜點工作室的取貨與預約方式請先詢問。'
 if idx==37:m['note']+='店名標示營業時間請看 Instagram。'
 metadata[p['name']]=m;p.update(routeStatus='verified',status='selected-for-publication')
(ROOT/'expansion-next-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
(ROOT/'expansion-next-maps.json').write_text(json.dumps(shops[:58],ensure_ascii=False,indent=2)+'\n')
(ROOT/'expansion-next-new-maps.json').write_text(json.dumps(shops[58:],ensure_ascii=False,indent=2)+'\n')
print(f'Selected {len(metadata)} new stores; {len(shops)-len(metadata)} excluded or held.')
