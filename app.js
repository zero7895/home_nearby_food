const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const data = window.NEARBY_DATA;
let selected = '全部', savedOnly = false, photoIndex = 0, photoPlace = null;
let saved = new Set();
try { const value = JSON.parse(localStorage.getItem('nearby-favorites') || '[]'); if(Array.isArray(value)) saved = new Set(value); } catch {}
const categories = ['全部','早餐','午餐','晚餐','宵夜','下午茶','咖啡廳','飲料','台菜','港式','日式'];
for(const [id,key] of [['cuisine','cuisines'],['type','types'],['period','periods'],['occasion','occasions'],['child','childRatings']]) {
  $('#'+id).innerHTML += data.taxonomy[key].map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join('');
}
$('#budget').innerHTML += data.taxonomy.priceBands.map(v=>`<option value="${esc(v.label)}">${esc(v.label)}</option>`).join('');
$('#facility').innerHTML += Object.keys(data.places[0].childFacilities).map(v=>`<option value="${esc(v)}">${esc(v)}（有公開記載）</option>`).join('');
$('#home-map').href = data.home.mapUrl;
$('#hero-count').textContent = `${data.places.length} 家店`;
$('#hero-image').src = data.places.find(p => p.id === 'goodday').photos[2];
$('#excluded').innerHTML = data.excluded.map(p => `<a href="${esc(p.mapUrl)}" target="_blank" rel="noopener noreferrer">${esc(p.name)} ↗</a>`).join('');
$('#categories').innerHTML = categories.map(c => `<button data-category="${c}" class="${c === selected ? 'active' : ''}" aria-pressed="${c === selected}">${c}</button>`).join('');
function updateSaved() {
  $('#saved-count').textContent = saved.size;
  $('#saved-toggle').classList.toggle('active',savedOnly);
  $('#saved-toggle').setAttribute('aria-pressed',String(savedOnly));
  try { localStorage.setItem('nearby-favorites', JSON.stringify([...saved])); } catch {}
}
function toggleSaved(id) {saved.has(id) ? saved.delete(id) : saved.add(id); updateSaved(); render();}
function fallbackImage(img) {
  img.onerror = null;
  img.classList.add('image-failed');
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="500" height="300" viewBox="0 0 500 300"><rect width="500" height="300" fill="#e8eddf"/><text x="250" y="135" text-anchor="middle" fill="#61735f" font-size="22">照片暫時無法載入</text><text x="250" y="172" text-anchor="middle" fill="#61735f" font-size="14">可開啟 Google Maps 查看原始照片</text></svg>');
}
function wireImages(root=document) {root.querySelectorAll('img').forEach(img => {img.onerror=()=>fallbackImage(img); if(img.complete && !img.naturalWidth && img.src) fallbackImage(img);});}
function render() {
  const search = $('#search').value.trim().toLowerCase(), budget = $('#budget').value, walk = +$('#walk').value;
  let places = data.places.filter(p => (selected === '全部' || p.tags.includes(selected)) && (!savedOnly || saved.has(p.id)) && (!search || [p.name,p.address,p.description,...p.tags,...p.dishes,...p.cuisines,...p.types].join(' ').toLowerCase().includes(search)) && (budget === 'all' || p.priceBands.includes(budget)) && p.walkMinutes <= walk && (!$('#high-rating').checked || p.rating >= 4.5) && ['cuisine','type','period','occasion'].every(id=>$('#'+id).value === 'all' || p[({cuisine:'cuisines',type:'types',period:'periods',occasion:'occasions'})[id]].includes($('#'+id).value)) && ($('#child').value === 'all' || p.childRating === $('#child').value) && ($('#facility').value === 'all' || p.childFacilities[$('#facility').value] !== '未查證'));
  const sort = $('#sort').value;
  places.sort((a,b) => sort === 'rating' ? b.rating-a.rating || b.reviewCount-a.reviewCount : sort === 'price' ? a.price[0]-b.price[0] || a.walkMinutes-b.walkMinutes : sort === 'reviews' ? b.reviewCount-a.reviewCount : a.walkMinutes-b.walkMinutes || b.rating-a.rating);
  $('#results-count').textContent = `${savedOnly ? '我的口袋 · ' : ''}${places.length} 家符合你的選擇`;
  $('#empty').hidden = places.length !== 0;
  $('#cards').innerHTML = places.map(p => `<article class="card"><div class="card-photo"><button data-detail="${p.id}" aria-label="查看${esc(p.name)}詳細資料"><img loading="lazy" src="${esc(p.photos[0])}" alt="${esc(p.name)}的 Google Maps 店家照片" referrerpolicy="no-referrer"></button><span class="walk-badge">↗ 步行 ${p.walkMinutes} 分鐘</span><button class="save ${saved.has(p.id) ? 'saved' : ''}" data-save="${p.id}" aria-label="${saved.has(p.id) ? '取消收藏' : '收藏'}${esc(p.name)}" aria-pressed="${saved.has(p.id)}">${saved.has(p.id) ? '♥' : '♡'}</button><span class="photo-count">▧ ${p.photos.length} 張照片</span></div><div class="card-body"><div class="card-topline"><h3>${esc(p.shortName || p.name)}</h3><span class="rating"><b>★</b> ${p.rating.toFixed(1)}<span class="review-count">${p.reviewCount.toLocaleString('zh-TW')} 則 Google 評論</span></span></div><div class="tags">${p.tags.slice(0,4).map(t => `<span>${t}</span>`).join('')}</div><p class="description">${esc(p.description)}</p><div class="card-bottom"><span class="price">$${p.price[0]}–${p.price[1]}<small>/ 人・估算</small></span><button class="detail-button" data-detail="${p.id}">看看這家 ↗</button></div><p class="address">⌖ ${esc(p.address.replace('新北市板橋區',''))}</p></div></article>`).join('');
  wireImages($('#cards'));
}
function openDetail(id) {
  const p = data.places.find(x => x.id === id);
  $('#detail-content').innerHTML = `<div class="detail-head"><button class="close" aria-label="關閉店家資料">×</button><span class="eyebrow">NEIGHBORHOOD / ${esc(p.area)}</span><h2>${esc(p.name)}</h2><div class="tags">${p.tags.map(t => `<span>${t}</span>`).join('')}</div><p>${esc(p.description)}</p></div><div class="detail-gallery">${p.photos.map((src,i) => `<button data-photo="${i}" aria-label="放大${esc(p.name)}第${i+1}張照片"><img src="${esc(src)}" alt="${esc(p.name)}照片 ${i+1}" referrerpolicy="no-referrer"></button>`).join('')}</div><div class="detail-info"><p class="small-note">Google Maps 店家頁面照片・點選放大・權利屬原攝影者</p><div class="detail-metrics"><div><small>Google 步行估計</small><strong>${p.walkMinutes} 分鐘</strong><p>${esc(p.walkDistance)}</p></div><div><small>人均預算・估算</small><strong>$${p.price[0]}–${p.price[1]}</strong><p>新台幣 / 每人</p></div><div><small>Google 評論</small><strong>★ ${p.rating.toFixed(1)}</strong><p>${p.reviewCount.toLocaleString('zh-TW')} 則評論</p></div></div><p><strong>可以點什麼</strong><br>${p.dishes.map(esc).join('、')}</p><p><strong>地址</strong><br>${esc(p.address)}</p><p><strong>價格依據</strong><br>${esc(p.priceNote)}</p><p><strong>出門前留意</strong><br>${esc(p.note)}</p><div class="map-actions"><a href="${esc(p.routeUrl)}" target="_blank" rel="noopener noreferrer">Google 步行導航 ↗</a><a href="${esc(p.mapUrl)}" target="_blank" rel="noopener noreferrer">Google 評論與照片 ↗</a></div><p><strong>資料來源</strong></p><a class="source-link" href="${esc(p.mapUrl)}" target="_blank" rel="noopener noreferrer">Google Maps｜評分、評論數、地址與照片（2026/10/04 查閱） ↗</a>${p.sources.map(s => `<a class="source-link" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.label)} ↗</a>`).join('')}<p class="small-note">步行路線：${esc(p.routeVia)}。Google 路線估計以社區地圖起點為準；實際走法、等紅燈與大樓出口會影響時間。此清單並非營業狀態即時服務。</p></div>`;
  $('#detail-content').querySelector('.close').onclick = () => $('#detail').close();
  const classification = document.createElement('section'); classification.className='classifications';
  classification.innerHTML = `<h3>六個維度，找到適合的一餐</h3><dl>${[['料理國別',p.cuisines.join('・')],['餐廳型態',p.types.join('・')],['適合時段',p.periods.join('・')],['適合場合（推估）',p.occasions.join('・')],['兒童友善',p.childRating + ' · ' + p.childBasis],['人均消費（價帶）',p.priceBands.join(' / ')]].map(([k,v])=>`<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl><p class="small-note">${esc(p.classificationBasis)}</p><div class="child-info"><h4>兒童設施與空間</h4><p>${esc(p.childNote)}</p><ul>${Object.entries(p.childFacilities).map(([k,v])=>`<li><span>${esc(k)}</span><strong class="${v==='未查證'?'unverified':'evidence'}">${esc(v)}</strong></li>`).join('')}</ul></div>`;
  $('#detail-content .detail-info').insertBefore(classification,$('#detail-content .detail-info .map-actions'));
  $('#detail-content').querySelectorAll('[data-photo]').forEach(button => button.onclick = () => openPhoto(p,+button.dataset.photo));
  wireImages($('#detail-content')); $('#detail').showModal();
}
function showPhoto() {
  const img=$('#large-photo'); img.classList.remove('image-failed'); img.src=photoPlace.photos[photoIndex]; img.alt=`${photoPlace.name} 第 ${photoIndex+1} 張照片`;
  $('#photo-caption').textContent = `${photoPlace.name} · ${photoIndex+1} / ${photoPlace.photos.length} · 照片來源：Google Maps 店家頁面`;
  img.onerror=()=>fallbackImage(img);
}
function openPhoto(p,i) {photoPlace=p;photoIndex=i;showPhoto();$('#lightbox').showModal();}
function movePhoto(offset){photoIndex=(photoIndex+offset+photoPlace.photos.length)%photoPlace.photos.length;showPhoto();}
$('#photo-prev').onclick=()=>movePhoto(-1);$('#photo-next').onclick=()=>movePhoto(1);$('#lightbox-close').onclick=()=>$('#lightbox').close();
$('#lightbox').addEventListener('keydown',e=>{if(e.key==='ArrowLeft')movePhoto(-1);if(e.key==='ArrowRight')movePhoto(1);});
[$('#detail'),$('#lightbox')].forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}}));
$('#cards').addEventListener('click',e=>{const save=e.target.closest('[data-save]'), detail=e.target.closest('[data-detail]'); if(save)toggleSaved(save.dataset.save);else if(detail)openDetail(detail.dataset.detail);});
$('#categories').addEventListener('click',e=>{const b=e.target.closest('[data-category]');if(!b)return;selected=b.dataset.category;$('#categories').querySelectorAll('button').forEach(b=>{b.classList.toggle('active',b.dataset.category===selected);b.setAttribute('aria-pressed',String(b.dataset.category===selected));});render();});
$('#search').addEventListener('input',render);['sort','budget','walk','high-rating','cuisine','type','period','occasion','child','facility'].forEach(id=>$('#'+id).addEventListener('change',render));
$('#saved-toggle').onclick=()=>{savedOnly=!savedOnly;updateSaved();render();$('#explore').scrollIntoView({behavior:'smooth'});};
function reset(){selected='全部';savedOnly=false;$('#search').value='';['budget','cuisine','type','period','occasion','child','facility'].forEach(id=>$('#'+id).value='all');$('#walk').value='15';$('#sort').value='walk';$('#high-rating').checked=false;$('#categories').querySelectorAll('button').forEach(b=>{b.classList.toggle('active',b.dataset.category==='全部');b.setAttribute('aria-pressed',String(b.dataset.category==='全部'));});updateSaved();render();}
$('#reset').onclick=reset;$('#empty-reset').onclick=reset; updateSaved();render();wireImages();
