"""Convert locally recorded Maps observations and researched metadata into static data.js."""
import json, re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SOURCE = lambda label, url: {'label': label, 'url': url}
META = {
 '禾冬咖啡 Hedong cafe': dict(id='hedong',shortName='禾冬咖啡',area='民生路巷弄',address='新北市板橋區民生路二段234巷24弄6號',rating=4.7,reviewCount=132,price=[270,450],description='早午餐、義大利麵與燉飯，一個巷弄裡的日常休息站。',dishes=['剝皮辣椒鹹豬肉義大利麵','雞腿早午餐','拿鐵'],cuisines=['義式','美式'],types=['早午餐','咖啡廳','義大利麵'],periods=['早餐','早午餐','午餐','下午茶','晚餐'],occasions=['一人用餐','情侶約會','朋友聚餐','聊天聚會'],priceNote='每人主餐或餐盤加飲品估 NT$270–450。2025 食記主餐約270元；目前外送義大利麵335元起，內用價格待現場確認。',note='寵物友善；店家公告週一公休。甜點與季節活動依當日供應。',childRating='未查證',sources=[SOURCE('店家社群轉載｜地址、空間與公休日','https://www.findglocal.com/TW/Xinbei/479981408521397/禾冬咖啡Hedong-cafe'),SOURCE('Fooday｜2025/02/15 到訪餐點價格','https://fooday.app/zh-TW/reviews/8ssaixYS6udAjVyDNVgJMm'),SOURCE('Uber Eats｜外送菜單（價格可能高於內用）','https://www.ubereats.com/tw/store/禾冬咖啡-hedong-cafe-丨-義大利麵-燉飯/oWt3L1jcWfyq7PXkvSQkKA')]),
 '食時在在民生店': dict(id='always',area='民生路二段',price=[60,180],description='熱壓吐司、漢堡與早餐套餐，適合簡單吃一餐。',dishes=['熱壓吐司','漢堡','卡啦捲餅'],cuisines=['台式','美式'],types=['早餐店','早午餐'],periods=['早餐','早午餐','午餐'],occasions=['一人用餐','快速用餐'],priceNote='早餐單點或套餐估 NT$60–180；2025/12 食記提到套餐約百元，實際依菜單。',note='公開食記：平日07:00–13:00，週末至14:00，週二公休；出門前看 Maps 最新公告。',sources=[SOURCE('PEKO｜2025/12 早餐食記、營業時段與價格','https://pekoblog.tw/post-48339596/')]),
 'Good Day Project 好菇計畫商行': dict(id='goodday',shortName='好菇計畫商行',area='民生路巷弄',price=[200,400],description='以菇類與時蔬做主角，從早午餐盤吃到手工義大利麵。',dishes=['菇 Day 早午餐','義式鮮蝦煙花女','三明治'],cuisines=['義式','美式'],types=['早午餐','咖啡廳','義大利麵'],periods=['早午餐','午餐','下午茶'],occasions=['一人用餐','情侶約會','朋友聚餐'],priceNote='依2025/04食記：菇Day 290元、義式鮮蝦煙花女330元，主餐附紅茶；依點餐方式估 NT$200–400。',note='Maps 名稱為好菇計畫商行。食記提到座位約14席、低消100元，熱門時段需候位。',sources=[SOURCE('Mii’s 漫行繪旅｜2025/04 菜單、座位與低消','https://minimiigo.com/good-day-project/')]),
 'ハーフ珈琲（Hafu coffee roaster)': dict(id='hafu',shortName='ハーフ珈琲 Hafu',area='莒光路巷弄',price=[150,350],description='巷子裡的咖啡與每日甜點，適合找個午後慢慢坐。',dishes=['咖啡','肉桂捲','布丁','每日蛋糕'],cuisines=['不適用（咖啡／茶飲）'],types=['咖啡廳','甜點店'],periods=['下午茶','甜點／飲料'],occasions=['一人用餐','情侶約會','聊天聚會'],priceNote='2025食記咖啡、甜點多為100多元；單杯或飲品加甜點估 NT$150–350，每日甜點價格可能不同。',note='店內有貓，入內依門鈴／店員引導。以咖啡甜點為主；兒童設備未查證。',sources=[SOURCE('WalkerLand｜2025/03 咖啡、甜點價位與空間','https://www.walkerland.com.tw/article/view/408012')]),
 '阿達師牛肉麵': dict(id='ada',area='莒光路',price=[150,250],description='紅燒牛肉麵、水餃與小菜，晚一點也能吃到熱騰騰的一餐。',dishes=['紅燒牛肉麵','香菇醡醬麵','水餃'],cuisines=['台式','中式'],types=['麵店','小吃'],periods=['午餐','晚餐','宵夜'],occasions=['一人用餐','快速用餐','朋友聚餐'],priceNote='依2026/03食記與麵食、小菜組合，估 NT$150–250；此為規劃預算，非精確店家平均。',note='食記時段11:30–14:00、17:00–24:00；週日至23:00。午晚餐尖峰可能排隊。',sources=[SOURCE('PEKO｜2026/03 菜單與宵夜時段','https://pekoblog.tw/adashi/'),SOURCE('Nash｜2026/05 最新到訪食記','https://nash.tw/letsgoadabeefnoodle2026/')]),
 '原味廣東粥': dict(id='porridge',area='莒光路',price=[80,130],description='現點現煮的廣東粥，外帶一碗當晚餐或暖胃宵夜。',dishes=['廣東粥','海鮮粥','豬肝粥'],cuisines=['港式','台式'],types=['小吃'],periods=['午餐','晚餐','宵夜'],occasions=['一人用餐','快速用餐'],priceNote='粥品單碗加油條預留 NT$80–130；公開資料為銅板價定位，精確最新售價待現場確認。',note='食記指出僅外帶、無內用座位；Maps查閱當日顯示22:30打烊，與舊食記23:00不同，以現場為準。',childRating='不太適合',sources=[SOURCE('PEKO｜2025/10 粥品菜單、僅外帶','https://pekoblog.tw/post-41758567/')]),
 '瓢記PIAO JI': dict(id='piao',shortName='瓢記 PIAO JI',area='莒光路巷弄',price=[400,800],description='台味小吃配創意調酒，適合下班後和朋友聚一聚。',dishes=['野格牛肉麵','手切滷肉飯','脆皮燒肉'],cuisines=['台式'],types=['餐酒館','酒吧','麵店','飯類'],periods=['晚餐','宵夜'],occasions=['情侶約會','朋友聚餐','多人聚餐','聊天聚會'],priceNote='FunNow人均參考500元；食記野格牛肉麵230元、調酒300–350元，餐點加飲品估 NT$400–800。',note='公開食記提到每人低消一杯飲料，餐酒館營業到凌晨，包廂與多人座位應先詢問。',childRating='不太適合',sources=[SOURCE('FunNow｜店家資訊、人均500元','https://www.myfunnow.com/zh-tw/branches/3385522445807'),SOURCE('有點想分享｜2025/04 餐點價格與低消','https://weshares.com.tw/newtaipei-piaoji/')]),
 '得正#板橋莒光計劃': dict(id='dejeng',shortName='得正・板橋莒光計劃',area='莒光路',price=[40,90],description='春烏龍、焙烏龍與奶蓋茶，飯後順路帶一杯。',dishes=['春烏龍','焙烏龍鮮奶','芝士奶蓋春烏龍'],cuisines=['台式'],types=['飲料店'],periods=['下午茶','甜點／飲料'],occasions=['快速用餐'],priceNote='以目前Uber Eats單杯價格參考：原茶40元、奶蓋60元、焙烏龍鮮奶65元；外送價，門市可能不同。',note='Google評分3.3，與外送平台4.9不同；本站只顯示此次查閱的Google評分。',sources=[SOURCE('Uber Eats｜本分店單杯外送價格','https://www.ubereats.com/tw/store/得正-oolong-tea-project-板橋莒光計劃/fFEAhR2hUUC4Bzuz5OfhpA')]),
 '鶴茶樓- 鶴頂紅茶商店(板橋新埔店)': dict(id='hechalou',shortName='鶴茶樓・板橋新埔店',area='民生路三段',price=[35,100],description='紅茶、鮮奶茶與特色凍飲，換個口感的手搖選擇。',dishes=['鶴頂紅茶','烏瓦那堤','特色凍飲'],cuisines=['台式'],types=['飲料店'],periods=['下午茶','甜點／飲料'],occasions=['快速用餐'],priceNote='依品牌公開菜單介紹與單杯飲品定位，預留 NT$35–100；新上市飲品、加料與尺寸可能超出。',note='官方門市資料核對為民生路三段11號；限定飲品依門市公告。',sources=[SOURCE('鶴茶樓官方｜新埔店地址、電話','https://hechaloutea.com.tw/shops/'),SOURCE('BALIMAN｜2026品牌菜單價位','https://baliman.tw/blog/post/hechalou-menu')]),
 '果汁媽粉條爸': dict(id='fruit',area='民生路二段',price=[50,150],description='當季水果甜點與蛋糕盒，買一份把下午茶帶回家。',dishes=['水果三明治','季節水果蛋糕盒','芋泥布丁蛋糕'],cuisines=['台式'],types=['甜點店','飲料店'],periods=['下午茶','甜點／飲料'],occasions=['快速用餐'],priceNote='單人小份甜點預留 NT$50–150；2024食記三明治45元、奶酪65元、菠蘿75元，整盒蛋糕約330元，不能當成單人均消。',note='草莓甜點有季節性，10月不保證有草莓品項；Maps顯示週一14:00開始營業，舊文章時間不同，先看公告。',sources=[SOURCE('TISS｜2024/11 甜點單份與整盒價格','https://tisshuang.com/blog/post/juicemom88'),SOURCE('PEKO｜草莓季節與外帶甜點','https://ifoodie.tw/post/5e7f5093cb7a1c584c7041ca')]),
 '雙月食品社 板橋店': dict(id='moon',shortName='雙月食品社・板橋店',area='文化路一段巷弄',price=[200,400],description='雞湯、拌麵與滷味，想喝湯時的一餐台式選擇。',dishes=['剝皮辣椒雞湯','蛤蜊雞湯','乾拌麵'],cuisines=['台式'],types=['小吃','麵店','飯類'],periods=['午餐','晚餐'],occasions=['一人用餐','家庭聚餐','帶小孩','長輩聚餐'],priceNote='Google資料轉載價帶200–400元；目前外送雞湯約280元、套餐298元，餐點搭配不同會影響總額。',note='午晚餐分段營業；尖峰常需候位。官方LINE舊資訊與目前inline訂位頁不同，請以當日分店為準。',childRating='適合',sources=[SOURCE('雙月官方｜板橋店點餐菜單','https://order.quickclick.cc/tw/food/P_mpGjEZqRA/'),SOURCE('Uber Eats｜雞湯與套餐外送價格','https://www.ubereats.com/store/雙月食品社-板橋店/brY8_Uz8USOFJxyyBnYd1Q'),SOURCE('Chew Map｜價位、家庭用餐與兒童高腳椅記載','https://chewmap.com/restaurants/restaurant-15252-71c407ee')]),
 '北城脆皮烤鴨 板橋新埔店': dict(id='duck',shortName='北城脆皮烤鴨・新埔店',area='民生路二段',price=[200,350],description='一鴨兩吃，片鴨夾餅和炒鴨架，外帶回家一起吃。',dishes=['片鴨夾餅','炒鴨架','一鴨兩吃'],cuisines=['中式'],types=['小吃'],periods=['午餐','晚餐'],occasions=['家庭聚餐','多人聚餐'],priceNote='目前外送半隻660元、全隻1220元；以半隻2–3人或全隻4–6人分享，估每人200–350元。門市較外送優惠，需電話確認。',note='目前地址是民生路二段169號，舊文部分仍寫228號。人均為多人分攤，單獨購買半隻金額不同。',sources=[SOURCE('Uber Eats｜目前半隻／全隻外送價格與地址','https://www.ubereats.com/tw/store/北城脆皮烤鴨-新埔店/mY8ssOR8UK-4KUY0J4v34g')]),
 '英記快餐': dict(id='ying',shortName='英記燒臘快餐',area='莒光路',price=[115,180],description='燒鴨、叉燒與油雞便當，想吃港式燒臘就順路帶一盒。',dishes=['英記招牌飯','叉燒香腸飯','燒鴨飯'],cuisines=['港式'],types=['便當','飯類','小吃'],periods=['午餐','晚餐'],occasions=['一人用餐','快速用餐'],priceNote='2024/05食記招牌飯與雙拼115元；考量加肉及價格變動，預留 NT$115–180，最新門市價未查證。',note='公開食記寫週六公休；本清單使用Google最新名稱「英記快餐」核對地址。',sources=[SOURCE('Cheer｜2024/05 菜單、地址與雙拼價格','https://cheer198.pixnet.net/blog/posts/2036620741')]),
 'THE·春 板橋店': dict(id='spring',area='莒光路巷弄',price=[220,600],description='日式丼飯、生魚片與握壽司，小資到海鮮都能選。',dishes=['蔥燒牛肉丼','小資海鮮丼','握壽司'],cuisines=['日式'],types=['丼飯','壽司'],periods=['午餐','晚餐'],occasions=['一人用餐','情侶約會','朋友聚餐','家庭聚餐'],priceNote='以單人丼飯加小菜估 NT$220–600；外送蔥燒牛肉丼220元、小資海鮮丼290元，珠寶盒等高價品可到980元。',note='午晚餐分段營業；菜單同時有生食與熟食。高價海鮮品項可超過本頁日常預算區間。',sources=[SOURCE('Uber Eats｜本店日式丼飯外送價格','https://www.ubereats.com/tw-en/store/the春-日式料理-板橋店/n4If2lPQQ7SyLU3gjjUalw'),SOURCE('Jeremy｜日式餐點、吧台與空間介紹','https://jeremyfoodie.tw/the-spring-banqiao/')]),
}

TAXONOMY = {
 'cuisines':['台式','中式','港式','日式','韓式','泰式','越式','新馬料理','印度料理','義式','法式','西班牙料理','美式','墨西哥料理','中東料理','其他異國料理','不適用（咖啡／茶飲）'],
 'types':['早餐店','早午餐','咖啡廳','甜點店','飲料店','小吃','麵店','飯類','便當','熱炒','火鍋','燒肉','鐵板燒','居酒屋','拉麵','壽司','丼飯','飲茶','牛排','義大利麵','披薩','Buffet','吃到飽','餐酒館','酒吧','速食','素食／蔬食'],
 'periods':['早餐','早午餐','午餐','晚餐','甜點／飲料'],
 'occasions':['一人用餐','情侶約會','朋友聚餐','家庭聚餐','帶小孩','長輩聚餐','慶生','商務聚餐','多人聚餐','聊天聚會','快速用餐'],
 'childRatings':['適合','普通','不適合'],
 'priceBands':[{'label':'NT$200 以下','min':0,'max':200},{'label':'NT$201–400','min':201,'max':400},{'label':'NT$401–600','min':401,'max':600},{'label':'NT$601–1,000','min':601,'max':1000},{'label':'NT$1,001–1,500','min':1001,'max':1500},{'label':'NT$1,501–2,000','min':1501,'max':2000},{'label':'NT$2,001 以上','min':2001,'max':999999}],
}

METADATA_FILES = [
    'expanded-metadata.json', 'expansion-200-metadata.json',
    'expansion-500-metadata.json', 'expansion-more-metadata.json',
    'expansion-next-metadata.json', 'audit-new-metadata.json',
]

def load_optional_json(filename, default):
    path = ROOT / filename
    return json.loads(path.read_text()) if path.exists() else default

def maps_place_identity(url):
    match = re.search(r'!1s(0x[0-9a-f]+:0x[0-9a-f]+)', url)
    return match.group(1) if match else None

METADATA_FILES += [p.name for p in sorted(ROOT.glob('weekly-*-metadata.json'))]

def expected_place_count():
    """Every approved metadata entry must produce one active, unique place."""
    approved = dict(META)
    for filename in METADATA_FILES:
        approved.update(load_optional_json(filename, {}))
    audited_exclusions = {
        row['name'] for row in load_optional_json('audit-2026-10-05-corrections.json', [])
        if row.get('action') == 'exclude'
    }
    return len(set(approved) - audited_exclusions)

def build():
    observed = json.loads((ROOT/'maps-research.json').read_text()) + json.loads((ROOT/'expanded-maps-research.json').read_text()) + json.loads((ROOT/'expansion-200-maps.json').read_text()) + json.loads((ROOT/'expansion-500-maps.json').read_text())
    META.update(json.loads((ROOT/'expanded-metadata.json').read_text()))
    META.update(json.loads((ROOT/'expansion-200-metadata.json').read_text()))
    META.update(json.loads((ROOT/'expansion-500-metadata.json').read_text()))
    more_metadata = json.loads((ROOT/'expansion-more-metadata.json').read_text())
    META.update(more_metadata)
    observed += json.loads((ROOT/'expansion-more-maps.json').read_text())
    next_metadata = json.loads((ROOT/'expansion-next-metadata.json').read_text())
    META.update(next_metadata)
    next_observed = json.loads((ROOT/'expansion-next-maps.json').read_text()) + json.loads((ROOT/'expansion-next-new-maps.json').read_text())
    next_names = {obs['name'] for obs in next_observed}
    observed = [obs for obs in observed if obs['name'] not in next_names] + next_observed
    audit_new_metadata = load_optional_json('audit-new-metadata.json', {})
    META.update(audit_new_metadata)
    audit_new_observed = load_optional_json('audit-new-maps.json', [])
    audit_new_names = {obs['name'] for obs in audit_new_observed}
    observed = [obs for obs in observed if obs['name'] not in audit_new_names] + audit_new_observed
    for file in sorted(ROOT.glob('weekly-*-metadata.json')):
        META.update(json.loads(file.read_text()))
    for file in sorted(ROOT.glob('weekly-*-maps.json')):
        updates = json.loads(file.read_text())
        updated_names = {obs['name'] for obs in updates}
        observed = [obs for obs in observed if obs['name'] not in updated_names] + updates
    expanded_routes = json.loads((ROOT/'expanded-routes-research.json').read_text()) + json.loads((ROOT/'expansion-200-routes.json').read_text()) + json.loads((ROOT/'expansion-500-routes.json').read_text())
    expanded_routes += json.loads((ROOT/'expansion-more-routes.json').read_text())
    expanded_routes += json.loads((ROOT/'expansion-next-routes.json').read_text())
    expanded_routes += load_optional_json('audit-new-routes.json', [])
    for file in sorted(ROOT.glob('weekly-*-routes.json')):
        expanded_routes += json.loads(file.read_text())
    weekly_live = {}
    for file in sorted(ROOT.glob('weekly-*-live.json')):
        weekly_live.update({r['name']: r for r in json.loads(file.read_text())})
    drives = {r['name']:r for r in expanded_routes if r['mode']=='driving'}
    routes = {r['name']:r for r in json.loads((ROOT/'routes-research.json').read_text())}
    routes.update({r['name']:r for r in expanded_routes if r['mode']=='walking'})
    corrections = json.loads((ROOT/'reviewed-corrections.json').read_text())
    dish_research = json.loads((ROOT/'recommended-dishes-research.json').read_text())
    dish_research.update(json.loads((ROOT/'expansion-next-dishes.json').read_text()))
    dish_research.update(load_optional_json('audit-new-dishes.json', {}))
    audit_corrections = {row['name']: row for row in load_optional_json('audit-2026-10-05-corrections.json', [])}
    live_ratings = {row['name']: row for row in load_optional_json('audit-live-maps.json', [])}
    places, excluded = [], []
    for obs in observed:
        audit = audit_corrections.get(obs['name'], {})
        if audit.get('action') == 'exclude':
            excluded.append({'name':obs['name'], 'mapUrl':obs['url'], 'reason':audit['patch']['excludedReason'], 'checkedAt':'2026-10-05'})
            continue
        if obs.get('excludedReason'):
            excluded.append({'name':obs['name'], 'mapUrl':obs['url'], 'reason':obs['excludedReason'], 'checkedAt':obs.get('checkedAt','2026-10-04')})
            continue
        if obs.get('closed'):
            excluded.append({'name':obs['name'], 'mapUrl':obs['url'], 'reason':'Google Maps 標示永久歇業', 'checkedAt':obs.get('checkedAt','2026-10-04')})
            continue
        if obs['name'] not in routes:
            excluded.append({'name':obs['name'], 'mapUrl':obs['url'], 'reason':'交通路線資料待複查，暫不收錄', 'checkedAt':obs.get('checkedAt','2026-10-04')})
            continue
        walk = int(re.search(r'(\d+) 分',routes[obs['name']]['options'][0]).group(1))
        drive = int(re.search(r'(\d+) 分',drives[obs['name']]['options'][0]).group(1)) if obs['name'] in drives else None
        if walk > 20 and (drive is None or drive > 15):
            excluded.append({'name':obs['name'], 'mapUrl':obs['url'], 'reason':'超過步行20分鐘且開車15分鐘範圍', 'checkedAt':obs.get('checkedAt','2026-10-04')})
            continue
        if obs['name'] not in META:
            excluded.append({'name':obs['name'], 'mapUrl':obs['url'], 'reason':'店家分類、預算與餐點資料尚未核實，暫不收錄', 'checkedAt':obs.get('checkedAt','2026-10-04')})
            continue
        p = dict(META[obs['name']])
        p.update(corrections.get(obs['name'], {}))
        if obs['name'] in dish_research:
            recommendation = dish_research[obs['name']]
            assert recommendation['dishes'] and recommendation['sources'], obs['name']
            assert all(isinstance(dish, str) and dish.strip() for dish in recommendation['dishes'])
            p['dishes'] = list(dict.fromkeys(recommendation['dishes']))
            sources = list(p.get('sources', []))
            for source in recommendation['sources']:
                if not any(existing['url'] == source['url'] for existing in sources):
                    sources.append(source)
            p['sources'] = sources
        # Apply researched fixes before generating tags, price bands and other UI fields.
        p.update(audit.get('patch', {}))
        if audit:
            sources = list(p.get('sources', []))
            for source in audit.get('sources', []):
                if not any(existing['url'] == source['url'] for existing in sources):
                    sources.append(source)
            p['sources'] = sources
        p['name'] = obs['name']
        p.setdefault('address',obs.get('address','').replace('地址: ','').strip())
        p['address'] = re.sub(r'^\d{3,6}(?=[^\d])','',p['address'])
        p['mapUrl'] = obs['url']
        p.setdefault('rating',float(obs.get('rating','0').split()[0]))
        p.setdefault('reviewCount',int(re.sub(r'\D','',obs.get('reviews','0'))))
        live_rating = live_ratings.get(obs['name'])
        if live_rating:
            identity = maps_place_identity(obs['url'])
            assert identity and identity == maps_place_identity(live_rating['mapUrl']), (obs['name'], 'Live rating source has a different Google Maps place identity')
            rating = float(live_rating['rating'])
            review_count = int(live_rating['reviewCount'])
            assert 0 < rating <= 5 and review_count >= 0, obs['name']
            p['rating'] = rating
            p['reviewCount'] = review_count
            p['ratingCheckedAt'] = live_rating['checkedAt']
        weekly = weekly_live.get(p['name'])
        if weekly:
            assert weekly['mapUrl'] == p['mapUrl'] and weekly['address'] == p['address'], 'Weekly observation must match saved shop identity and address'
            assert 0 < weekly['rating'] <= 5 and isinstance(weekly['reviewCount'], int) and weekly['reviewCount'] >= 0
            p['rating'] = weekly['rating']
            p['reviewCount'] = weekly['reviewCount']
            p['ratingCheckedAt'] = weekly['checkedAt']
            p['businessCheckedAt'] = weekly['checkedAt']
            p['businessStatus'] = weekly['businessStatus']
        photo_ids = set()
        p['photos'] = []
        for url in obs['photos']:
            url = re.sub(r'^url\("?|"?\)$','',url)
            identity = url.split('=')[0]
            if identity not in photo_ids:
                photo_ids.add(identity)
                p['photos'].append(url)
        p['photos'] = p['photos'][:5]
        p['photoSource'] = 'Google Maps 店家頁面；權利屬原攝影者'
        route = routes[obs['name']]
        route_text = route['options'][0]
        minutes = re.search(r'(\d+) 分',route_text)
        distance = re.search(r'([\d.]+ (?:公尺|公里))',route_text)
        p['walkMinutes'] = int(minutes.group(1))
        p['walkDistance'] = distance.group(1)
        p['routeVia'] = next((s for s in route_text.splitlines() if s.startswith('途經')),'Google 建議步行路線')
        p['routeUrl'] = route['url']
        p['driveMinutes'] = drive
        p['driveDistance'] = re.search(r'([\d.]+ (?:公尺|公里))',drives[obs['name']]['options'][0]).group(1) if drive is not None else '未查證'
        p['driveRouteUrl'] = drives[obs['name']]['url'] if drive is not None else 'https://www.google.com/maps/dir/?api=1&destination='+quote(p['name']+' '+p['address'])+'&travelmode=driving'
        p['driveVia'] = next((s for s in drives[obs['name']]['options'][0].splitlines() if s.startswith('途經')),'Google 建議開車路線') if drive is not None else '未查證，請自行規劃路線'
        p['walkBand'] = '0-5' if walk <= 5 else '5-10' if walk <= 10 else '10-20' if walk <= 20 else None
        assert walk <= 20 or (drive is not None and drive <= 15)
        # Retain the researched meal periods and shop types without the removed categories.
        old_periods = p['periods']
        p['periods'] = [v for v in old_periods if v not in ['下午茶','宵夜']]
        if '宵夜' in old_periods and not p['periods']:
            p['periods'] = ['晚餐']
        elif not p['periods']:
            p['periods'] = ['甜點／飲料']
        p['tags'] = p['periods'] + [t for t in ['咖啡廳','飲料'] if (t=='咖啡廳' and t in p['types']) or (t=='飲料' and '飲料店' in p['types'])] + ['台菜' if c=='台式' else c for c in p['cuisines'] if c in ['港式','日式'] or (c=='台式' and any(t in p['types'] for t in ['小吃','麵店','飯類','餐酒館','熱炒']))]
        original_rating = p.get('childRating', '未查證')
        p['childRating'] = {'很適合':'適合', '不太適合':'不適合', '未查證':'普通'}.get(original_rating, original_rating)
        p.setdefault('childBasis','資料不足，暫列普通，並非已確認適合兒童' if original_rating == '未查證' else '公開資料＋情境推估')
        for field in ['childNote', 'highchair', 'spacious']:
            p.pop(field, None)
        assert p['childRating'] in TAXONOMY['childRatings']
        p['priceBands'] = [band['label'] for band in TAXONOMY['priceBands'] if p['price'][0] <= band['max'] and p['price'][1] >= band['min']]
        p.setdefault('classificationBasis','依公開菜單與店家定位整理；適合場合為情境推估，未保證兒童或包廂設備。')
        p['checkedAt'] = obs.get('checkedAt', '2026-10-04')
        assert len(p['photos']) == 5 and len(set(p['photos'])) == 5, p['name']
        for field in ['cuisines','types','periods','occasions']:
            assert all(v in TAXONOMY[field] for v in p[field]), (p['name'],field)
        places.append(p)
    assert len({p['name'] for p in places}) == len(places)
    identities = [re.search(r'!1s(0x[^!]+)',p['mapUrl']).group(1) if re.search(r'!1s(0x[^!]+)',p['mapUrl']) else p['name'] for p in places]
    assert len(set(identities)) == len(places), 'Duplicate Google Maps place identity'
    assert len(places) == expected_place_count(), 'Approved metadata entries must all pass observation and route gates'
    assert len({p['id'] for p in places}) == len(places)
    result = {'checkedAt':max(p['checkedAt'] for p in places),'home':{'label':'板橋區民生路二段240巷68號','mapUrl':json.loads((ROOT/'home-map.json').read_text())['url']},'places':places,'excluded':excluded,'taxonomy':TAXONOMY}
    (ROOT/'data.js').write_text('window.NEARBY_DATA = '+json.dumps(result,ensure_ascii=False,indent=2)+';\n')
    (ROOT/'restaurants.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f'Built {len(places)} active places, {sum(len(p["photos"]) for p in places)} photos; excluded {len(excluded)} candidates.')

if __name__ == '__main__':
    build()
