const API = location.protocol === 'file:' ? 'http://localhost:5000/api' : '/api';

let customers=[], products=[], sales=[], invoices=[], stockHistory=[];
let chartCategory=null, chartDoughnut=null, chartPie=null, chartReport=null;
let chartStockBar=null, chartStockPie=null;
let isAdmin=false, pendingSection=null, reportData=[], currentStockFilter='all';

const PROTECTED=['sales','customers','products','stocks','invoices','reports'];
const titles={dashboard:'Dashboard',sales:'Sales',customers:'Customers',products:'Products',stocks:'Stocks',invoices:'Invoices',reports:'Reports'};

// ═══ AUTH ═══
async function checkAuth(){
  try{ const r=await fetch(API+'/auth/check',{credentials:'include'}); const d=await r.json(); isAdmin=d.authenticated===true; }
  catch(e){ isAdmin=false; }
  updateAuthUI();
}
function updateAuthUI(){
  document.getElementById('btn-login').style.display=isAdmin?'none':'inline-flex';
  document.getElementById('btn-logout').style.display=isAdmin?'inline-flex':'none';
  document.getElementById('admin-badge').style.display=isAdmin?'inline-flex':'none';
  PROTECTED.forEach(s=>{ const l=document.getElementById('lock-'+s); if(l) l.style.display=isAdmin?'none':'inline'; });
}
function showLogin(t){ if(t) pendingSection=t; document.getElementById('login-overlay').classList.add('visible'); document.getElementById('login-user').value=''; document.getElementById('login-pass').value=''; document.getElementById('login-error').textContent=''; setTimeout(()=>document.getElementById('login-user').focus(),300); }
function hideLogin(){ document.getElementById('login-overlay').classList.remove('visible'); pendingSection=null; }
async function login(){
  const u=document.getElementById('login-user').value.trim(), p=document.getElementById('login-pass').value;
  const err=document.getElementById('login-error'), btn=document.getElementById('login-submit-btn');
  if(!u||!p){ err.textContent='Enter username and password'; return; }
  btn.disabled=true; btn.textContent='Logging in...'; err.textContent='';
  try{
    const r=await fetch(API+'/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({username:u,password:p})});
    const d=await r.json();
    if(r.ok&&d.success){ isAdmin=true; updateAuthUI(); hideLogin(); toast('Logged in'); if(pendingSection){navigateTo(pendingSection);pendingSection=null;} await refreshAll(); }
    else{ err.textContent=d.error||'Invalid credentials'; }
  }catch(e){ err.textContent='Connection error'; }
  btn.disabled=false; btn.textContent='LOGIN';
}
async function logout(){ try{await fetch(API+'/logout',{method:'POST',credentials:'include'});}catch(e){} isAdmin=false; updateAuthUI(); navigateTo('dashboard'); toast('Logged out'); }
document.addEventListener('keydown',e=>{ if(e.key==='Enter'&&document.getElementById('login-overlay').classList.contains('visible')) login(); });

// ═══ NAV ═══
function navigateTo(sec){
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  const nav=document.querySelector(`.nav-item[data-section="${sec}"]`);
  if(nav) nav.classList.add('active');
  document.getElementById('section-'+sec).classList.add('active');
  document.getElementById('pageTitle').textContent=titles[sec];
}
document.querySelectorAll('.nav-item').forEach(item=>{
  item.addEventListener('click',()=>{
    const sec=item.dataset.section;
    if(item.dataset.protected==='true'&&!isAdmin){showLogin(sec);return;}
    navigateTo(sec);
    if(sec==='invoices') loadInvoices();
    if(sec==='stocks') loadStocksPage();
  });
});

// ═══ HELPERS ═══
function toast(m,t='success'){ const el=document.getElementById('toast'); el.textContent=(t==='success'?'✓ ':'✗ ')+m; el.className='show '+t; setTimeout(()=>el.className='',3000); }
async function api(path,method='GET',body=null){
  const opts={method,headers:{'Content-Type':'application/json'},credentials:'include'};
  if(body) opts.body=JSON.stringify(body);
  const res=await fetch(API+path,opts);
  if(res.status===401){ isAdmin=false; updateAuthUI(); navigateTo('dashboard'); showLogin(); toast('Session expired','error'); throw new Error('Session expired'); }
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}
function badge(c){ const m={'Electronics':'elec','Home Goods':'home','Apparel':'app'}; return `<span class="badge badge-${m[c]||'other'}">${c||'—'}</span>`; }
function memberBadge(t){ return t==='Gold'?`<span class="badge badge-gold">Gold</span>`:`<span class="badge badge-regular">${t||'Regular'}</span>`; }
function stockBadge(q){ if(q<=0) return `<span class="badge badge-outstock">Out of Stock</span>`; if(q<=10) return `<span class="badge badge-lowstock">Low (${q})</span>`; return `<span class="badge badge-instock">In Stock</span>`; }
function stockBar(q,max){ const pct=max>0?Math.min((q/max)*100,100):0; const cls=pct>50?'high':pct>20?'medium':'low'; return `<div class="stock-bar"><div class="stock-bar-fill ${cls}" style="width:${pct}%"></div></div>${q}`; }
function invBadge(s){ const m={'Paid':'paid','Pending':'pending','Cancelled':'cancelled'}; return `<span class="badge badge-${m[s]||'pending'}">${s}</span>`; }
const fmt=v=>'$'+Number(v).toLocaleString('en-US',{minimumFractionDigits:2});

// ═══ KPIs ═══
async function loadKPIs(){
  const d=await api('/analytics/kpis');
  document.getElementById('kpi-revenue').textContent=fmt(d.total_revenue);
  document.getElementById('kpi-sales').textContent=d.total_sales;
  document.getElementById('kpi-avg').textContent=fmt(d.avg_order_value);
  document.getElementById('kpi-customers').textContent=d.total_customers;
  document.getElementById('kpi-products').textContent=d.total_products;
  document.getElementById('kpi-lowstock').textContent=d.low_stock_count||0;
  document.getElementById('kpi-outstock').textContent=d.out_stock_count||0;
  document.getElementById('kpi-pending').textContent=d.pending_invoices||0;
}

// ═══ CHARTS ═══
const ACCENT=['#ec4899','#3b82f6','#a855f7','#f43f5e','#3ddc84'];
async function loadCharts(){
  const catData=await api('/analytics/revenue-by-category');
  if(chartCategory) chartCategory.destroy(); if(chartDoughnut) chartDoughnut.destroy(); if(chartPie) chartPie.destroy();
  Chart.defaults.color='#94a3b8'; Chart.defaults.font={family:"'JetBrains Mono',monospace",size:11};
  chartCategory=new Chart(document.getElementById('chartCategory'),{type:'bar',data:{labels:catData.map(r=>r.category),datasets:[{data:catData.map(r=>r.total_revenue),backgroundColor:ACCENT.map(c=>c+'CC'),borderColor:ACCENT,borderWidth:1,borderRadius:4,barThickness:20}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{grid:{color:'#334155'},ticks:{callback:v=>'$'+v}}}}});
  chartDoughnut=new Chart(document.getElementById('chartDoughnut'),{type:'doughnut',data:{labels:catData.map(r=>r.category),datasets:[{data:catData.map(r=>r.total_revenue),backgroundColor:ACCENT,borderWidth:0,hoverOffset:8}]},options:{responsive:true,maintainAspectRatio:false,cutout:'65%',plugins:{legend:{position:'right',labels:{usePointStyle:true,boxWidth:8,padding:10}}}}});
  let g=0,r=0; customers.forEach(c=>{if(c.member_type==='Gold')g++;else r++;}); if(!g&&!r){g=1;r=1;}
  chartPie=new Chart(document.getElementById('chartPie'),{type:'pie',data:{labels:['Gold','Regular'],datasets:[{data:[g,r],backgroundColor:['#fbbf24','#64748b'],borderWidth:0,hoverOffset:8}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{usePointStyle:true,boxWidth:8,padding:10}}}}});
}

// ═══ AUTO-CALC ═══
function calcSaleAmount(){
  const sel=document.getElementById('sale-product'); const opt=sel.options[sel.selectedIndex];
  const price=parseFloat(opt?.getAttribute('data-price')||0);
  const qty=parseInt(document.getElementById('sale-qty').value)||0;
  document.getElementById('sale-amount').value=(price*qty>0)?(price*qty).toFixed(2):'';
}

// ═══ SALES ═══
async function loadSales(){
  sales=await api('/sales'); const tbody=document.getElementById('sales-tbody');
  document.getElementById('sales-count').textContent=sales.length+' records';
  if(!sales.length){tbody.innerHTML=`<tr><td colspan="10"><div class="empty">No sales yet</div></td></tr>`;return;}
  tbody.innerHTML=sales.map(s=>`<tr><td class="td-mono" style="color:var(--muted)">#${s.sale_id}</td><td>${s.customer_name}</td><td>${s.product_name}</td><td>${badge(s.category)}</td><td class="td-mono">${s.sale_date}</td><td class="td-mono">${s.quantity}</td><td class="td-mono">${fmt(s.unit_price||0)}</td><td class="td-mono" style="color:var(--accent);font-weight:700">${fmt(s.sale_amount)}</td><td>${s.invoice_no?`<span class="badge badge-paid">${s.invoice_no}</span>`:'—'}</td><td><button class="btn btn-danger" onclick="deleteSale(${s.sale_id})">✕</button></td></tr>`).join('');
}
async function addSale(){
  const cid=document.getElementById('sale-customer').value,pid=document.getElementById('sale-product').value,date=document.getElementById('sale-date').value,qty=document.getElementById('sale-qty').value,amount=document.getElementById('sale-amount').value;
  if(!cid||!pid||!date||!qty){toast('Fill all fields','error');return;}
  if(!amount||parseFloat(amount)<=0){toast('Select product with price','error');return;}
  try{await api('/sales','POST',{customer_id:+cid,product_id:+pid,sale_date:date,quantity:+qty,sale_amount:+amount});toast('Sale added + Invoice generated');document.getElementById('sale-qty').value=1;document.getElementById('sale-amount').value='';await Promise.all([loadSales(),loadProducts(),loadKPIs(),loadCharts()]);}catch(e){if(e.message!=='Session expired')toast('Error: '+e.message,'error');}
}
async function deleteSale(id){if(!confirm('Delete?'))return;try{await api('/sales/'+id,'DELETE');toast('Deleted');await Promise.all([loadSales(),loadProducts(),loadKPIs(),loadCharts()]);}catch(e){if(e.message!=='Session expired')toast(e.message,'error');}}

// ═══ CUSTOMERS ═══
async function loadCustomers(){
  customers=await api('/customers'); const tbody=document.getElementById('customers-tbody');
  document.getElementById('customers-count').textContent=customers.length+' records';
  document.getElementById('sale-customer').innerHTML=customers.map(c=>`<option value="${c.customer_id}">${c.first_name} ${c.last_name}</option>`).join('');
  if(!customers.length){tbody.innerHTML=`<tr><td colspan="9"><div class="empty">No customers</div></td></tr>`;return;}
  tbody.innerHTML=customers.map(c=>`<tr><td class="td-mono" style="color:var(--muted)">${c.customer_id}</td><td>${c.first_name}</td><td>${c.last_name}</td><td>${c.city||'—'}</td><td class="td-mono">${c.mobile_no||'—'}</td><td>${c.email||'—'}</td><td>${c.region||'—'}</td><td>${memberBadge(c.member_type)}</td><td><div class="action-btns"><button class="btn btn-edit" onclick="editCustomer(${c.customer_id})">✎</button><button class="btn btn-danger" onclick="deleteCustomer(${c.customer_id})">✕</button></div></td></tr>`).join('');
}
async function submitCustomer(){
  const editId=document.getElementById('cust-edit-id').value;
  const f=document.getElementById('cust-first').value.trim(),l=document.getElementById('cust-last').value.trim();
  if(!f||!l){toast('Name required','error');return;}
  const p={first_name:f,last_name:l,city:document.getElementById('cust-city').value.trim(),mobile_no:document.getElementById('cust-mobile').value.trim(),email:document.getElementById('cust-email').value.trim(),region:document.getElementById('cust-region').value,member_type:document.getElementById('cust-member').value};
  try{if(editId){await api('/customers/'+editId,'PUT',p);toast('Updated');}else{await api('/customers','POST',p);toast('Added');}cancelCustomerEdit();await Promise.all([loadCustomers(),loadKPIs(),loadCharts()]);}catch(e){if(e.message!=='Session expired')toast(e.message,'error');}
}
function editCustomer(id){const c=customers.find(x=>x.customer_id===id);if(!c)return;document.getElementById('cust-first').value=c.first_name||'';document.getElementById('cust-last').value=c.last_name||'';document.getElementById('cust-city').value=c.city||'';document.getElementById('cust-mobile').value=c.mobile_no||'';document.getElementById('cust-email').value=c.email||'';document.getElementById('cust-region').value=c.region||'';document.getElementById('cust-member').value=c.member_type||'Regular';document.getElementById('cust-edit-id').value=id;document.getElementById('customer-form-title').textContent='Editing #'+id;document.getElementById('cust-submit-btn').textContent='Update';document.getElementById('cust-submit-btn').className='btn btn-update';document.getElementById('cust-cancel-btn').style.display='inline-flex';document.getElementById('customer-form-panel').classList.add('editing');document.getElementById('customer-form-panel').scrollIntoView({behavior:'smooth'});}
function cancelCustomerEdit(){document.getElementById('cust-edit-id').value='';['cust-first','cust-last','cust-city','cust-mobile','cust-email'].forEach(id=>document.getElementById(id).value='');document.getElementById('cust-region').value='';document.getElementById('cust-member').value='Regular';document.getElementById('customer-form-title').textContent='Add Customer';document.getElementById('cust-submit-btn').textContent='+ Add Customer';document.getElementById('cust-submit-btn').className='btn btn-primary';document.getElementById('cust-cancel-btn').style.display='none';document.getElementById('customer-form-panel').classList.remove('editing');}
async function deleteCustomer(id){if(!confirm('Delete customer & sales?'))return;try{await api('/customers/'+id,'DELETE');toast('Deleted');cancelCustomerEdit();await Promise.all([loadCustomers(),loadSales(),loadKPIs(),loadCharts()]);}catch(e){if(e.message!=='Session expired')toast(e.message,'error');}}

// ═══ PRODUCTS ═══
async function loadProducts(){
  products=await api('/products'); const tbody=document.getElementById('products-tbody');
  document.getElementById('products-count').textContent=products.length+' records';
  const sel=document.getElementById('sale-product');
  sel.innerHTML=products.map(p=>`<option value="${p.product_id}" data-price="${p.unit_price||0}" data-stock="${p.stock_qty||0}">${p.product_name} — ${fmt(p.unit_price||0)} [${p.stock_qty||0}]</option>`).join('');
  sel.removeEventListener('change',calcSaleAmount); sel.addEventListener('change',calcSaleAmount);
  // Restock dropdown
  document.getElementById('restock-product').innerHTML=products.map(p=>`<option value="${p.product_id}">${p.product_name} (Current: ${p.stock_qty||0})</option>`).join('');
  if(!products.length){tbody.innerHTML=`<tr><td colspan="7"><div class="empty">No products</div></td></tr>`;return;}
  tbody.innerHTML=products.map(p=>`<tr><td class="td-mono" style="color:var(--muted)">${p.product_id}</td><td>${p.product_name}</td><td>${badge(p.category)}</td><td class="td-mono" style="color:var(--accent)">${fmt(p.unit_price||0)}</td><td class="td-mono">${p.stock_qty||0}</td><td>${stockBadge(p.stock_qty||0)}</td><td><div class="action-btns"><button class="btn btn-edit" onclick="editProduct(${p.product_id})">✎</button><button class="btn btn-danger" onclick="deleteProduct(${p.product_id})">✕</button></div></td></tr>`).join('');
  calcSaleAmount();
}
async function submitProduct(){
  const editId=document.getElementById('prod-edit-id').value,name=document.getElementById('prod-name').value.trim(),cat=document.getElementById('prod-category').value,price=document.getElementById('prod-price').value,stock=document.getElementById('prod-stock').value;
  if(!name){toast('Name required','error');return;}
  if(!price||parseFloat(price)<0){toast('Valid price needed','error');return;}
  const p={product_name:name,category:cat,unit_price:parseFloat(price),stock_qty:parseInt(stock)||0};
  try{if(editId){await api('/products/'+editId,'PUT',p);toast('Updated');}else{await api('/products','POST',p);toast('Added');}cancelProductEdit();await Promise.all([loadProducts(),loadKPIs()]);}catch(e){if(e.message!=='Session expired')toast(e.message,'error');}
}
function editProduct(id){const p=products.find(x=>x.product_id===id);if(!p)return;document.getElementById('prod-name').value=p.product_name||'';document.getElementById('prod-category').value=p.category||'Other';document.getElementById('prod-price').value=p.unit_price||'';document.getElementById('prod-stock').value=p.stock_qty||0;document.getElementById('prod-edit-id').value=id;document.getElementById('product-form-title').textContent='Editing #'+id;document.getElementById('prod-submit-btn').textContent='Update';document.getElementById('prod-submit-btn').className='btn btn-update';document.getElementById('prod-cancel-btn').style.display='inline-flex';document.getElementById('product-form-panel').classList.add('editing');document.getElementById('product-form-panel').scrollIntoView({behavior:'smooth'});}
function cancelProductEdit(){document.getElementById('prod-edit-id').value='';document.getElementById('prod-name').value='';document.getElementById('prod-price').value='';document.getElementById('prod-stock').value='0';document.getElementById('prod-category').value='Electronics';document.getElementById('product-form-title').textContent='Add Product';document.getElementById('prod-submit-btn').textContent='+ Add Product';document.getElementById('prod-submit-btn').className='btn btn-primary';document.getElementById('prod-cancel-btn').style.display='none';document.getElementById('product-form-panel').classList.remove('editing');}
async function deleteProduct(id){if(!confirm('Delete product & sales?'))return;try{await api('/products/'+id,'DELETE');toast('Deleted');cancelProductEdit();await Promise.all([loadProducts(),loadSales(),loadKPIs(),loadCharts()]);}catch(e){if(e.message!=='Session expired')toast(e.message,'error');}}

// ═══ STOCKS PAGE ═══
async function loadStocksPage(){
  await loadProducts(); // Ensure products are fresh
  const total=products.length;
  const instock=products.filter(p=>(p.stock_qty||0)>10).length;
  const low=products.filter(p=>(p.stock_qty||0)>0&&(p.stock_qty||0)<=10).length;
  const out=products.filter(p=>(p.stock_qty||0)<=0).length;
  const units=products.reduce((s,p)=>s+(p.stock_qty||0),0);

  document.getElementById('stock-total').textContent=total;
  document.getElementById('stock-instock').textContent=instock;
  document.getElementById('stock-low').textContent=low;
  document.getElementById('stock-out').textContent=out;
  document.getElementById('stock-units').textContent=units;

  renderStockTable(currentStockFilter);
  renderStockCharts(instock,low,out);
  await loadStockHistory();
}

function filterStock(filter){
  currentStockFilter=filter;
  renderStockTable(filter);
}

function renderStockTable(filter){
  const maxStock=Math.max(...products.map(p=>p.stock_qty||0),1);
  let filtered=products;
  if(filter==='instock') filtered=products.filter(p=>(p.stock_qty||0)>10);
  else if(filter==='low') filtered=products.filter(p=>(p.stock_qty||0)>0&&(p.stock_qty||0)<=10);
  else if(filter==='out') filtered=products.filter(p=>(p.stock_qty||0)<=0);

  const tbody=document.getElementById('stocks-tbody');
  if(!filtered.length){tbody.innerHTML=`<tr><td colspan="7"><div class="empty">No products match filter</div></td></tr>`;return;}
  tbody.innerHTML=filtered.map(p=>`<tr>
    <td class="td-mono" style="color:var(--muted)">${p.product_id}</td>
    <td>${p.product_name}</td><td>${badge(p.category)}</td>
    <td class="td-mono" style="color:var(--accent)">${fmt(p.unit_price||0)}</td>
    <td class="td-mono">${p.stock_qty||0}</td>
    <td>${stockBar(p.stock_qty||0,maxStock)}</td>
    <td>${stockBadge(p.stock_qty||0)}</td>
  </tr>`).join('');
}

function renderStockCharts(instock,low,out){
  if(chartStockBar) chartStockBar.destroy();
  if(chartStockPie) chartStockPie.destroy();

  const sorted=[...products].sort((a,b)=>(b.stock_qty||0)-(a.stock_qty||0)).slice(0,10);
  chartStockBar=new Chart(document.getElementById('chartStockBar'),{
    type:'bar',
    data:{labels:sorted.map(p=>p.product_name.substring(0,15)),datasets:[{data:sorted.map(p=>p.stock_qty||0),backgroundColor:sorted.map(p=>{const q=p.stock_qty||0;return q<=0?'#f43f5eCC':q<=10?'#fbbf24CC':'#3ddc84CC';}),borderRadius:4,barThickness:18}]},
    options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{grid:{color:'#334155'}},y:{grid:{display:false}}}}
  });

  chartStockPie=new Chart(document.getElementById('chartStockPie'),{
    type:'doughnut',
    data:{labels:['In Stock (>10)','Low Stock (1-10)','Out of Stock (0)'],datasets:[{data:[instock,low,out],backgroundColor:['#3ddc84','#fbbf24','#f43f5e'],borderWidth:0,hoverOffset:8}]},
    options:{responsive:true,maintainAspectRatio:false,cutout:'60%',plugins:{legend:{position:'right',labels:{usePointStyle:true,boxWidth:8,padding:10}}}}
  });
}

async function restockProduct(){
  const pid=document.getElementById('restock-product').value;
  const qty=parseInt(document.getElementById('restock-qty').value)||0;
  if(!pid||qty<=0){toast('Select product and enter valid qty','error');return;}
  try{
    await api('/stocks/restock','POST',{product_id:+pid,quantity:qty});
    toast('Restocked successfully');
    document.getElementById('restock-qty').value=1;
    await Promise.all([loadProducts(),loadKPIs(),loadStocksPage()]);
  }catch(e){if(e.message!=='Session expired')toast(e.message,'error');}
}

async function loadStockHistory(){
  try{
    const data=await api('/stocks/history');
    stockHistory=data;
    const tbody=document.getElementById('stock-history-tbody');
    if(!data.length){tbody.innerHTML=`<tr><td colspan="5"><div class="empty">No stock changes yet</div></td></tr>`;return;}
    tbody.innerHTML=data.map(h=>{
      const typeColor=h.change_type==='RESTOCK'?'badge-instock':h.change_type==='SALE'?'badge-outstock':'badge-lowstock';
      const sign=h.qty_change>0?'+':'';
      return `<tr>
        <td class="td-mono">${h.created_at||'—'}</td>
        <td>${h.product_name}</td>
        <td><span class="badge ${typeColor}">${h.change_type}</span></td>
        <td class="td-mono" style="color:${h.qty_change>0?'#3ddc84':'#f43f5e'}">${sign}${h.qty_change}</td>
        <td class="td-mono">${h.new_stock}</td>
      </tr>`;
    }).join('');
  }catch(e){ /* ignore if table doesn't exist yet */ }
}

// ═══ INVOICES (list) ═══
async function loadInvoices(){
  try{
    invoices=await api('/invoices'); const tbody=document.getElementById('invoices-tbody');
    document.getElementById('invoices-count').textContent=invoices.length+' records';
    if(!invoices.length){tbody.innerHTML=`<tr><td colspan="9"><div class="empty">No invoices yet</div></td></tr>`;return;}
    tbody.innerHTML=invoices.map(inv=>`<tr>
      <td class="td-mono" style="color:var(--accent);font-weight:700;">${inv.invoice_no}</td>
      <td>${inv.customer_name}</td>
      <td class="td-mono">${inv.sale_date}</td>
      <td>${inv.product_name} ×${inv.quantity}</td>
      <td class="td-mono">${fmt(inv.subtotal)}</td>
      <td class="td-mono">${fmt(inv.tax_amount)}</td>
      <td class="td-mono" style="font-weight:700;color:#3ddc84;">${fmt(inv.grand_total)}</td>
      <td>${invBadge(inv.status)}</td>
      <td><div class="action-btns">
        <button class="btn btn-purple btn-sm" onclick="downloadSavedInvoice(${inv.invoice_id})">PDF</button>
        ${inv.status==='Pending'?`<button class="btn btn-success btn-sm" onclick="markPaid(${inv.invoice_id})">Paid</button>`:''}
      </div></td>
    </tr>`).join('');
  }catch(e){if(e.message!=='Session expired')toast('Error loading invoices','error');}
}
async function markPaid(id){
  try{await api('/invoices/'+id+'/status','PUT',{status:'Paid'});toast('Marked Paid');await Promise.all([loadInvoices(),loadKPIs()]);}
  catch(e){if(e.message!=='Session expired')toast(e.message,'error');}
}
function downloadSavedInvoice(id){window.open(API+'/invoices/'+id+'/download','_blank');}


// ═══ INVOICE BUILDER ═══════════════════════════════════════════
let invRows   = [];      // [{sale_id, description, unit_price, qty, amount}]
let invPayload = null;   // last built payload — reused by download after save

// ── Generate random invoice number ──
function genInvNo(){
  const yr  = new Date().getFullYear();
  const mo  = String(new Date().getMonth()+1).padStart(2,'0');
  const rnd = Math.floor(10000+Math.random()*90000);
  const no  = `INV-${yr}${mo}-${rnd}`;
  document.getElementById('inv-number-display').textContent = no;
  return no;
}
function currentInvNo(){ return document.getElementById('inv-number-display').textContent || genInvNo(); }

// ── Populate customer dropdown ──
function populateInvCustomers(){
  const sel = document.getElementById('inv-customer');
  sel.innerHTML = '<option value="">— Pick Customer —</option>' +
    customers.map(c=>
      `<option value="${c.customer_id}">${c.customer_id} — ${c.first_name} ${c.last_name}${c.city?', '+c.city:''}</option>`
    ).join('');
}

// ── Customer selected → fetch their sales and fill rows ──
async function onInvCustomerChange(){
  const cid = +document.getElementById('inv-customer').value;
  const chip = document.getElementById('inv-cust-chip');
  if(!cid){ chip.style.display='none'; invRows=[]; renderInvRows(); recalcTotals(); return; }

  // Show customer chip
  const c = customers.find(x=>x.customer_id===cid);
  if(c){
    document.getElementById('inv-cust-name').textContent = `${c.first_name} ${c.last_name}`;
    document.getElementById('inv-cust-meta').innerHTML =
      `City: <b style="color:var(--text)">${c.city||'—'}</b> &nbsp;|&nbsp; `+
      `Mobile: <b style="color:var(--text)">${c.mobile_no||'—'}</b> &nbsp;|&nbsp; `+
      `Email: <b style="color:var(--text)">${c.email||'—'}</b> &nbsp;|&nbsp; `+
      `Region: <b style="color:var(--text)">${c.region||'—'}</b>`;
    chip.style.display = 'block';
  }

  // Fetch customer's existing sales as line items
  try{
    const salesData = await api(`/customers/${cid}/sales`);
    if(salesData && salesData.length){
      invRows = salesData.map(s=>({
        sale_id:     s.sale_id,
        description: s.description || s.product_name || '—',
        unit_price:  parseFloat(s.unit_price||0),
        qty:         parseInt(s.qty||s.quantity||1),
        amount:      parseFloat(s.amount||s.sale_amount||0),
        sale_date:   s.sale_date||'',
        invoice_no:  s.invoice_no||null,   // null = not yet invoiced
      }));
      toast(`Loaded ${invRows.length} sale(s) for ${c?c.first_name:'customer'}`);
    } else {
      invRows = [];
      toast('No existing sales — add rows manually');
    }
  } catch(e){
    invRows = [];
    toast('Could not load sales: '+e.message,'error');
  }
  renderInvRows();
  recalcTotals();
}

// ── Add blank row ──
function addInvRow(){
  invRows.push({sale_id:null, description:'', unit_price:0, qty:1, amount:0});
  renderInvRows();
  setTimeout(()=>{ const el=document.getElementById(`inv-desc-${invRows.length-1}`); if(el) el.focus(); },60);
}

// ── Remove row ──
function removeInvRow(idx){
  invRows.splice(idx,1);
  renderInvRows();
  recalcTotals();
}

// ── Re-render rows ──
function renderInvRows(){
  const container = document.getElementById('inv-rows-container');
  if(!invRows.length){
    container.innerHTML=`<div style="padding:24px;text-align:center;color:var(--muted);font-size:12px;">Select a customer to auto-fill, or click "+ Add Row"</div>`;
    return;
  }
  container.innerHTML = invRows.map((row,i)=>{
    const alreadyInv = row.invoice_no ? `<span style="font-size:9px;background:rgba(61,220,132,.12);color:#3ddc84;padding:1px 6px;border-radius:4px;margin-left:4px;">${row.invoice_no}</span>` : '';
    return `<div style="display:grid;grid-template-columns:36px 1fr 110px 70px 100px 36px;border-bottom:1px solid var(--border);background:${i%2===0?'var(--surface)':'var(--surface2)'};">
      <div style="padding:8px 10px;color:var(--muted);font-size:11px;display:flex;align-items:center;">${i+1}</div>
      <div style="padding:4px 4px;">
        <input id="inv-desc-${i}" class="form-control inv-cell-input" placeholder="Description"
               value="${escHtml(row.description)}"
               oninput="invRows[${i}].description=this.value" />
        ${alreadyInv}
      </div>
      <div style="padding:4px 4px;">
        <input type="number" id="inv-price-${i}" class="form-control inv-cell-input" style="text-align:right;" min="0" step="0.01"
               value="${row.unit_price||''}" placeholder="0.00"
               oninput="invRows[${i}].unit_price=parseFloat(this.value)||0;calcRowAmt(${i});" />
      </div>
      <div style="padding:4px 4px;">
        <input type="number" id="inv-qty-${i}" class="form-control inv-cell-input" style="text-align:center;" min="1"
               value="${row.qty||1}"
               oninput="invRows[${i}].qty=parseInt(this.value)||1;calcRowAmt(${i});" />
      </div>
      <div style="padding:8px 10px;display:flex;align-items:center;justify-content:flex-end;">
        <span style="font-family:var(--font-mono);font-size:12px;color:var(--accent);" id="inv-amt-${i}">$${(row.amount||0).toFixed(2)}</span>
      </div>
      <div style="padding:4px;display:flex;align-items:center;justify-content:center;">
        <button onclick="removeInvRow(${i})" style="background:none;border:none;color:var(--muted);cursor:pointer;font-size:16px;line-height:1;padding:2px 6px;" title="Remove">×</button>
      </div>
    </div>`;
  }).join('');
}

function escHtml(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

function calcRowAmt(idx){
  const r = invRows[idx];
  r.amount = parseFloat(((r.unit_price||0)*(r.qty||1)).toFixed(2));
  const el = document.getElementById(`inv-amt-${idx}`);
  if(el) el.textContent = '$'+r.amount.toFixed(2);
  recalcTotals();
}

function recalcTotals(){
  const sub   = invRows.reduce((s,r)=>s+(r.amount||0),0);
  const tax   = sub*0.18;
  const grand = sub+tax;
  const box   = document.getElementById('inv-totals');
  if(sub>0){
    box.style.display='block';
    document.getElementById('inv-sub').textContent   = '$'+sub.toFixed(2);
    document.getElementById('inv-tax').textContent   = '$'+tax.toFixed(2);
    document.getElementById('inv-grand').textContent = '$'+grand.toFixed(2);
  } else {
    box.style.display='none';
  }
}

// ── Build payload ──
function buildInvPayload(){
  const cid   = +document.getElementById('inv-customer').value;
  const invNo = currentInvNo();
  const notes = document.getElementById('inv-notes').value.trim();
  if(!cid)  { toast('Select a customer','error'); return null; }
  const valid = invRows.filter(r=>r.description&&r.amount>0);
  if(!valid.length){ toast('Add at least one line item with amount','error'); return null; }
  const customer   = customers.find(x=>x.customer_id===cid)||{};
  const subtotal   = parseFloat(valid.reduce((s,r)=>s+r.amount,0).toFixed(2));
  const taxAmount  = parseFloat((subtotal*0.18).toFixed(2));
  const grandTotal = parseFloat((subtotal+taxAmount).toFixed(2));
  return { invoice_no:invNo, customer_id:cid, customer, items:valid, subtotal, tax_rate:18, tax_amount:taxAmount, grand_total:grandTotal, notes };
}

// ── Preview (HTML modal) ──
function previewInvoice(){
  const p = buildInvPayload();
  if(!p) return;
  invPayload = p;
  renderPreviewModal(p);
  document.getElementById('inv-modal-overlay').style.display='block';
  document.body.style.overflow='hidden';
}
function closeInvModal(){
  document.getElementById('inv-modal-overlay').style.display='none';
  document.body.style.overflow='';
}

function renderPreviewModal(p){
  const today = new Date();
  const due   = new Date(); due.setDate(due.getDate()+14);
  const fd    = d=>d.toLocaleDateString('en-GB').replace(/\//g,'-');
  const C     = { name:'SalesDB Pvt. Ltd.', pin:'754289', phone:'+91 7894389104', email:'sales@salesdb.com', gst:'21XXXXX1234X1ZX' };

  document.getElementById('inv-modal-no').textContent = p.invoice_no;
  document.getElementById('inv-modal-body').innerHTML = `
    <div style="background:#f3f0ff;border-radius:8px;padding:18px 22px;margin-bottom:22px;display:flex;justify-content:space-between;align-items:flex-start;">
      <div>
        <div style="font-size:16px;font-weight:700;color:#1e293b;margin-bottom:3px;">${C.name}</div>
        <div style="font-size:10px;color:#64748b;line-height:1.9;">
          Address : Kendrapara, Odisha, PIN ${C.pin}<br>
          Phone   : ${C.phone}<br>
          Email   : ${C.email}<br>
          GSTIN   : ${C.gst}
        </div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:10px;">
        <!-- Sidebar-style logo -->
        <div style="background:linear-gradient(135deg,#be185d,#7c3aed);border-radius:8px;padding:9px 16px;text-align:center;min-width:100px;">
          <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:20px;color:#fff;line-height:1;text-shadow:0 0 8px rgba(236,72,153,0.5);">
            Sales<span style="color:#fce7f3;">DB</span>
          </div>
          <div style="font-size:8px;color:rgba(255,255,255,0.75);letter-spacing:2px;text-transform:uppercase;margin-top:3px;">Analytics</div>
        </div>
        <!-- Invoice meta -->
        <div style="text-align:right;font-size:11px;color:#64748b;line-height:1.9;">
          <strong style="color:#1e293b;font-size:13px;">${p.invoice_no}</strong><br>
          Date : ${fd(today)}<br>
          Due  : ${fd(due)}
        </div>
      </div>
    </div>

    <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;margin-bottom:18px;">
      <div style="font-size:10px;font-weight:700;color:#7c3aed;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Bill To</div>
      <div style="font-size:13px;font-weight:700;color:#1e293b;">${p.customer.first_name||''} ${p.customer.last_name||''}</div>
      <div style="font-size:11px;color:#64748b;line-height:1.9;margin-top:3px;">
        City: ${p.customer.city||'—'} &nbsp;|&nbsp; Mobile: ${p.customer.mobile_no||'—'}<br>
        Email: ${p.customer.email||'—'} &nbsp;|&nbsp; Region: ${p.customer.region||'—'}
      </div>
    </div>

    <table style="width:100%;border-collapse:collapse;margin-bottom:18px;font-size:12px;">
      <thead>
        <tr style="background:#7c3aed;">
          <th style="padding:8px 10px;color:#fff;text-align:left;">#</th>
          <th style="padding:8px 10px;color:#fff;text-align:left;">Description</th>
          <th style="padding:8px 10px;color:#fff;text-align:right;">Unit Price</th>
          <th style="padding:8px 10px;color:#fff;text-align:center;">Qty</th>
          <th style="padding:8px 10px;color:#fff;text-align:right;">Amount</th>
        </tr>
      </thead>
      <tbody>
        ${p.items.map((item,i)=>`
          <tr style="background:${i%2===0?'#faf5ff':'#fff'};">
            <td style="padding:8px 10px;border-bottom:1px solid #e2e8f0;">${i+1}</td>
            <td style="padding:8px 10px;border-bottom:1px solid #e2e8f0;">${escHtml(item.description)}</td>
            <td style="padding:8px 10px;border-bottom:1px solid #e2e8f0;text-align:right;">$${parseFloat(item.unit_price||0).toFixed(2)}</td>
            <td style="padding:8px 10px;border-bottom:1px solid #e2e8f0;text-align:center;">${item.qty}</td>
            <td style="padding:8px 10px;border-bottom:1px solid #e2e8f0;text-align:right;font-weight:600;color:#7c3aed;">$${parseFloat(item.amount).toFixed(2)}</td>
          </tr>`).join('')}
      </tbody>
    </table>

    <div style="display:flex;justify-content:flex-end;margin-bottom:18px;">
      <div style="min-width:250px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:5px;font-size:12px;"><span style="color:#64748b;">Subtotal</span><span style="font-family:monospace;">$${p.subtotal.toFixed(2)}</span></div>
        <div style="display:flex;justify-content:space-between;margin-bottom:10px;font-size:12px;"><span style="color:#64748b;">GST (18%)</span><span style="font-family:monospace;">$${p.tax_amount.toFixed(2)}</span></div>
        <div style="border-top:2px solid #7c3aed;padding-top:8px;display:flex;justify-content:space-between;">
          <span style="font-weight:700;color:#1e293b;font-size:13px;">Total (USD)</span>
          <span style="font-family:monospace;font-weight:800;color:#7c3aed;font-size:15px;">$${p.grand_total.toFixed(2)}</span>
        </div>
      </div>
    </div>

    ${p.notes?`<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:6px;padding:9px 13px;margin-bottom:16px;font-size:11px;color:#92400e;"><strong>Notes:</strong> ${escHtml(p.notes)}</div>`:''}

    <div style="border-top:1px solid #e2e8f0;padding-top:12px;font-size:10px;color:#94a3b8;">
      <strong style="color:#7c3aed;">Terms and Conditions</strong><br>
      Payment is due within 14 days. Please make checks payable to: ${C.name}<br>
      Contact: ${C.phone} | ${C.email}
    </div>
    <div style="margin-top:14px;background:#f3f0ff;border-radius:6px;padding:7px;text-align:center;font-size:9px;color:#94a3b8;">
      Generated by SalesDB | ${C.name} | Kendrapara, Odisha | PIN ${C.pin}
    </div>`;
}

// ── Save to DB + Download PDF ──
async function saveInvoice(){
  const p = buildInvPayload();
  if(!p) return;
  invPayload = p;

  try{
    // 1. Save to database
    const saved = await api('/invoices/save','POST',{
      customer_id: p.customer_id,
      items:       p.items,
      notes:       p.notes,
    });
    // Use the server-generated invoice number
    invPayload.invoice_no = saved.invoice_no || p.invoice_no;
    document.getElementById('inv-number-display').textContent = invPayload.invoice_no;
    toast('Invoice saved: '+invPayload.invoice_no);

    // 2. Refresh all affected sections
    await Promise.all([loadInvoices(), loadSales(), loadKPIs()]);

    // 3. Download PDF
    // await downloadCustomInvoice();

  } catch(e){
    if(e.message!=='Session expired') toast('Save failed: '+e.message,'error');
  }
}

// ── Download PDF only (uses last built payload) ──
async function downloadCustomInvoice(){
  const p = invPayload || buildInvPayload();
  if(!p) return;
  invPayload = p;
  try{
    const res = await fetch(API+'/invoices/download-custom',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      credentials:'include',
      body: JSON.stringify(p),
    });
    if(!res.ok){ const e=await res.json(); toast(e.error||'Download failed','error'); return; }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href=url; a.download=p.invoice_no+'.pdf'; a.click();
    URL.revokeObjectURL(url);
    toast('PDF downloaded: '+p.invoice_no);
  }catch(e){ toast('Download error: '+e.message,'error'); }
}

// ── Reset form ──
function resetInvoiceForm(){
  document.getElementById('inv-customer').value='';
  document.getElementById('inv-cust-chip').style.display='none';
  document.getElementById('inv-notes').value='';
  document.getElementById('inv-totals').style.display='none';
  invRows=[]; invPayload=null;
  renderInvRows();
  genInvNo();
}

// ── Hook navigateTo to init builder when opening invoices ──
const _origNav = navigateTo;
navigateTo = function(sec){
  _origNav(sec);
  if(sec==='invoices'){
    populateInvCustomers();
    loadInvoices();
    if(!document.getElementById('inv-number-display').textContent||
       document.getElementById('inv-number-display').textContent==='—') genInvNo();
    if(!invRows.length) renderInvRows();
  }
};

// Close modal on backdrop click
document.getElementById('inv-modal-overlay').addEventListener('click',function(e){
  if(e.target===this) closeInvModal();
});

// ═══ REPORTS ═══
async function loadReport(){
  const from=document.getElementById('report-from').value,to=document.getElementById('report-to').value,cat=document.getElementById('report-cat').value,region=document.getElementById('report-region').value;
  let url='/reports/sales?';
  if(from)url+='from='+from+'&'; if(to)url+='to='+to+'&'; if(cat)url+='category='+cat+'&'; if(region)url+='region='+region+'&';
  try{
    const data=await api(url); reportData=data.records||[];
    document.getElementById('report-kpis').style.display='grid';
    document.getElementById('rpt-revenue').textContent=fmt(data.total_revenue||0);
    document.getElementById('rpt-count').textContent=data.total_count||0;
    document.getElementById('rpt-avg').textContent=fmt(data.avg_order||0);
    document.getElementById('report-table-panel').style.display='block';
    document.getElementById('report-count').textContent=reportData.length+' records';
    const tbody=document.getElementById('report-tbody');
    if(!reportData.length){tbody.innerHTML=`<tr><td colspan="8"><div class="empty">No data</div></td></tr>`;}
    else{tbody.innerHTML=reportData.map(s=>`<tr><td class="td-mono" style="color:var(--muted)">#${s.sale_id}</td><td>${s.customer_name}</td><td>${s.product_name}</td><td>${badge(s.category)}</td><td class="td-mono">${s.sale_date}</td><td class="td-mono">${s.quantity}</td><td class="td-mono">${fmt(s.unit_price||0)}</td><td class="td-mono" style="color:var(--accent)">${fmt(s.sale_amount)}</td></tr>`).join('');}
    document.getElementById('report-charts').style.display='grid';
    if(chartReport)chartReport.destroy();
    const daily={};reportData.forEach(r=>{daily[r.sale_date]=(daily[r.sale_date]||0)+r.sale_amount;});const dates=Object.keys(daily).sort();
    chartReport=new Chart(document.getElementById('chartReport'),{type:'line',data:{labels:dates,datasets:[{data:dates.map(d=>daily[d]),borderColor:'#ec4899',backgroundColor:'rgba(236,72,153,0.1)',borderWidth:2,pointRadius:4,tension:0.3,fill:true}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{grid:{color:'#334155'},ticks:{callback:v=>'$'+v}}}}});
    toast('Report generated');
  }catch(e){if(e.message!=='Session expired')toast(e.message,'error');}
}
function exportCSV(){
  if(!reportData.length){toast('Generate report first','error');return;}
  const h=['Sale ID','Customer','Product','Category','Date','Qty','Price','Total'];
  const rows=reportData.map(s=>[s.sale_id,s.customer_name,s.product_name,s.category,s.sale_date,s.quantity,s.unit_price||0,s.sale_amount]);
  let csv=h.join(',')+'\n'; rows.forEach(r=>{csv+=r.map(v=>`"${v}"`).join(',')+'\n';});
  const blob=new Blob([csv],{type:'text/csv'}); const url=URL.createObjectURL(blob);
  const a=document.createElement('a'); a.href=url; a.download='SalesDB_Report.csv'; a.click(); URL.revokeObjectURL(url);
  toast('CSV exported');
}

// ═══ INIT ═══
async function refreshAll(){
  try{await Promise.all([loadCustomers(),loadProducts(),loadSales()]);await Promise.all([loadKPIs(),loadCharts()]);toast('Data refreshed');}
  catch(e){if(e.message!=='Session expired'){toast('Cannot reach API','error');document.querySelector('.status-dot').style.background='#ff6b6b';}}
}
document.getElementById('sale-date').valueAsDate=new Date();
document.getElementById('sale-qty').addEventListener('input',calcSaleAmount);
(async()=>{await checkAuth();await refreshAll();})();