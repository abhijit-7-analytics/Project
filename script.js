const API = location.protocol === 'file:'
  ? 'http://localhost:5000/api'
  : '/api';

// ── State ──────────────────────────────────────
let customers = [], products = [], sales = [];
let chartCategory = null, chartDoughnut = null, chartPie = null;

// ── Navigation ─────────────────────────────────
const titles = {
  dashboard: 'Dashboard',
  sales: 'Sales',
  customers: 'Customers',
  products: 'Products',
};

document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    const sec = item.dataset.section;
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    item.classList.add('active');
    document.getElementById('section-' + sec).classList.add('active');
    document.getElementById('pageTitle').textContent = titles[sec];
  });
});

// ── Toast ──────────────────────────────────────
function toast(msg, type = 'success') {
  const el = document.getElementById('toast');
  el.textContent = (type === 'success' ? '✓ ' : '✗ ') + msg;
  el.className = 'show ' + type;
  setTimeout(() => el.className = '', 3000);
}

// ── Fetch helpers ──────────────────────────────
async function api(path, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ── Category badge ─────────────────────────────
function badge(cat) {
  const map = { 'Electronics': 'elec', 'Home Goods': 'home', 'Apparel': 'app' };
  const cls = map[cat] || 'other';
  return `<span class="badge badge-${cls}">${cat || '—'}</span>`;
}

// ── Member badge ───────────────────────────────
function memberBadge(type) {
  if (type === 'Gold') return `<span class="badge badge-gold">Gold</span>`;
  return `<span class="badge badge-regular">${type || 'Regular'}</span>`;
}

// ── Format currency ────────────────────────────
const fmt = v => '$' + Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 });


// ══════════════════════════════════════════════
//  KPIs
// ══════════════════════════════════════════════
async function loadKPIs() {
  const d = await api('/analytics/kpis');
  document.getElementById('kpi-revenue').textContent = fmt(d.total_revenue);
  document.getElementById('kpi-sales').textContent = d.total_sales;
  document.getElementById('kpi-avg').textContent = fmt(d.avg_order_value);
  document.getElementById('kpi-customers').textContent = d.total_customers;
  document.getElementById('kpi-products').textContent = d.total_products;
}


// ══════════════════════════════════════════════
//  CHARTS
// ══════════════════════════════════════════════
const ACCENT = ['#ec4899', '#3b82f6', '#a855f7', '#f43f5e', '#3ddc84'];

async function loadCharts() {
  const catData = await api('/analytics/revenue-by-category');

  if (chartCategory) chartCategory.destroy();
  if (chartDoughnut) chartDoughnut.destroy();
  if (chartPie) chartPie.destroy();

  Chart.defaults.color = '#94a3b8';
  Chart.defaults.font = { family: "'JetBrains Mono', monospace", size: 11 };

  // 1. Bar Chart
  chartCategory = new Chart(document.getElementById('chartCategory'), {
    type: 'bar',
    data: {
      labels: catData.map(r => r.category),
      datasets: [{
        data: catData.map(r => r.total_revenue),
        backgroundColor: ACCENT.map(c => c + 'CC'),
        borderColor: ACCENT,
        borderWidth: 1,
        borderRadius: 4,
        barThickness: 20
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8', callback: v => '$' + v } },
      }
    }
  });

  // 2. Doughnut Chart
  chartDoughnut = new Chart(document.getElementById('chartDoughnut'), {
    type: 'doughnut',
    data: {
      labels: catData.map(r => r.category),
      datasets: [{
        data: catData.map(r => r.total_revenue),
        backgroundColor: ACCENT,
        borderWidth: 0,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: { position: 'right', labels: { usePointStyle: true, boxWidth: 8, padding: 14 } }
      }
    }
  });

  // 3. Pie Chart — Member type split
  let goldCount = 0, regularCount = 0;
  customers.forEach(c => {
    if (c.member_type === 'Gold') goldCount++;
    else regularCount++;
  });
  if (goldCount === 0 && regularCount === 0) { goldCount = 1; regularCount = 1; }

  chartPie = new Chart(document.getElementById('chartPie'), {
    type: 'pie',
    data: {
      labels: ['Gold Members', 'Regular Members'],
      datasets: [{
        data: [goldCount, regularCount],
        backgroundColor: ['#fbbf24', '#64748b'],
        borderWidth: 0,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { usePointStyle: true, boxWidth: 8, padding: 14 } }
      }
    }
  });
}


// ══════════════════════════════════════════════
//  AUTO-CALCULATE SALE AMOUNT
// ══════════════════════════════════════════════
function calcSaleAmount() {
  const sel = document.getElementById('sale-product');
  const selectedOption = sel.options[sel.selectedIndex];
  const price = parseFloat(selectedOption?.getAttribute('data-price') || 0);
  const qty = parseInt(document.getElementById('sale-qty').value) || 0;
  const total = price * qty;
  document.getElementById('sale-amount').value = total > 0 ? total.toFixed(2) : '';
}


// ══════════════════════════════════════════════
//  SALES
// ══════════════════════════════════════════════
async function loadSales() {
  sales = await api('/sales');
  const tbody = document.getElementById('sales-tbody');
  document.getElementById('sales-count').textContent = sales.length + ' records';

  if (!sales.length) {
    tbody.innerHTML = `<tr><td colspan="9"><div class="empty"><div class="empty-icon">◈</div>No sales yet</div></td></tr>`;
    return;
  }

  tbody.innerHTML = sales.map(s => `
    <tr>
      <td class="td-mono" style="color:var(--muted)">#${s.sale_id}</td>
      <td>${s.customer_name}</td>
      <td>${s.product_name}</td>
      <td>${badge(s.category)}</td>
      <td class="td-mono">${s.sale_date}</td>
      <td class="td-mono">${s.quantity}</td>
      <td class="td-mono">${fmt(s.unit_price || 0)}</td>
      <td class="td-mono" style="color:var(--accent);font-weight:700">${fmt(s.sale_amount)}</td>
      <td><button class="btn btn-danger" onclick="deleteSale(${s.sale_id})">✕</button></td>
    </tr>
  `).join('');
}

async function addSale() {
  const cid = document.getElementById('sale-customer').value;
  const pid = document.getElementById('sale-product').value;
  const date = document.getElementById('sale-date').value;
  const qty = document.getElementById('sale-qty').value;
  const amount = document.getElementById('sale-amount').value;

  if (!cid || !pid || !date || !qty) {
    toast('Please fill all fields', 'error'); return;
  }
  if (!amount || parseFloat(amount) <= 0) {
    toast('Select a product with a valid price', 'error'); return;
  }

  try {
    await api('/sales', 'POST', {
      customer_id: +cid, product_id: +pid,
      sale_date: date, quantity: +qty, sale_amount: +amount,
    });
    toast('Sale added');
    document.getElementById('sale-date').value = '';
    document.getElementById('sale-qty').value = 1;
    document.getElementById('sale-amount').value = '';
    await Promise.all([loadSales(), loadKPIs(), loadCharts()]);
  } catch (e) { toast('Error: ' + e.message, 'error'); }
}

async function deleteSale(id) {
  if (!confirm('Delete this sale?')) return;
  try {
    await api('/sales/' + id, 'DELETE');
    toast('Sale deleted');
    await Promise.all([loadSales(), loadKPIs(), loadCharts()]);
  } catch (e) { toast('Error: ' + e.message, 'error'); }
}


// ══════════════════════════════════════════════
//  CUSTOMERS
// ══════════════════════════════════════════════
async function loadCustomers() {
  customers = await api('/customers');
  const tbody = document.getElementById('customers-tbody');
  document.getElementById('customers-count').textContent = customers.length + ' records';

  const sel = document.getElementById('sale-customer');
  sel.innerHTML = customers.map(c =>
    `<option value="${c.customer_id}">${c.first_name} ${c.last_name}</option>`
  ).join('');

  if (!customers.length) {
    tbody.innerHTML = `<tr><td colspan="9"><div class="empty"><div class="empty-icon">◉</div>No customers yet</div></td></tr>`;
    return;
  }

  tbody.innerHTML = customers.map(c => `
    <tr>
      <td class="td-mono" style="color:var(--muted)">${c.customer_id}</td>
      <td>${c.first_name}</td>
      <td>${c.last_name}</td>
      <td>${c.city || '—'}</td>
      <td class="td-mono">${c.mobile_no || '—'}</td>
      <td>${c.email || '—'}</td>
      <td>${c.region || '—'}</td>
      <td>${memberBadge(c.member_type)}</td>
      <td>
        <div class="action-btns">
          <button class="btn btn-edit" onclick="editCustomer(${c.customer_id})">✎ Edit</button>
          <button class="btn btn-danger" onclick="deleteCustomer(${c.customer_id})">✕</button>
        </div>
      </td>
    </tr>
  `).join('');
}

async function submitCustomer() {
  const editId = document.getElementById('cust-edit-id').value;

  const first = document.getElementById('cust-first').value.trim();
  const last = document.getElementById('cust-last').value.trim();
  const city = document.getElementById('cust-city').value.trim();
  const mobile = document.getElementById('cust-mobile').value.trim();
  const email = document.getElementById('cust-email').value.trim();
  const region = document.getElementById('cust-region').value;
  const member = document.getElementById('cust-member').value;

  if (!first || !last) { toast('First and last name required', 'error'); return; }

  const payload = {
    first_name: first,
    last_name: last,
    city: city,
    mobile_no: mobile,
    email: email,
    region: region,
    member_type: member
  };

  try {
    if (editId) {
      await api('/customers/' + editId, 'PUT', payload);
      toast('Customer updated successfully');
    } else {
      await api('/customers', 'POST', payload);
      toast('Customer added successfully');
    }
    cancelCustomerEdit();
    await Promise.all([loadCustomers(), loadKPIs(), loadCharts()]);
  } catch (e) { toast('Error: ' + e.message, 'error'); }
}

function editCustomer(id) {
  const c = customers.find(x => x.customer_id === id);
  if (!c) return;

  document.getElementById('cust-first').value = c.first_name || '';
  document.getElementById('cust-last').value = c.last_name || '';
  document.getElementById('cust-city').value = c.city || '';
  document.getElementById('cust-mobile').value = c.mobile_no || '';
  document.getElementById('cust-email').value = c.email || '';
  document.getElementById('cust-region').value = c.region || '';
  document.getElementById('cust-member').value = c.member_type || 'Regular';

  document.getElementById('cust-edit-id').value = id;

  document.getElementById('customer-form-title').textContent = '✎ Editing Customer #' + id;
  document.getElementById('cust-submit-btn').textContent = '✓ Update Customer';
  document.getElementById('cust-submit-btn').className = 'btn btn-update';
  document.getElementById('cust-cancel-btn').style.display = 'inline-flex';
  document.getElementById('customer-form-panel').classList.add('editing');

  document.getElementById('customer-form-panel').scrollIntoView({ behavior: 'smooth' });
}

function cancelCustomerEdit() {
  document.getElementById('cust-edit-id').value = '';
  ['cust-first', 'cust-last', 'cust-city', 'cust-mobile', 'cust-email'].forEach(id =>
    document.getElementById(id).value = ''
  );
  document.getElementById('cust-region').value = '';
  document.getElementById('cust-member').value = 'Regular';

  document.getElementById('customer-form-title').textContent = 'Add Customer';
  document.getElementById('cust-submit-btn').textContent = '+ Add Customer';
  document.getElementById('cust-submit-btn').className = 'btn btn-primary';
  document.getElementById('cust-cancel-btn').style.display = 'none';
  document.getElementById('customer-form-panel').classList.remove('editing');
}

async function deleteCustomer(id) {
  if (!confirm('Delete this customer and all their sales?')) return;
  try {
    await api('/customers/' + id, 'DELETE');
    toast('Customer deleted');
    cancelCustomerEdit();
    await Promise.all([loadCustomers(), loadSales(), loadKPIs(), loadCharts()]);
  } catch (e) { toast('Error: ' + e.message, 'error'); }
}


// ══════════════════════════════════════════════
//  PRODUCTS
// ══════════════════════════════════════════════
async function loadProducts() {
  products = await api('/products');
  const tbody = document.getElementById('products-tbody');
  document.getElementById('products-count').textContent = products.length + ' records';

  // Populate sales dropdown with price data
  const sel = document.getElementById('sale-product');
  sel.innerHTML = products.map(p =>
    `<option value="${p.product_id}" data-price="${p.unit_price || 0}">${p.product_name} — ${fmt(p.unit_price || 0)}</option>`
  ).join('');

  // Attach auto-calculate listeners
  sel.removeEventListener('change', calcSaleAmount);
  sel.addEventListener('change', calcSaleAmount);

  if (!products.length) {
    tbody.innerHTML = `<tr><td colspan="5"><div class="empty"><div class="empty-icon">◇</div>No products yet</div></td></tr>`;
    return;
  }

  tbody.innerHTML = products.map(p => `
    <tr>
      <td class="td-mono" style="color:var(--muted)">${p.product_id}</td>
      <td>${p.product_name}</td>
      <td>${badge(p.category)}</td>
      <td class="td-mono" style="color:var(--accent)">${fmt(p.unit_price || 0)}</td>
      <td>
        <div class="action-btns">
          <button class="btn btn-edit" onclick="editProduct(${p.product_id})">✎ Edit</button>
          <button class="btn btn-danger" onclick="deleteProduct(${p.product_id})">✕</button>
        </div>
      </td>
    </tr>
  `).join('');

  // Trigger initial calculation
  calcSaleAmount();
}

async function submitProduct() {
  const editId = document.getElementById('prod-edit-id').value;

  const name = document.getElementById('prod-name').value.trim();
  const cat = document.getElementById('prod-category').value;
  const price = document.getElementById('prod-price').value;

  if (!name) { toast('Product name required', 'error'); return; }
  if (!price || parseFloat(price) < 0) { toast('Valid price required', 'error'); return; }

  const payload = { product_name: name, category: cat, unit_price: parseFloat(price) };

  try {
    if (editId) {
      await api('/products/' + editId, 'PUT', payload);
      toast('Product updated successfully');
    } else {
      await api('/products', 'POST', payload);
      toast('Product added successfully');
    }
    cancelProductEdit();
    await Promise.all([loadProducts(), loadKPIs(), loadCharts()]);
  } catch (e) { toast('Error: ' + e.message, 'error'); }
}

function editProduct(id) {
  const p = products.find(x => x.product_id === id);
  if (!p) return;

  document.getElementById('prod-name').value = p.product_name || '';
  document.getElementById('prod-category').value = p.category || 'Other';
  document.getElementById('prod-price').value = p.unit_price || '';
  document.getElementById('prod-edit-id').value = id;

  document.getElementById('product-form-title').textContent = '✎ Editing Product #' + id;
  document.getElementById('prod-submit-btn').textContent = '✓ Update Product';
  document.getElementById('prod-submit-btn').className = 'btn btn-update';
  document.getElementById('prod-cancel-btn').style.display = 'inline-flex';
  document.getElementById('product-form-panel').classList.add('editing');

  document.getElementById('product-form-panel').scrollIntoView({ behavior: 'smooth' });
}

function cancelProductEdit() {
  document.getElementById('prod-edit-id').value = '';
  document.getElementById('prod-name').value = '';
  document.getElementById('prod-price').value = '';
  document.getElementById('prod-category').value = 'Electronics';

  document.getElementById('product-form-title').textContent = 'Add Product';
  document.getElementById('prod-submit-btn').textContent = '+ Add Product';
  document.getElementById('prod-submit-btn').className = 'btn btn-primary';
  document.getElementById('prod-cancel-btn').style.display = 'none';
  document.getElementById('product-form-panel').classList.remove('editing');
}

async function deleteProduct(id) {
  if (!confirm('Delete this product and all related sales?')) return;
  try {
    await api('/products/' + id, 'DELETE');
    toast('Product deleted');
    cancelProductEdit();
    await Promise.all([loadProducts(), loadSales(), loadKPIs(), loadCharts()]);
  } catch (e) { toast('Error: ' + e.message, 'error'); }
}


// ══════════════════════════════════════════════
//  INIT
// ══════════════════════════════════════════════
async function refreshAll() {
  try {
    await Promise.all([
      loadCustomers(), loadProducts(), loadSales()
    ]);
    await Promise.all([loadKPIs(), loadCharts()]);
    toast('Data refreshed');
  } catch (e) {
    toast('Cannot reach API — is Flask running?', 'error');
    document.querySelector('.status-dot').style.background = '#ff6b6b';
    document.querySelector('.status-dot').style.boxShadow = '0 0 8px #ff6b6b';
  }
}

// Set today as default date
document.getElementById('sale-date').valueAsDate = new Date();

// Listen for quantity changes to auto-calculate
document.getElementById('sale-qty').addEventListener('input', calcSaleAmount);

// Start
refreshAll();