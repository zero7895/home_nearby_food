const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const data = window.NEARBY_DATA;
let visibleCount = 24;
let selected = '全部', photoIndex = 0, photoPlace = null;
const normalizeSearch = value => value.normalize('NFKC').toLocaleLowerCase('zh-TW').replace(/台/g,'臺');
const searchIndex = new Map(data.places.map(p => [p.id, normalizeSearch([p.name,p.address,p.description,...p.tags,...p.dishes,...p.cuisines,...p.types].join(' '))]));
const categories = ['全部','早餐','午餐','晚餐','咖啡廳','飲料'];
for(const [id,key] of [['period','periods'],['child','childRatings']]) {
  $('#'+id).innerHTML += data.taxonomy[key].map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join('');
}
$('#budget').innerHTML += data.taxonomy.priceBands.map(v=>`<option value="${esc(v.label)}">${esc(v.label)}</option>`).join('');
$('#hero-count').textContent = `${data.places.length} 家店`;
$('#walk option[value="all"]').textContent = `全部 ${data.places.length} 間`;
$('#categories').innerHTML = categories.map(c => `<button data-category="${c}" class="${c === selected ? 'active' : ''}" aria-pressed="${c === selected}">${c}</button>`).join('');
function fallbackImage(img) {
  img.onerror = null;
  img.classList.add('image-failed');
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="500" height="300" viewBox="0 0 500 300"><rect width="500" height="300" fill="#e8eddf"/><text x="250" y="135" text-anchor="middle" fill="#61735f" font-size="22">照片暫時無法載入</text><text x="250" y="172" text-anchor="middle" fill="#61735f" font-size="14">可開啟 Google Maps 查看原始照片</text></svg>');
}
function wireImages(root=document) {root.querySelectorAll('img').forEach(img => {img.onerror=()=>fallbackImage(img); if(img.complete && !img.naturalWidth && img.src) fallbackImage(img);});}
function render(keepPage=false) {
  if(keepPage !== true) visibleCount = 24;
  const search = normalizeSearch($('#search').value).trim().split(/\s+/).filter(Boolean), budget = $('#budget').value, walk = $('#walk').value;
  let places = data.places.filter(p => (selected === '全部' || p.tags.includes(selected)) && search.every(term => searchIndex.get(p.id).includes(term)) && (budget === 'all' || p.priceBands.includes(budget)) && (walk === 'all' || (walk === 'walk20' && p.walkMinutes <= 20) || (walk === 'drive15' && Number.isFinite(p.driveMinutes) && p.driveMinutes <= 15) || p.walkBand === walk) && ($('#period').value === 'all' || p.periods.includes($('#period').value)) && ($('#child').value === 'all' || p.childRating === $('#child').value));
  const sort = $('#sort').value;
  places.sort((a,b) => sort === 'drive' ? (Number.isFinite(a.driveMinutes)?a.driveMinutes:Infinity)-(Number.isFinite(b.driveMinutes)?b.driveMinutes:Infinity) || b.rating-a.rating : sort === 'rating' ? b.rating-a.rating || b.reviewCount-a.reviewCount : sort === 'price' ? a.price[0]-b.price[0] || a.walkMinutes-b.walkMinutes : sort === 'price-desc' ? b.price[0]-a.price[0] || a.walkMinutes-b.walkMinutes : sort === 'reviews' ? b.reviewCount-a.reviewCount : a.walkMinutes-b.walkMinutes || b.rating-a.rating);
  $('#results-count').textContent = `${places.length} 家符合你的選擇`;
  $('#empty').hidden = places.length !== 0;
  $('#load-more').hidden = places.length <= visibleCount;
  $('#load-more').textContent = `再看 ${Math.min(24,Math.max(0,places.length-visibleCount))} 間（已顯示 ${Math.min(visibleCount,places.length)} / ${places.length}）`;
  const start = keepPage === true ? $('#cards').children.length : 0;
  const markup = places.slice(start,visibleCount).map(p => `<article class="card"><div class="card-photo"><button data-detail="${p.id}" aria-label="查看${esc(p.name)}詳細資料"><img decoding="async" loading="lazy" src="${esc(p.photos[0])}" alt="${esc(p.name)}的 Google Maps 店家照片" referrerpolicy="no-referrer"></button><span class="walk-badge">${walk === 'drive15' || p.walkMinutes > 20 ? '開車 '+p.driveMinutes : '步行 '+p.walkMinutes} 分鐘</span><span class="photo-count">▧ ${p.photos.length} 張照片</span></div><div class="card-body"><div class="card-topline"><div class="card-heading"><h3>${esc(p.shortName || p.name)}</h3><p class="address">⌖ ${esc(p.address.replace('新北市板橋區',''))}</p></div><a class="card-map-link detail-button" href="${esc(p.mapUrl)}" target="_blank" rel="noopener noreferrer" aria-label="在 Google Maps 查看${esc(p.name)}">⌖ 看地圖 ↗</a></div><div class="tags">${p.tags.slice(0,4).map(t => `<span>${t}</span>`).join('')}</div><p class="description">${esc(p.description)}</p>${p.dishes.length ? `<p class="dish-recommendations"><strong>推薦品項</strong><span>${p.dishes.slice(0,3).map(esc).join('、')}</span></p>` : ''}<div class="card-bottom"><span class="price">$${p.price[0]}–${p.price[1]}<small>/ 人</small></span><button class="detail-button" data-detail="${p.id}" aria-label="查看${esc(p.name)}詳細資料">查看詳細介紹 →</button></div></div></article>`).join('');
  if(keepPage === true) $('#cards').insertAdjacentHTML('beforeend',markup);
  else $('#cards').innerHTML = markup;
  wireImages($('#cards'));
  if(keepPage === true) $('#cards').children[start]?.querySelector('[data-detail]')?.focus({preventScroll:true});
}
function openDetail(id) {
  const p = data.places.find(x => x.id === id);
  $('#detail-content').innerHTML = `<div class="random-close-bar"><button class="close" aria-label="關閉店家資料">×</button></div><div class="detail-head"><span class="eyebrow">NEIGHBORHOOD / ${esc(p.area)}</span><h2 id="detail-title">${esc(p.name)}</h2><div class="tags">${p.tags.map(t => `<span>${t}</span>`).join('')}</div><p>${esc(p.description)}</p></div><div class="detail-gallery">${p.photos.map((src,i) => `<button data-photo="${i}" aria-label="放大${esc(p.name)}第${i+1}張照片"><img src="${esc(src)}" alt="${esc(p.name)}照片 ${i+1}" referrerpolicy="no-referrer"></button>`).join('')}</div><div class="detail-info"><p class="small-note">Google Maps 店家頁面照片・點選放大・權利屬原攝影者</p><div class="detail-metrics"><div><small>Google 步行估計</small><strong>${p.walkMinutes} 分鐘</strong><p>${esc(p.walkDistance)}</p></div><div><small>Google 開車估計</small><strong>${Number.isFinite(p.driveMinutes) ? p.driveMinutes+' 分鐘' : '未查證'}</strong><p>${esc(p.driveDistance)}</p></div><div><small>人均預算・估算</small><strong>$${p.price[0]}–${p.price[1]}</strong><p>新台幣 / 每人</p></div><div><small>Google 評論</small><strong>★ ${p.rating.toFixed(1)}</strong><p>${p.reviewCount.toLocaleString('zh-TW')} 則評論</p></div></div><p><strong>地址</strong><br>${esc(p.address)}</p><section class="detail-recommendations"><h3>推薦品項</h3>${p.dishes.length ? '<ul>'+p.dishes.map(d=>'<li>'+esc(d)+'</li>').join('')+'</ul>' : '<p>推薦品項待補充</p>'}</section><div class="map-actions"><a href="${esc(p.routeUrl)}" aria-label="規劃步行路線" target="_blank" rel="noopener noreferrer"><span class="map-label-full">Google 步行導航 ↗</span><span class="map-label-short">步行 ↗</span></a><a href="${esc(p.driveRouteUrl)}" aria-label="規劃開車路線" target="_blank" rel="noopener noreferrer"><span class="map-label-full">Google 開車導航 ↗</span><span class="map-label-short">開車 ↗</span></a><a href="${esc(p.mapUrl)}" target="_blank" rel="noopener noreferrer" aria-label="Google 評論與照片"><span class="map-label-full">Google 評論與照片 ↗</span><span class="map-label-short">評論照片 ↗</span></a></div></div>`;
  $('#detail-content').querySelector('.close').onclick = () => $('#detail').close();
  const classification = document.createElement('section'); classification.className='classifications';
  const childDisplay = p.childRating === '普通' && p.childBasis === '資料不足，暫列普通，並非已確認適合兒童' ? '普通(未確認)' : p.childRating + ' · ' + p.childBasis;
  classification.innerHTML = `<dl>${[['料理國別',p.cuisines.join('・')],['餐廳型態',p.types.join('・')],['適合時段',p.periods.join('・')],['適合場合（推估）',p.occasions.join('・')],['兒童友善',childDisplay],['人均消費',`NT$${p.price[0]}–${p.price[1]}`]].map(([k,v])=>`<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl>`;
  $('#detail-content .detail-info').insertBefore(classification,$('#detail-content .detail-info .map-actions'));
  $('#detail-content').querySelectorAll('[data-photo]').forEach(button => button.onclick = () => openPhoto(p,+button.dataset.photo));
  wireImages($('#detail-content')); $('#detail').showModal(); $('#detail').scrollTop=0;
}
function showPhoto() {
  const img=$('#large-photo'); img.classList.remove('image-failed'); img.src=photoPlace.photos[photoIndex]; img.alt=`${photoPlace.name} 第 ${photoIndex+1} 張照片`;
  $('#photo-caption').textContent = `${photoPlace.name} · ${photoIndex+1} / ${photoPlace.photos.length} · 照片來源：Google Maps 店家頁面`;
  img.onerror=()=>fallbackImage(img);
}
function openPhoto(p,i) {photoPlace=p;photoIndex=i;showPhoto();$('#lightbox').showModal();}
function movePhoto(offset){photoIndex=(photoIndex+offset+photoPlace.photos.length)%photoPlace.photos.length;showPhoto();}
$('#photo-prev').onclick=()=>movePhoto(-1);$('#photo-next').onclick=()=>movePhoto(1);$('#lightbox-close').onclick=()=>$('#lightbox').close();
$('#lightbox').addEventListener('keydown',e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();movePhoto(e.key==='ArrowLeft'?-1:1);}});
[$('#detail'),$('#lightbox'),$('#random-dialog')].forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}}));
$('#cards').addEventListener('click',e=>{const detail=e.target.closest('[data-detail]'); if(detail)openDetail(detail.dataset.detail);});
$('#categories').addEventListener('click',e=>{const b=e.target.closest('[data-category]');if(!b)return;selected=b.dataset.category;$('#categories').querySelectorAll('button').forEach(b=>{b.classList.toggle('active',b.dataset.category===selected);b.setAttribute('aria-pressed',String(b.dataset.category===selected));});render();});
$('#search').addEventListener('input',e=>{if(!e.isComposing)render();});$('#search').addEventListener('compositionend',()=>render());['sort','budget','walk','period','child'].forEach(id=>$('#'+id).addEventListener('change',render));
function reset(){selected='全部';$('#search').value='';['budget','period','child'].forEach(id=>$('#'+id).value='all');$('#walk').value='all';$('#sort').value='walk';$('#categories').querySelectorAll('button').forEach(b=>{b.classList.toggle('active',b.dataset.category==='全部');b.setAttribute('aria-pressed',String(b.dataset.category==='全部'));});render();}
$('#load-more').onclick=()=>{visibleCount+=24;render(true);};
$('#reset').onclick=reset;$('#empty-reset').onclick=reset; render();wireImages();

let randomKind = 'meal';
const previousDraws = {meal:[],snack:[]};
function drawRandomPlaces() {
  const kinds = randomKind === 'meal' ? ['早餐','午餐','晚餐'] : ['咖啡廳','飲料'];
  const eligible = data.places.filter(p => kinds.some(t => p.tags.includes(t)));
  const fresh = eligible.filter(p => !previousDraws[randomKind].includes(p.id));
  const pool = fresh.length >= 3 ? fresh : eligible;
  // Partial Fisher–Yates: three distinct shops, each eligible shop equally likely.
  for(let i=0;i<Math.min(3,pool.length);i++) {
    const j=i+Math.floor(Math.random()*(pool.length-i));
    [pool[i],pool[j]]=[pool[j],pool[i]];
  }
  previousDraws[randomKind] = pool.slice(0,3).map(p=>p.id);
  $('#random-title').textContent = randomKind === 'meal' ? '今天的正餐，試試這三間！' : '點心時間，這三間等你！';
  $('#random-description').textContent = kinds.join('・')+'，隨機給你三個靈感。';
  $('#random-results').innerHTML = pool.slice(0,3).map(p => `<article class="random-card" data-place-id="${esc(p.id)}"><span class="random-walk-badge">走路 ${p.walkMinutes} 分鐘</span><img src="${esc(p.photos[0])}" alt="${esc(p.name)}的店家照片" referrerpolicy="no-referrer"><div class="random-card-body"><h3>${esc(p.shortName || p.name)}</h3><div class="tags">${p.tags.filter(t=>kinds.includes(t)).map(t=>`<span>${esc(t)}</span>`).join('')}</div><p class="random-rating">★ ${p.rating.toFixed(1)} <span>· $${p.price[0]}–${p.price[1]} / 人・估算</span></p><p class="random-description">${esc(p.description)}</p><div class="random-card-actions"><button class="detail-button" data-detail="${esc(p.id)}">詳細介紹 ↗</button><a class="random-google-link" href="${esc(p.mapUrl)}" target="_blank" rel="noopener noreferrer" aria-label="在 Google Maps 查看${esc(p.name)}">Google ↗</a></div></div></article>`).join('');
  wireImages($('#random-results'));
  $('#random-dialog').scrollTop=0;
}
document.querySelectorAll('[data-random]').forEach(button => button.onclick=()=>{randomKind=button.dataset.random;drawRandomPlaces();$('#random-dialog').showModal();$('#random-dialog').scrollTop=0;});
$('#random-again').onclick=drawRandomPlaces;
$('#random-close').onclick=()=>$('#random-dialog').close();
$('#random-results').addEventListener('click',e=>{const button=e.target.closest('[data-detail]');if(button)openDetail(button.dataset.detail);});
