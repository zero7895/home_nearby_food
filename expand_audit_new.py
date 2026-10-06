"""Generate the new audit batch without mutating Maps, routes or pipeline inputs.

Run only after the Maps/routing collection and identity decisions are complete.
Outputs dictionaries keyed by the observed canonical Maps name, plus a hold report.
"""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECKED_AT = '2026-10-05'

# Cuisine, type, meal context and short introduction reviewed for each candidate.
# Periods describe meal contexts, not a promise that the shop opens every day.
PROFILES = {
 0: ('台式','麵店,小吃','早餐,午餐,晚餐','餛飩麵、麻醬麵與湯品，適合日常用餐或外帶。',(60,150)),
 1: ('台式','小吃,飯類','午餐,晚餐','古早味油飯搭配肉羹與花枝羹，適合簡單用餐。',(40,160)),
 2: ('台式','小吃','午餐,晚餐','現炸臭豆腐搭配泡菜，適合外帶小吃。',(65,150)),
 3: ('台式','小吃','午餐,晚餐','肉圓與虱目魚丸湯，適合日常小吃或外帶。',(60,150)),
 4: ('不適用（咖啡／茶飲）','飲料店','甜點／飲料','珍珠奶茶與外帶茶飲，適合飯後順路帶一杯。',(40,100)),
 5: ('台式','甜點店,小吃','甜點／飲料','水果糖葫蘆，適合散步時外帶甜點。',(25,100)),
 6: ('台式','小吃','午餐,晚餐','甜不辣搭配醬料與熱湯，適合簡單吃一份小吃。',(60,150)),
 7: ('台式','小吃','午餐,晚餐','胡椒餅與小酥餅，適合外帶點心或簡單用餐。',(50,150)),
 8: ('中式','小吃','晚餐','現蒸小籠包，適合晚間用餐或外帶分享。',(130,250)),
 9: ('台式','甜點店','甜點／飲料','鮮奶麻糬搭配花生、芝麻或可可，適合外帶分享。',(60,180)),
 10: ('美式','早午餐,咖啡廳,甜點店','早餐,早午餐,午餐,晚餐,甜點／飲料','早午餐、咖啡與手作甜點，適合白天用餐或聊天。',(200,500)),
 11: ('日式','居酒屋,壽司,丼飯','午餐,晚餐','日式丼飯、壽司與串燒，適合用餐或朋友聚會。',(250,800)),
 12: ('韓式','飯類,小吃','午餐,晚餐','韓式炸雞、辣炒年糕與海鮮煎餅，適合朋友分食。',(200,500)),
 13: ('日式','咖啡廳,飯類','午餐,晚餐,甜點／飲料','咖哩飯、燒肉飯與飲品，適合喜歡貓咪的用餐者。',(300,500)),
 14: ('日式','飯類','午餐,晚餐','咖哩飯與配餐，適合在車站商場吃一份主餐。',(240,500)),
 15: ('不適用（咖啡／茶飲）','咖啡廳,甜點店','甜點／飲料','特色咖啡搭配巴斯克乳酪蛋糕，適合短暫休息。',(150,400)),
 16: ('其他異國料理','餐酒館','午餐,晚餐','精釀啤酒與異國共享餐點，適合朋友聚餐。',(500,1000)),
 17: ('台式','小吃','甜點／飲料','高麗菜煎餅，適合外帶鹹點心。',(40,150)),
 18: ('台式','小吃','晚餐,甜點／飲料','炸雞翅、腿排與薯條，適合外帶或朋友分享。',(60,250)),
 19: ('台式','小吃','午餐,晚餐','蚵嗲與炸蔬菜，適合外帶古早味小吃。',(50,180)),
 20: ('台式','麵店,小吃','早餐,午餐','大腸蚵仔麵線，適合早上或中午簡單用餐。',(50,150)),
 21: ('台式','麵店,小吃','早餐,午餐','米苔目與黑白切，適合早上或中午吃一碗熱湯麵。',(60,180)),
 22: ('台式','飯類,小吃','午餐,晚餐','手切滷肉飯與雞肉飯，適合日常用餐或外帶。',(60,180)),
 23: ('台式','甜點店','甜點／飲料','豆花與豆漿甜品，適合飯後甜點或外帶。',(45,130)),
 24: ('台式','甜點店','甜點／飲料','紅豆、奶油與芋頭車輪餅，適合外帶點心。',(25,120)),
 25: ('台式','麵店','晚餐','紅燒牛肉麵、水餃與乾麵，適合晚間日常用餐。',(100,250)),
 26: ('台式','麵店','午餐,晚餐','涼麵搭配味噌湯，適合日常用餐或外帶。',(60,180)),
 27: ('台式','小吃','甜點／飲料','蔥肉餅、蘿蔔絲餅與高麗菜餅，適合外帶鹹點心。',(25,120)),
 28: ('台式','小吃,麵店','晚餐','鵝肉切盤與鵝肉米粉，適合晚間用餐或分食。',(150,400)),
 29: ('台式','火鍋','晚餐','紅燒羊肉爐與羊肉配料，適合多人分享一鍋。',(250,600)),
 30: ('韓式','飯類,火鍋','午餐,晚餐','牛肉雪濃湯、韓式烤肉與湯鍋，適合午晚餐聚會。',(250,600)),
 31: ('其他異國料理','飯類','午餐,晚餐','夏威夷拌飯搭配蔬菜與配料，適合日常用餐或外帶。',(210,350)),
 32: ('台式','便當,飯類','午餐,晚餐','雞腿排、牛肉與松阪豬飯，適合午晚餐或外帶。',(170,300)),
 33: ('台式','甜點店','甜點／飲料','脆皮雞蛋糕與起司口味，適合外帶點心。',(50,150)),
 34: ('港式','小吃','午餐,晚餐','石磨腸粉搭配鮮蝦、牛肉或海鮮，適合簡單用餐。',(120,300)),
}

# Actual observed menu examples; these are reference dishes, not average spending.
MENU_REFERENCES = {
 0: '2026-01 食記列餛飩麵等品項約60–80元',
 1: '2026-01 食記列油飯40元、羹湯70–90元',
 2: '2026-01 食記列臭豆腐65–85元',
 3: '2026-01 食記列肉圓60元、虱目魚丸湯50元',
 4: '2026-01 食記列珍珠奶茶55元',
 5: '2026-01 食記列糖葫蘆25–40元',
 6: '2026-01 食記列甜不辣60–75元',
 7: '2026-01 食記列胡椒餅50元',
 8: '2026-01 食記列小籠包130元',
 31: '2025-07 同址食記列好身材POKE、泰式POKE各210元',
 32: '2025-07 同址食記列雞腿排、沙爹牛肉、松阪豬飯170／190／250元',
 34: '同址外送菜單列手剝鮮蝦腸粉189元；外送價可能與現場不同',
}


def read(filename):
    return json.loads((ROOT / filename).read_text())


def load_rules():
    """Reuse classifier functions/constants without its integration side effects."""
    tree = ast.parse((ROOT / 'classify_expansion.py').read_text())
    allowed = {'budgets', 'review_price_notes'}
    nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))
             or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in allowed for t in n.targets))]
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'classify_expansion.py', 'exec'), namespace)
    return namespace


def route_minutes(route):
    if not route or not route.get('url') or not route.get('options'):
        return None
    option = route['options'][0]
    if not isinstance(option, str) or not re.search(r'\d+(?:\.\d+)?\s*(?:公里|公尺)', option):
        return None
    hours = re.search(r'(\d+)\s*小時', option)
    minutes = re.search(r'(\d+)\s*分(?:鐘)?', option)
    if not hours and not minutes:
        return None
    return (int(hours[1]) * 60 if hours else 0) + (int(minutes[1]) if minutes else 0)


def sources_for(candidate, supplement):
    sources = [{'label': '同店公開餐點與店家資料', 'url': u} for u in candidate.get('sourceUrls', [])]
    for s in supplement.get('sources', []):
        sources.append({'label': s.get('kind') or s.get('label') or '同店菜單補查', 'url': s['url']})
    return list({s['url']: s for s in sources}.values())


def main():
    candidates = read('audit-new-candidates.json')
    shops = read('audit-new-maps.json')
    routes = read('audit-new-routes.json')
    supplements = {s['name']: s for s in read('audit-new-menu-supplement.json')}
    rules = load_rules()
    route_names = {(r.get('name'), r.get('mode')): r for r in routes}
    route_indices = {(int(r['index']), r.get('mode')): r for r in routes if r.get('index') is not None}
    metadata, dishes, excluded = {}, {}, []
    for original in shops:
        p = dict(original)
        idx = p.get('index')
        if not isinstance(idx, int) or idx not in PROFILES or idx >= len(candidates):
            excluded.append({'index': idx, 'name': p.get('name'), 'excludedReason': '候選 index 缺失或不在本批次'})
            continue
        c = candidates[idx]
        name = p.get('name', '')
        supplement = supplements.get(c['name'], {})
        def route(mode):
            return route_indices.get((idx, mode)) or route_names.get((name, mode)) or route_names.get((c['name'], mode))
        w, d = route('walking'), route('driving')
        wm, dm = route_minutes(w), route_minutes(d)
        reason = p.get('excludedReason')
        if not reason and p.get('closed'):
            reason = 'Maps 當前營業狀態為永久歇業或暫時關閉，暫不新增'
        if not reason and (p.get('pending') or not name or not p.get('address') or not (re.search(r'!1s[^!]+', p.get('url', '')) or (p.get('identityChecked') is True and p.get('addressChecked') is True and p.get('identityBasis')))):
            reason = 'Google Maps 店家身分、正式名稱或地址尚未確認'
        if not reason and (wm is None or dm is None):
            reason = '步行或開車路線尚未查證，需時間、距離與路線網址'
        if not reason and wm > 20 and dm > 15:
            reason = '超過步行20分鐘且開車15分鐘範圍'
        photos = {re.sub(r'=[ws]\d+.*$', '', u) for u in p.get('photos', []) if isinstance(u, str) and u.startswith('http')}
        if not reason and len(photos) < 5:
            reason = '尚未取得至少5張不同的店家照片'
        try:
            rating = float(str(p.get('rating') or '0').replace(',', '').replace('★', '').strip())
            reviews = int(re.sub(r'[^\d]', '', str(p.get('reviews') or '0')) or '0')
        except ValueError:
            rating, reviews = 0, 0
        if not reason and not (0 < rating <= 5 and reviews > 0):
            reason = 'Maps 評分或評論數尚未確認'
        recommended = list(dict.fromkeys(supplement.get('recommendedDishes') or c.get('recommendedDishes') or []))
        public_sources = sources_for(c, supplement)
        if not reason and (not recommended or not public_sources):
            reason = '同店推薦品項或公開來源尚未確認'
        if not reason and name in metadata:
            reason = 'Maps 正式名稱與本批次已納入店家重複，需人工裁決'
        if reason:
            excluded.append({'index': idx, 'name': name, 'candidateName': c['name'], 'excludedReason': reason})
            continue
        p.update(text=p.get('text') or '', rating=str(rating), reviews=str(reviews))
        m = rules['enrich'](p, rules['classify'](p))
        cuisine, types, periods, description, budget = PROFILES[idx]
        m.update(cuisines=cuisine.split(','), types=types.split(','), periods=periods.split(','), description=description,
                 childRating='普通', childBasis='資料不足，暫列普通，並非已確認適合兒童',
                 price=list(budget), dishes=recommended, id=f'expanded-audit-{idx+1:03d}', area='板橋・新埔／江子翠／府中及周邊')
        if any(t in m['types'] for t in ['餐酒館','居酒屋']):
            m['occasions'] = ['情侶約會','朋友聚餐','聊天聚會']
        elif '火鍋' in m['types']:
            m['occasions'] = ['朋友聚餐','家庭聚餐','多人聚餐']
        elif any(t in m['types'] for t in ['咖啡廳','甜點店','早午餐']):
            m['occasions'] = ['一人用餐','情侶約會','聊天聚會']
        else:
            m['occasions'] = ['一人用餐','快速用餐']
        lo, hi = budget
        m['priceNote'] = f'依店型與同店公開餐點資訊規劃每人 NT${lo}–{hi}；屬規劃推估，非已查證售價或店家平均消費。'
        m['priceBasis'] = 'planning-estimate'
        if idx in MENU_REFERENCES:
            m['priceNote'] = f'{MENU_REFERENCES[idx]}；依不同點餐規劃每人 NT${lo}–{hi}。參考菜單日期可能較舊，非店家統計平均消費。'
            m['priceBasis'] = 'menu-reference-estimate'
        observed = p.get('observedPriceRange') or ''
        match = re.search(r'(?:NT\s*)?\$?\s*([\d,]+)\s*[–－—-]\s*\$?\s*([\d,]+)', observed)
        if match:
            low, high = [int(v.replace(',', '')) for v in match.groups()]
            if 0 < low <= high:
                if low == 1:
                    low = min(lo, high)
                    m['priceNote'] = f'Google Maps 消費者回報區間為 NT${high} 以下；下限 NT${low} 為同店餐點與店型的參考預算，非已查證最低消費。'
                else:
                    m['priceNote'] = f'依 {CHECKED_AT} Google Maps 消費者回報的人均區間；非店家固定套餐價，實際消費依點餐與當日菜單。'
                m.update(price=[low, high], priceBasis='maps-reported-range', observedPriceRange=observed)
        m['sources'] = [{'label': 'Google Maps｜店家名稱、地址、評分與照片', 'url': p['url']}] + public_sources
        for r, label in [(w, 'Google Maps｜實際步行路線'), (d, 'Google Maps｜實際開車路線')]:
            m['sources'].append({'label': label, 'url': r['url']})
        m['classificationBasis'] = '料理、型態與餐廳簡介依同店公開菜單及 Maps 店家資料整理；時段是用餐情境，兒童設施未確認。'
        m['shortName'] = {13:'貓爪爪貓咪咖啡廳',23:'天天豆花',25:'莒光路27巷牛肉麵',29:'MR.羊 羊肉爐'}.get(idx,m['shortName'])
        m['candidateIndex'] = idx
        m['candidateName'] = c['name']
        m['routeEvidence'] = {'walking': w, 'driving': d}
        if idx == 13:
            m['note'] += '兒童入店與訂位規定請先詢問店家。'
        if idx == 27:
            m['note'] += '攤位出攤位置與售完時間請先確認。'
        metadata[name] = m
        dishes[name] = {'dishes': recommended, 'sources': [{'title': s['label'], 'url': s['url']} for s in public_sources],
                        'evidence': '推薦品項依同址公開菜單或實食資料整理；店家當日供應為準。',
                        'checkedAt': CHECKED_AT, 'scope': '同店公開餐點資料；非 Google 評論統計排名',
                        'candidateIndex': idx, 'candidateName': c['name']}
    for filename, data in [('audit-new-metadata.json', metadata), ('audit-new-dishes.json', dishes), ('audit-new-excluded.json', excluded)]:
        (ROOT / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(f'Selected {len(metadata)}; held {len(excluded)}. Original Maps and route inputs preserved.')


if __name__ == '__main__':
    main()
