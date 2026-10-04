import json,re
from pathlib import Path
root=Path('/Users/yujen/nate_project/home_nearby_food')
shops=json.loads((root/'expansion-500-maps.json').read_text());routes=json.loads((root/'expansion-500-routes.json').read_text())
# Category/position comes from the observed Maps store page. Budgets without menu support remain explicit planning estimates.
budgets={
'六堆伙房':(200,450),'板橋新埔食堂':(200,400),'陶板屋':(800,1100),'和牛涮':(900,1300),'聚 日式':(400,700),'炎上':(900,1500),'涮武鶴':(1000,1800),'燒惑':(800,1250),'石二鍋':(250,450),'川蜀':(200,450),'大魔':(500,1200),'吉哆':(600,1000),'海牧':(600,1200),'XO':(600,1200),'樂釜':(500,1000),'初鍋':(350,700),'錢都':(280,550),'友谷':(320,600),'梁季':(300,550),'新埔洞天':(350,650),'武侍':(400,750),'chao':(600,1100),'頑味':(1000,1500),'豐華':(700,1500),'喝桶海':(600,1200),'魚港':(500,1000),'四維客棧':(500,900),'食樂堂':(400,800),'品鮮':(400,800),'天香':(250,600),'金龍':(500,1000),'旬野':(400,900),'鮨跡':(600,1500),'二穀':(300,700),'賀本':(200,400),'鯨於':(100,200),'煨煨':(100,250),'萬得富':(250,450),'大小通吃':(100,250),'HALO':(130,300),'泰之初':(200,450),'TNT':(400,850),'樂威':(250,550),'風日':(300,600),'MJ':(350,750),'緣聚':(500,1000),'丹生':(400,700),'金春喜':(400,700),'涓豆腐':(450,800),'TG':(180,350),'定食8':(220,400),'老串角':(500,1000),'老味噌':(500,1000),'BELLINI':(450,800),'solemio':(450,800),'P\'go':(250,500),'禾多':(300,650),'NU':(200,450),'初義':(150,300),'烏龍麵所':(150,300),'大師兄':(250,450),'樂麵屋':(300,500),'讚岐':(150,350),'大洺':(200,350),'來來':(100,250),'武越天':(100,250),'甘泉':(180,300),'五六':(100,250),'二姊':(100,250),'元氣':(100,220),'日日晴食':(130,250),'182':(200,400),'Bonnie':(200,450),'拾梯':(250,500),'古斯塔':(150,400),'糰聚':(60,150),'福來':(80,220),'J Kitchen':(80,200),'美而美':(60,180),'早。自己':(80,200),'肉sandwich':(180,350),'拾貳籃':(170,350),'Quack':(280,450),'時光造所':(150,350),'清原':(60,150),'娃娃臉':(80,200),'這里恬':(80,200),'埔墘市場':(40,120),'星巴克':(120,350),'彼得好':(80,250),'有kaffe':(120,300)}
review_price_notes={
'烏龍麵所':'此次查閱的 Google 公開評論提到柴魚昆布烏龍麵110元、豆皮加點20元；評論價格可能較舊，加入其他餐點預留150–300元。',
'Quack':'Google 公開評論提到法式吐司280元；主餐搭飲品預留280–450元，最新菜單待店家確認。',
'拾貳籃':'Google 公開評論提到總匯100元加70元套餐；依不同主餐規劃170–350元，最新價格待店家確認。',
'聚 日式':'Google 公開評論記載有500元內的單人用餐組合；不同主餐與加點預留400–700元，最新菜單待確認。',
'老串角居酒屋-江子翠':'此次 Google 公開評論出現每人400–600元區間；串燒搭配酒飲規劃500–1,000元，並非店家統計平均。',
'來來':'Google 公開評論記載水餃每顆8元、至少10顆，另有麵與湯品；規劃每人100–250元，評論價格可能較舊。',
'友谷':'Google 公開評論記載基本鍋約319元；加點與肉品不同，預留320–600元，最新價格待確認。',
'頑味':'Google 公開評論記載曾以每人1,000元預算提供無菜單料理；預留1,000–1,500元，需事先確認當日內容與價格。',
'糰聚':'Google 公開評論記載內用飯糰50元、鮪魚蛋餅45元、豆漿30元；規劃每人60–150元，外送價格不同且評論價格可能較舊。',
'清原':'Google 公開評論記載紅豆湯約100元，業主回覆鮮奶紅茶70元；單份甜品或飲料規劃60–150元，特殊加料另計。',
'涮武鶴':'Google 公開評論記載1,580元吃到飽另加一成服務費；不同方案預留1,000–1,800元，訂位前請確認最新方案。',
'錢都日式涮涮鍋-板橋莒光':'Google 公開評論記載低脂牛鍋289元；不同主餐及加點預留280–550元，評論價格可能較舊。',
'燒惑':'Google 公開評論記載699／899／1,099元套餐另加一成服務費；預留800–1,250元，最新方案待店家确认。',
}
def starts(name,mapping):return next((v for k,v in mapping.items() if k in name),None)
def classify(p):
 n=p['name'];lines=p['text'].splitlines();i=next((i for i,x in enumerate(lines) if re.fullmatch(r'\([\d,]+\)',x)),None);cat=(lines[i+1] if i is not None else '').split('·')[0];key=n+' '+cat
 c=['台式'];t=['小吃'];period=['午餐','晚餐'];lo,hi=100,300;desc='街區裡的日常用餐選擇。'
 if any(k in key for k in ['咖啡店','咖啡廳','CAFE','咖啡哈','pancake','KDI CAFE']):c=['不適用（咖啡／茶飲）'];t=['咖啡廳'];period=['下午茶','甜點／飲料'];lo,hi=120,350;desc='咖啡與午後休息的選擇，餐點以店內當日供應為準。'
 if any(k in key for k in ['甜品','糕餅','餅店','烘焙','雪花冰','米苔目冰','舒芙蕾','水果塔','甜塔','點點甜甜','清原']):t=['甜點店'];period=['下午茶','甜點／飲料'];lo,hi=80,350;desc='甜點或烘焙點心，適合下午茶與外帶分享。'
 if '法式' in key or '古斯塔亨利' in key:c=['法式']
 if any(k in key for k in ['珍珠奶茶','茶飲','茶坊','茶行','茶聚','都可','COMEBUY','再睡5分鐘','五桐號','麻古','季緣','晴喜摘','天湧茶','烏弄']):c=['台式'];t=['飲料店'];period=['下午茶','甜點／飲料'];lo,hi=35,110;desc='外帶茶飲與特色飲品，飯後順路帶一杯。'
 if any(k in key for k in ['早餐','早午餐','Kitchen','小巷柒食','美而美','早。自己','糰聚','Near Home','Brunch','藍海子','邑朵','鳳梨寶堡','182 pancake']):c=['台式','美式'];t=['早餐店'] if '早餐店' in cat else ['早午餐'];period=['早餐','早午餐','午餐'];lo,hi=(60,200) if t==['早餐店'] else (180,400);desc='早餐與輕食選擇，適合白天簡單吃一餐。'
 if '早午餐' in t:period+=['下午茶']
 if '咖啡店' in cat and '咖啡廳' not in t:t+=['咖啡廳']
 if any(k in key for k in ['麵店','麵食','烏冬','烏龍麵所','麵館','麵擔','鍋燒麵','銷魂麵','水餃','餃子店']):c=['台式'];t=['麵店','小吃'];period=['午餐','晚餐'];lo,hi=100,280;desc='麵食與小吃，適合一個人或快速用餐。'
 if '烏冬' in key or '烏龍麵所' in n:c=['日式'];t=['麵店']
 if '小螺波' in n:c=['中式'];desc='廣西風味螺螄粉，想吃酸辣麵食時的選擇。'
 if '拉麵' in key or 'ラーメン' in key or '樂麵屋' in key:c=['日式'];t=['拉麵','麵店'];lo,hi=250,450;desc='日式拉麵，適合午晚餐吃一碗熱湯麵。'
 if any(k in key for k in ['定食','日本餐廳','日本料理','日料','日式食堂','丼飯','壽司']):c=['日式'];t=['飯類'];lo,hi=250,700;desc='日式料理與單人主餐，依當日菜單選擇。'
 if any(k in key for k in ['壽司','鮨跡','旬野','日料']):t+=['壽司']
 if '丼飯' in key or '二穀' in n:t+=['丼飯']
 if any(k in key for k in ['居酒屋','老串角 板橋','老味噌','緣聚']):c=['日式'] if '緣聚' not in n else ['台式'];t=['居酒屋'] if '緣聚' not in n else ['餐酒館'];period=['晚餐','宵夜'];lo,hi=500,1000;desc='晚間聚餐與酒食選擇，適合朋友相約。'
 if any(k in key for k in ['意大利','義式','義大利麵','PASTA','Pasta','solemio','BELLINI','MJ Bistro','風日洋食']):c=['義式'];t=['義大利麵'];period=['午餐','晚餐'];lo,hi=250,600;desc='義式主餐，適合約會或朋友輕鬆聚餐。'
 if any(k in key for k in ['禾多','solemio','BELLINI','P\'go']):t+=['披薩']
 if any(k in key for k in ['泰國','泰式','盈泰豐','泰廚','泰之初']):c=['泰式'];t=['熱炒'] if '早午餐' not in t else t;period=['午餐','晚餐'];lo,hi=200,500;desc='泰式料理，適合換個口味或多人分食。'
 if any(k in key for k in ['韓國','韓式','韓廚','涓豆腐','煨煨']):c=['韓式'];t=['飯類','小吃'];period=['午餐','晚餐'];lo,hi=200,500;desc='韓式餐點，依當日菜單挑選一餐。'
 if '煨煨' in n:c=['台式','韓式'];desc='粥品與韓式飯捲，適合外帶與日常用餐。'
 if '越南' in key:c=['越式'];t=['麵店','小吃'];lo,hi=100,250;desc='越南風味麵食與小吃。'
 if any(k in key for k in ['馬來西亞','肉骨茶']):c=['新馬料理'];t=['小吃','飯類'];lo,hi=250,450;desc='肉骨茶湯品，想喝熱湯時的一餐。'
 if any(k in key for k in ['快餐店','速食','麥當勞','德克士']):c=['美式'];t=['速食'];lo,hi=120,300;desc='速食與套餐，適合快速用餐。'
 if any(k in key for k in ['扒房','牛排館']):c=['美式'];t=['牛排'];lo,hi=300,800;desc='牛排主餐，適合午晚餐聚會。'
 if '陶板屋' in n:c=['日式','美式'];t=['牛排'];desc='和風洋食套餐，適合約會與慶生聚餐。'
 if any(k in key for k in ['中菜館','台灣餐廳','客家菜','海鮮餐廳','魚港','喝桶海','四維客棧','豐華小館','品鮮','天香小廚']):c=['台式'] if '豐華' not in n else ['中式'];t=['熱炒'];lo,hi=300,800;desc='台式或中式料理，適合多人分享一桌。'
 if '六堆' in n:t=['麵店','飯類','熱炒'];desc='客家麵食與家常菜，單人或多人分食都能選。'
 if any(k in key for k in ['炒飯','潮飯','雞飯','健康餐','餐盒','大小通吃']):c=['台式'];t=['飯類','便當'] if '餐盒' in key else ['飯類','小吃'];lo,hi=100,250;desc='飯類主餐，適合日常午晚餐或外帶。'
 if '食神滷味' in n:t=['小吃'];lo,hi=100,250;desc='滷味小吃，依想吃的食材自由搭配。'
 if '砂鍋粥' in n:c=['中式'];t=['小吃'];lo,hi=250,600;desc='潮汕砂鍋粥，適合多人分食暖胃的一餐。'
 if any(k in key for k in ['火鍋','涮涮','鍋物','獨享鍋','和牛涮']):c=['台式'];t=['火鍋'];period=['午餐','晚餐'];lo,hi=350,750;desc='火鍋主餐，適合午晚餐與朋友聚會。'
 if '日式' in key or '和牛涮' in n:c=['日式']
 if any(k in key for k in ['和牛涮','吉哆','涮武鶴','chao潮肉']):t+=['吃到飽']
 if '梁季' in n or '粵式' in n:c=['港式']
 if '丹生炊事' in n:c=['台式'];t=['火鍋','熱炒'];desc='台式鍋物與共享餐點，適合多人聚餐。'
 if '燒肉' in key:c=['日式'];t=['燒肉','吃到飽'];period=['午餐','晚餐'];lo,hi=800,1500;desc='日式燒肉聚餐，依套餐選擇不同肉品。'
 # Late-night tag is supported by the observed closing time, not generic cuisine assumptions.
 clock=re.search(r'打烊時間：(\d{1,2}):(\d{2})',p['text'])
 if clock and (int(clock.group(1))>=22 or int(clock.group(1))<5) and t!=['飲料店'] and '宵夜' not in period:period+=['宵夜']
 if '深夜早餐' in n:period=['晚餐','宵夜'];desc='深夜供應早餐類餐點，想吃宵夜時的選擇。'
 override=starts(n,budgets)
 if override:lo,hi=override
 occasions=['一人用餐','快速用餐']
 if any(v in t for v in ['早午餐','咖啡廳','甜點店']):occasions=['一人用餐','情侶約會','聊天聚會']
 if any(v in t for v in ['義大利麵','披薩','壽司','牛排']):occasions=['一人用餐','情侶約會','朋友聚餐']
 if any(v in t for v in ['熱炒','火鍋','燒肉']):occasions=['朋友聚餐','家庭聚餐','多人聚餐']
 if any(v in t for v in ['居酒屋','餐酒館']):occasions=['情侶約會','朋友聚餐','聊天聚會']
 child='未查證';childBasis=None
 if re.search(r'親子友善|對小孩友善|帶小孩方便|兒童餐椅|兒童餐具|兒童附餐',p['text']):child='適合';childBasis='Google 公開資料有親子用餐記載，並非店家保證';occasions+=['帶小孩']
 # Do not classify a venue as child-unfriendly solely because it serves alcohol.
 if '陶板屋' in n:occasions+=['慶生','長輩聚餐']
 short=n.split('|')[0].split('｜')[0].strip()
 short=re.split(r'-板橋美食|-新埔美食|-江子翠捷運站|\.新北手沖|⎜',short)[0]
 short=re.sub(r'\([^)]*\)|（[^）]*）','',short).strip()
 short=re.sub(r'\s+Night Burger.*','',short)
 short=re.sub(r'請看IG.*','',short)
 if 'Guten Morgen' in n:short='貳巷食號 Guten Morgen'
 if '時光造所' in n:short='時光造所 As Time Goes By'
 if '有kaffe' in n:short='有 kaffe 冇・新埔店'
 if '鳳梨寶堡' in n:short='鳳梨寶堡'
 note='營業與菜單依店家當日公告；適合時段是用餐情境參考，請先查看實際營業時間。'
 if '售完' in n:note+='售完可能提早打烊。'
 if '無訂位' in n:note+='店名公告無訂位服務。'
 if '只收現金' in n:note+='店名公告只收現金。'
 priceNote=starts(n,review_price_notes)
 if not priceNote:priceNote=f'尚未逐項核對最新菜單；依 Google 店家定位規劃每人 NT${lo}–{hi} 的參考預算，屬推估而非已查證售價或店家平均消費。'
 if any(v in t for v in ['熱炒','燒肉']):priceNote+='人均依多人分食估算，會受點餐與人數影響。'
 if '吃到飽' in t or '陶板屋' in n:priceNote+='餐期、平假日、服務費與加價品項請向店家確認。'
 sources=[{'label':'Google Maps｜店家定位、餐點照片與公開評論；未查證價格為規劃推估','url':p['url']}]
 if p.get('website'):sources.append({'label':'店家網站／菜單入口（由 Maps 提供）','url':p['website']})
 if '六堆伙房' in n:sources+=[{'label':'六堆伙房官方｜料理與新埔店資訊','url':'https://www.liouduai.com.tw/'}]
 if '石二鍋' in n:sources+=[{'label':'石二鍋官方｜菜單入口','url':'https://www.12hotpot.com.tw/menu-list.php'}]
 meta=dict(shortName=short,area='板橋・新埔及周邊',cuisines=c,types=list(dict.fromkeys(t)),periods=list(dict.fromkeys(period)),occasions=list(dict.fromkeys(occasions)),childRating=child,price=[lo,hi],priceNote=priceNote,description=desc,note=note,dishes=[],sources=sources,classificationBasis='料理與型態依 Maps 店家定位整理；場合、兒童友善與未查證預算為參考判斷。')
 if childBasis:meta['childBasis']=childBasis
 return meta

def category(p):
 lines=p['text'].splitlines()
 i=next((i for i,x in enumerate(lines) if re.fullmatch(r'\([\d,]+\)',x)),None)
 return lines[i+1].split('·')[0] if i is not None else ''

def enrich(p,meta):
 n=p['name'];cat=category(p);key=n+' '+cat
 def change(c,t,price,desc,periods=None):
  meta.update(cuisines=c,types=t,price=list(price),description=desc)
  if periods:meta['periods']=periods
 if any(k in key for k in ['飯盒','便當','燒臘','雞腿王']):
  change(['港式'] if '港式' in key or '燒臘' in key else ['台式'],['便當','飯類'],(100,230),'便當與飯類主餐，適合外帶或快速用餐。',['午餐','晚餐'])
 if any(k in key for k in ['無酒精飲料','冰品飲料','先喝道','50嵐','茶萃','蔗醴','七福手作茶飲','正阪橋茶水坊']):
  change(['台式'],['飲料店'],(40,120),'茶飲或特色飲品，適合外帶。',['下午茶','甜點／飲料'])
 if '冰品店' in cat or '冰品' in n or any(k in n for k in ['吃啥冰品','十分甜品','大方冰品','二水町','紅豆煜','阿賢古早味麵茶']):
  change(['台式'],['甜點店'],(60,180),'冰品與甜品，適合午後休息或外帶。',['下午茶','甜點／飲料'])
 if any(k in key for k in ['鐵板燒','鐵板料理','Teppanyaki']):
  change(['台式'],['鐵板燒'],(350,1000),'鐵板料理主餐，適合午晚餐或聚餐。',['午餐','晚餐'])
 if any(k in key for k in ['粵菜','港式茶餐','望月樓']):
  change(['港式'],['飲茶','熱炒'],(500,1200),'港式餐點與共享料理，適合多人分食。',['午餐','晚餐'])
 if '韓式燒烤' in cat or 'Manna韓式' in n:
  change(['韓式'],['燒肉'],(700,1300),'韓式烤肉，適合朋友與家庭聚餐。',['午餐','晚餐'])
 if '四川' in cat or any(k in n for k in ['川味','重慶','成都','螺螄','川菜']):
  meta['cuisines']=['中式']
 if '滬菜' in cat or '上海廚藝' in n:meta['cuisines']=['中式']
 if '牛排' in n and '鐵板燒' not in meta['types']:
  change(['美式'],['牛排'],(250,750),'牛排主餐，依不同肉品與套餐規劃用餐預算。',['午餐','晚餐'])
 if '彌生軒' in n or 'YAYOI' in n or '台灣松屋' in n:
  change(['日式'],['飯類','丼飯'],(180,450),'日式飯類與定食，適合一人用餐或日常午晚餐。',['午餐','晚餐'])
 if '日式炸豬扒' in cat or '勝牛' in n:
  change(['日式'],['飯類'],(350,700),'日式炸物主餐與套餐，依店內菜單選擇。',['午餐','晚餐'])
 if any(k in key for k in ['漢堡','美式餐廳','現代美式','英式餐廳']):
  change(['其他異國料理'] if '英式' in cat else ['美式'],['飯類','小吃'],(300,700),'西式主餐與輕食，適合朋友聚會或午晚餐。',['午餐','晚餐'])
 if 'SUBWAY' in n or '肯德基' in n or 'Potato Corner' in n:
  change(['美式'],['速食'],(100,300),'速食、輕食或外帶點心，適合快速用餐。',['午餐','晚餐'])
 if any(k in key for k in ['蔬食','素食']):
  meta['types']=list(dict.fromkeys(meta['types']+['素食／蔬食']))
 if '自助餐餐廳' in cat:
  if '素食／蔬食' not in meta['types']:
   change(['台式','其他異國料理'],['Buffet','吃到飽'],(800,1500),'自助餐與共享聚餐選擇，依餐期與方案訂位。',['午餐','下午茶','晚餐'])
  else:meta['price']=[100,250]
 if '客家' in key or '粄條' in key:meta['cuisines']=['台式'];meta['types']=list(dict.fromkeys(meta['types']+['麵店']))
 if any(k in n for k in ['牛肉麵','切仔麵','蚵仔麵線','油庫口','湯麵','鍋燒','抄手','福州乾麵','米粉湯','麵攤','麵茶']) and '麵茶' not in n and not any(t in meta['types'] for t in ['拉麵','義大利麵']):
  meta['types']=list(dict.fromkeys(['麵店']+meta['types']))
 if '韓式燒烤' in cat:meta['cuisines']=['韓式']
 if '海底撈' in n:meta['cuisines']=['中式'];meta['price']=[600,1200]
 if any(k in key for k in ['海南雞','星馬','肉骨茶']):meta['cuisines']=['新馬料理']
 if '越式' in cat or '越南' in key:meta['cuisines']=['越式'];meta['types']=['麵店','小吃'];meta['price']=[100,250]
 if any(k in key for k in ['義式','義大利','意大利','Pasta','pasta','FlagPasta']):meta['cuisines']=['義式'];meta['types']=['義大利麵'];meta['price']=[220,650]
 if 'pizza' in key.lower():meta['types'].append('披薩')
 if '早食' in n or '飯丸' in n or '飯糰' in n or '吐司' in n or '豆漿' in n or '早餐' in n or '早喚' in n or 'BREAKFAST' in n:
  meta['types']=['早餐店'];meta['periods']=['早餐','早午餐','午餐'];meta['price']=[60,200];meta['description']='早餐與輕食，適合白天用餐或外帶。'
 if '親子餐廳' in cat:meta.update(childRating='適合',childBasis='Google 店家類型標示親子餐廳；實際用餐規定請向店家確認')
 if '調進所' in n or 'LAFORYA' in n or '青寓' in n or 'coffee' in n.lower() or 'cafe' in n.lower() or '咖啡' in n or '珈琲' in n:
  if '咖啡店' in cat or '外帶咖啡' in cat or '珈琲' in n:meta['cuisines']=['不適用（咖啡／茶飲）'];meta['types']=list(dict.fromkeys(['咖啡廳']+(['早午餐'] if '早午餐' in meta['types'] else [])));meta['periods']=['下午茶','甜點／飲料'];meta['price']=[120,350]
 if '售完' in n:meta['note']+='售完可能提早打烊。'
 if '預約' in n:meta['note']+='店名標示預約制，請先向店家確認。'
 if '取貨' in n or '網路訂購' in n:meta['note']+='店名標示取貨／網路訂購，內用服務未確認。'
 if '工作室' in n:meta['note']+='工作室的內用、取貨與預約方式請先詢問。'
 if '不接受訂位' in n or '無提供訂位' in n:meta['note']+='店名標示不提供訂位。'
 meta['shortName']=re.split(r'\s*[|｜丨⎜]\s*',meta['shortName'])[0].strip()
 meta['occasions']=['一人用餐','快速用餐']
 if any(t in meta['types'] for t in ['咖啡廳','甜點店','早午餐']):meta['occasions']=['一人用餐','情侶約會','聊天聚會']
 if any(t in meta['types'] for t in ['義大利麵','披薩','壽司','牛排','鐵板燒']):meta['occasions']=['一人用餐','情侶約會','朋友聚餐']
 if any(t in meta['types'] for t in ['熱炒','燒肉','火鍋','Buffet','飲茶']):meta['occasions']=['朋友聚餐','家庭聚餐','多人聚餐']
 if any(t in meta['types'] for t in ['居酒屋','餐酒館']):meta['occasions']=['情侶約會','朋友聚餐','聊天聚會']
 if meta.get('childRating')=='適合':meta['occasions'].append('帶小孩')
 lo,hi=meta['price'];meta['priceNote']=f'尚未逐項核對最新菜單；依 Google 店家類型與公開餐點資訊規劃每人 NT${lo}–{hi} 的參考預算，屬推估，並非已查證售價或店家平均消費。'
 if any(t in meta['types'] for t in ['熱炒','燒肉','飲茶']):meta['priceNote']+='多人分食會受人數與點餐影響。'
 if '吃到飽' in meta['types'] or 'Buffet' in meta['types']:meta['priceNote']+='餐期、方案與服務費請向店家確認。'
 return meta

route_lookup={(r['name'],r['mode']):r for r in routes}
existing=[p for p in json.loads((root/'restaurants.json').read_text())['places'] if not p['id'].startswith('expanded-500-')]
identity=lambda u:re.search(r'!1s([^!]+)',u).group(1) if re.search(r'!1s([^!]+)',u) else u
seen={identity(p['mapUrl']) for p in existing}
complete=[];partial=[]
for p in shops:
 cat=category(p);cid=identity(p['url'])
 if cat in ['運輸服務','傳統市場','酒舖','商店','隱形眼鏡供應商','商場']:
  p['excludedReason']='非獨立餐飲店家（'+cat+'）';continue
 if cid in seen:p['excludedReason']='與既有 Google Maps 店家地點重複';continue
 seen.add(cid)
 if p.get('closed'):continue
 if len({u.split('=')[0] for u in p['photos']})<5:p['excludedReason']='目前未取得五張不同店家照片，待補查';continue
 w=route_lookup.get((p['name'],'walking'));d=route_lookup.get((p['name'],'driving'))
 wm=int(re.search(r'(\d+) 分',w['options'][0]).group(1)) if w else None
 dm=int(re.search(r'(\d+) 分',d['options'][0]).group(1)) if d else None
 if w and d:
  if wm<=20 or dm<=15:complete.append(p)
  else:p['excludedReason']='超過步行20分鐘且開車15分鐘範圍'
 elif w and wm<=20:partial.append(p)
 else:p['excludedReason']='交通路線資料待複查，暫不收錄'
selected=complete+partial[:300-len(complete)]
assert len(selected)==300
metadata={}
for idx,p in enumerate(selected):
 meta=enrich(p,classify(p));meta['id']=f'expanded-500-{idx+1:03d}'
 if (p['name'],'driving') not in route_lookup:
  meta['note']+='已確認步行20分鐘內；開車時間尚未查證，不列入開車篩選。'
 metadata[p['name']]=meta
for p in partial:
 if p['name'] not in metadata:p['excludedReason']='暫列候補：步行範圍已確認，開車資料待補查'
(root/'expansion-500-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
(root/'expansion-500-maps.json').write_text(json.dumps(shops,ensure_ascii=False,indent=2)+'\n')
print('Selected',len(complete),'complete +',len(selected)-len(complete),'walking-confirmed stores')
