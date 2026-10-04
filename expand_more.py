"""Build metadata only for additional shops with complete, observed Maps routes."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
shops=json.loads((ROOT/'expansion-more-maps.json').read_text())
routes=json.loads((ROOT/'expansion-more-routes.json').read_text())
# Reuse the established classification definitions, stopping before its 500-shop batch job.
rules={}
source=(ROOT/'classify_expansion.py').read_text()
exec(source[:source.index('route_lookup=')],rules)
lookup={(r['name'],r['mode']):r for r in routes}
metadata={}
for p in shops:
    w=lookup.get((p['name'],'walking'));d=lookup.get((p['name'],'driving'))
    if not w or not d:continue
    wm=int(re.search(r'(\d+) 分',w['options'][0]).group(1));dm=int(re.search(r'(\d+) 分',d['options'][0]).group(1))
    if p.get('closed') or not p.get('rating') or len({u.split('=')[0] for u in p['photos']})<5 or (wm>20 and dm>15):continue
    m=rules['enrich'](p,rules['classify'](p));n=p['name'];text=p['text']
    def set_food(c,t,price,description,periods=None):
        m.update(cuisines=c,types=t,price=price,description=description)
        if periods:m['periods']=periods
    if n=='埔墘小吃':set_food(['台式'],['小吃','飯類','麵店'],[70,200],'滷肉飯、便當與藥燉排骨湯，適合日常用餐。')
    if n=='豆干爸ㄟ臭豆腐':
        set_food(['台式'],['小吃'],[60,180],'現炸臭豆腐搭配泡菜的外帶小吃。',['晚餐'])
        m['note']+='公開評論提到巡迴攤車，前往前請先確認當日出攤位置。'
    if '雞肉飯' in n or '冬瓜肉飯' in n:set_food(['台式'],['飯類','小吃'],[70,200],'飯類主餐與小吃，適合日常午晚餐或外帶。')
    if n=='良師塾人文食飲':set_food(['義式','台式'],['咖啡廳','義大利麵','麵店'],[250,600],'咖啡、義大利麵與牛肉麵，適合用餐或聊天。',['午餐','晚餐','甜點／飲料'])
    if n=='品鼎殿日式壽喜燒':set_food(['日式'],['火鍋','吃到飽'],[600,1100],'日式壽喜燒吃到飽，方案與服務費依當日菜單。',['午餐','晚餐'])
    if n=='夏廚食光餐廳':set_food(['義式'],['義大利麵','牛排'],[300,750],'義大利麵、燉飯與牛排，適合午晚餐聚會。')
    if n=='森林敘事 La Foresta by Narrative':set_food(['義式'],['義大利麵','餐酒館'],[500,1200],'義大利麵、燉飯與葡萄酒，適合約會或聚餐。')
    if n=='首屋':set_food(['台式'],['小吃','麵店'],[250,650],'何首烏雞湯、麵線與小菜，適合暖胃的一餐。')
    if n=='慶祥樓北方館':m['cuisines']=['中式'];m['price']=[400,1000]
    if n=='國光小館/板橋美食':set_food(['中式'],['熱炒'],[300,800],'川菜與共享料理，適合多人分食。')
    if '漢堡' in n:set_food(['美式'],['速食'] if '角落' in n else ['早午餐'],[150,450],'漢堡與美式輕食，依當日菜單搭配主餐。',['午餐','晚餐'])
    if n=='蓋子美式餐廳':set_food(['美式','義式'],['義大利麵','披薩','早午餐'],[300,700],'漢堡、義大利麵與燉飯，適合朋友聚餐。',['午餐','晚餐'])
    if n.startswith('月餐酒館'):set_food(['義式'],['餐酒館','義大利麵'],[450,1000],'燉飯、義大利麵與酒飲，適合晚間聚餐。',['晚餐'])
    if n.startswith('來吧sunset'):set_food(['其他異國料理','義式'],['餐酒館','酒吧','義大利麵','披薩'],[500,1300],'南洋風味餐酒與義式主餐，依酒飲與點餐方式規劃預算。',['晚餐'])
    if n.startswith('貳巷貓弄'):
        set_food(['義式'],['咖啡廳','義大利麵','甜點店'],[200,500],'貓咪主題空間，提供義大利麵、鬆餅與飲料。',['午餐','晚餐','甜點／飲料'])
        m['childRating']='普通';m['childBasis']='店名公告未滿12歲孩童須電話或粉絲團預約，請先向店家確認。'
    if n.startswith('老先覺'):set_food(['台式'],['火鍋','吃到飽'],[280,600],'麻辣鍋與蔬菜自助吧；吃到飽範圍依店家方案，並非純素餐廳。',['午餐','晚餐'])
    if n.startswith('涮乃葉'):set_food(['日式'],['火鍋','吃到飽'],[450,1000],'日式涮涮鍋，餐期與方案依店家公告。',['午餐','晚餐'])
    if n.startswith('米個人燒肉'):m['price']=[250,600]
    if n.startswith('21Plus'):set_food(['美式'],['速食'],[150,400],'烤雞與速食套餐，適合快速用餐。',['午餐','晚餐'])
    if '燒肉' in m['types'] and not re.search(r'吃到飽|無限量供應|無限供應|無限續',text):m['types']=[t for t in m['types'] if t!='吃到飽']
    m['id']=f'expanded-more-{len(metadata)+1:03d}'
    m['area']='板橋・府中／中正／中山及周邊'
    if n=='阿嘉職人雞肉飯':m['dishes']=['雞肉飯']
    if n=='埔墘小吃':m['dishes']=['滷肉飯','藥燉排骨湯']
    if any(t in m['types'] for t in ['餐酒館','酒吧','居酒屋']):m['occasions']=['情侶約會','朋友聚餐','聊天聚會']
    elif any(t in m['types'] for t in ['火鍋','燒肉','熱炒']):m['occasions']=['朋友聚餐','家庭聚餐','多人聚餐']
    elif any(t in m['types'] for t in ['咖啡廳','早午餐','義大利麵']):m['occasions']=['一人用餐','情侶約會','朋友聚餐']
    lo,hi=m['price'];m['priceNote']=f'尚未逐項核對最新菜單；依 Google 店家類型與公开餐點資訊規劃每人 NT${lo}–{hi} 的參考預算，屬推估，並非已查證售價或店家平均消費。'.replace('公开','公開')
    if any(t in m['types'] for t in ['熱炒','燒肉','餐酒館']):m['priceNote']+='多人分食與酒飲會受點餐及人數影響。'
    if '吃到飽' in m['types']:m['priceNote']+='餐期、方案與服務費請向店家確認。'
    metadata[n]=m
for p in shops:
    p['rating']=str(p['rating']) if p.get('rating') is not None else '0'
    p['reviews']=str(p.get('reviews') or 0)
    if p['name'] not in metadata:p['excludedReason']='照片、評分或交通資料尚未完整查證，暫不收錄'
(ROOT/'expansion-more-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
(ROOT/'expansion-more-maps.json').write_text(json.dumps(shops,ensure_ascii=False,indent=2)+'\n')
print('Selected',len(metadata),'new shops with both walking and driving routes.')
