const API = '/api' // proxy prefix — served directly from FastAPI, no prefix needed
const BASE = ''

let token = localStorage.getItem('token') || null

// --- API helpers ---
async function api(method, path, body) {
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (res.status === 204) return null
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Request failed')
  return data
}

async function apiForm(path, formData) {
  const headers = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(BASE + path, { method: 'POST', headers, body: formData })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Login failed')
  return data
}

// --- DOM refs ---
const navUserName = document.getElementById('nav-user-name')
const btnLogout = document.getElementById('btn-logout')
const btnShowLogin = document.getElementById('btn-show-login')
const btnShowRegister = document.getElementById('btn-show-register')
const btnCart = document.getElementById('btn-cart')
const cartCount = document.getElementById('cart-count')
const modalOverlay = document.getElementById('modal-overlay')
const modalClose = document.getElementById('modal-close')
const formLogin = document.getElementById('form-login')
const formRegister = document.getElementById('form-register')
const sectionProducts = document.getElementById('section-products')
const sectionCart = document.getElementById('section-cart')
const sectionOrders = document.getElementById('section-orders')

// --- Auth state ---
async function applyAuthState() {
  if (!token) {
    navUserName.textContent = ''
    btnLogout.classList.add('hidden')
    btnShowLogin.classList.remove('hidden')
    btnShowRegister.classList.remove('hidden')
    cartCount.textContent = '0'
    return
  }
  try {
    const me = await api('GET', '/auth/me')
    navUserName.textContent = me.full_name
    btnLogout.classList.remove('hidden')
    btnShowLogin.classList.add('hidden')
    btnShowRegister.classList.add('hidden')
    refreshCartCount()
  } catch {
    token = null
    localStorage.removeItem('token')
    applyAuthState()
  }
}

async function refreshCartCount() {
  if (!token) return
  try {
    const cart = await api('GET', '/cart')
    cartCount.textContent = cart.items.length
  } catch { /* ignore */ }
}

// --- Show/hide sections ---
function showSection(name) {
  sectionProducts.classList.add('hidden')
  sectionCart.classList.add('hidden')
  sectionOrders.classList.add('hidden')
  if (name === 'products') sectionProducts.classList.remove('hidden')
  if (name === 'cart') sectionCart.classList.remove('hidden')
  if (name === 'orders') sectionOrders.classList.remove('hidden')
}

// --- Products ---
async function loadProducts() {
  const search = document.getElementById('search-input').value
  const category = document.getElementById('category-filter').value
  let url = '/products'
  const params = []
  if (search) params.push(`search=${encodeURIComponent(search)}`)
  if (category) params.push(`category=${encodeURIComponent(category)}`)
  if (params.length) url += '?' + params.join('&')

  const products = await api('GET', url)
  const grid = document.getElementById('product-grid')
  grid.innerHTML = ''
  products.forEach(p => {
    const card = document.createElement('div')
    card.className = 'product-card'
    card.dataset.testid = `product-card-${p.id}`
    card.innerHTML = `
      <span class="category">${p.category}</span>
      <h3>${p.name}</h3>
      <p class="desc">${p.description}</p>
      <span class="price">$${p.price.toFixed(2)}</span>
      <span class="stock">In stock: ${p.stock}</span>
      <button data-id="${p.id}" data-testid="add-to-cart-${p.id}">Add to cart</button>
    `
    card.querySelector('button').addEventListener('click', () => addToCart(p.id))
    grid.appendChild(card)
  })
}

async function loadCategories() {
  const categories = await api('GET', '/products/categories')
  const select = document.getElementById('category-filter')
  categories.forEach(c => {
    const opt = document.createElement('option')
    opt.value = c
    opt.textContent = c.charAt(0).toUpperCase() + c.slice(1)
    select.appendChild(opt)
  })
}

async function addToCart(productId) {
  if (!token) { openModal('login'); return }
  try {
    await api('POST', '/cart/items', { product_id: productId, quantity: 1 })
    refreshCartCount()
  } catch (e) {
    alert(e.message)
  }
}

// --- Cart ---
async function loadCart() {
  showSection('cart')
  const cart = await api('GET', '/cart')
  cartCount.textContent = cart.items.length

  const cartItemsEl = document.getElementById('cart-items')
  cartItemsEl.innerHTML = ''
  if (!cart.items.length) {
    cartItemsEl.innerHTML = '<p>Your cart is empty.</p>'
    document.getElementById('cart-total').textContent = ''
    return
  }
  cart.items.forEach(item => {
    const row = document.createElement('div')
    row.className = 'cart-item'
    row.innerHTML = `
      <span>${item.product_name}</span>
      <span>Qty: ${item.quantity}</span>
      <span class="subtotal">$${item.subtotal.toFixed(2)}</span>
      <button data-testid="remove-${item.product_id}">Remove</button>
    `
    row.querySelector('button').addEventListener('click', () => removeFromCart(item.product_id))
    cartItemsEl.appendChild(row)
  })
  document.getElementById('cart-total').textContent = `Total: $${cart.total.toFixed(2)}`

  const msg = document.getElementById('checkout-msg')
  msg.classList.add('hidden')
}

async function removeFromCart(productId) {
  await api('DELETE', `/cart/items/${productId}`)
  loadCart()
}

// --- Checkout ---
async function checkout() {
  try {
    const order = await api('POST', '/orders')
    const msg = document.getElementById('checkout-msg')
    msg.textContent = `Order #${order.id.slice(0, 8)} placed! Total: $${order.total.toFixed(2)}`
    msg.className = 'success'
    msg.classList.remove('hidden')
    loadCart()
    refreshCartCount()
  } catch (e) {
    alert(e.message)
  }
}

// --- Orders ---
async function loadOrders() {
  if (!token) { openModal('login'); return }
  showSection('orders')
  const orders = await api('GET', '/orders')
  const list = document.getElementById('orders-list')
  list.innerHTML = ''
  if (!orders.length) { list.innerHTML = '<p>No orders yet.</p>'; return }
  orders.forEach(o => {
    const card = document.createElement('div')
    card.className = 'order-card'
    card.dataset.testid = `order-${o.id}`
    card.innerHTML = `
      <h3>Order #${o.id.slice(0, 8)} &nbsp; <span class="order-status">${o.status}</span></h3>
      ${o.items.map(i => `<div class="order-item">${i.product_name} × ${i.quantity} — $${i.subtotal.toFixed(2)}</div>`).join('')}
      <div class="order-total">Total: $${o.total.toFixed(2)}</div>
    `
    list.appendChild(card)
  })
}

// --- Modal ---
function openModal(form) {
  modalOverlay.classList.remove('hidden')
  if (form === 'login') {
    formLogin.classList.remove('hidden')
    formRegister.classList.add('hidden')
  } else {
    formLogin.classList.add('hidden')
    formRegister.classList.remove('hidden')
  }
}
function closeModal() { modalOverlay.classList.add('hidden') }

// --- Login ---
document.getElementById('btn-login').addEventListener('click', async () => {
  const email = document.getElementById('login-email').value
  const password = document.getElementById('login-password').value
  const errEl = document.getElementById('login-error')
  errEl.classList.add('hidden')
  try {
    const form = new FormData()
    form.append('username', email)
    form.append('password', password)
    const data = await apiForm('/auth/login', form)
    token = data.access_token
    localStorage.setItem('token', token)
    closeModal()
    applyAuthState()
    loadProducts()
  } catch (e) {
    errEl.textContent = e.message
    errEl.classList.remove('hidden')
  }
})

// --- Register ---
document.getElementById('btn-register').addEventListener('click', async () => {
  const full_name = document.getElementById('reg-name').value
  const email = document.getElementById('reg-email').value
  const password = document.getElementById('reg-password').value
  const errEl = document.getElementById('register-error')
  const successEl = document.getElementById('register-success')
  errEl.classList.add('hidden')
  successEl.classList.add('hidden')
  try {
    await api('POST', '/auth/register', { full_name, email, password })
    successEl.textContent = 'Account created! You can now log in.'
    successEl.classList.remove('hidden')
  } catch (e) {
    errEl.textContent = e.message
    errEl.classList.remove('hidden')
  }
})

// --- Event wiring ---
btnShowLogin.addEventListener('click', () => openModal('login'))
btnShowRegister.addEventListener('click', () => openModal('register'))
modalClose.addEventListener('click', closeModal)
modalOverlay.addEventListener('click', e => { if (e.target === modalOverlay) closeModal() })

btnLogout.addEventListener('click', () => {
  token = null
  localStorage.removeItem('token')
  applyAuthState()
  showSection('products')
})

btnCart.addEventListener('click', () => {
  if (!token) { openModal('login'); return }
  loadCart()
})

document.getElementById('btn-checkout').addEventListener('click', checkout)

document.getElementById('search-input').addEventListener('input', loadProducts)
document.getElementById('category-filter').addEventListener('change', loadProducts)

// Add orders nav link dynamically
const ordersBtn = document.createElement('button')
ordersBtn.textContent = 'Orders'
ordersBtn.className = 'secondary'
ordersBtn.id = 'btn-orders'
ordersBtn.addEventListener('click', loadOrders)
document.getElementById('nav-auth').appendChild(ordersBtn)

// --- Init ---
showSection('products')
loadCategories()
loadProducts()
applyAuthState()
