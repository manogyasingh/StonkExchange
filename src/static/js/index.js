// Cache DOM elements
const orderForm = document.getElementById('orderForm');
const stockSelect = document.getElementById('stockSelect');
const bidsTable = document.getElementById('bidsTable');
const asksTable = document.getElementById('asksTable');
const userBalance = document.getElementById('userBalance');

let currentSymbol = stockSelect?.value || '';
let charts = {};

// Utility functions
const formatPrice = (price) => `$${parseFloat(price).toFixed(2)}`;
const formatDate = (date) => new Date(date).toLocaleString();

function showMessage(message, type = 'error') {
    const existingMessage = document.querySelector('.message');
    if (existingMessage) {
        existingMessage.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.textContent = message;
    orderForm.insertAdjacentElement('beforebegin', messageDiv);

    setTimeout(() => messageDiv.remove(), 5000);
}

function createTable(orders) {
    if (!orders || !orders.length) {
        return '<p class="text-center">No orders</p>';
    }

    return `<table>
        <tr><th>Price</th><th>Quantity</th><th>User</th></tr>
        ${orders.map(([price, qty, user]) => 
            `<tr>
                <td>${formatPrice(price)}</td>
                <td>${qty}</td>
                <td>${user}</td>
            </tr>`
        ).join('')}
    </table>`;
}

function updateOrderbook(orderbook) {
    if (!orderbook) return;
    
    bidsTable.innerHTML = createTable(orderbook.bids);
    asksTable.innerHTML = createTable(orderbook.asks);
}

function updatePortfolio(user) {
    if (!user) return;

    userBalance.textContent = parseFloat(user.balance).toFixed(2);
    for (const [symbol, quantity] of Object.entries(user.stocks)) {
        const element = document.getElementById(`stock-${symbol}`);
        if (element) {
            element.textContent = quantity;
        }
    }
}

function initializeChart(symbol, priceHistory) {
    const ctx = document.getElementById(`chart-${symbol}`);
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (charts[symbol]) {
        charts[symbol].destroy();
    }

    const data = (priceHistory || []).map(h => ({
        x: new Date(h.time),
        y: h.price
    }));

    charts[symbol] = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Price',
                data: data,
                borderColor: '#1a73e8',
                tension: 0.1,
                pointRadius: 2,
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 0 // Disable animation for better performance
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        }
                    },
                    ticks: {
                        maxTicksLimit: 6
                    }
                },
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: value => formatPrice(value)
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: context => formatPrice(context.parsed.y)
                    }
                }
            }
        }
    });
}

function updateChart(symbol, priceHistory) {
    if (!charts[symbol] || !priceHistory) return;

    const data = priceHistory.slice(-60).map(h => ({
        x: new Date(h.time),
        y: h.price
    }));

    charts[symbol].data.datasets[0].data = data;
    charts[symbol].update('none'); // Update without animation
}

// Event Listeners
stockSelect?.addEventListener('change', (e) => {
    currentSymbol = e.target.value;
    updateOrderbook(orderbooks[currentSymbol] || {bids:[], asks: []});
});

orderForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitButton = orderForm.querySelector('button');
    submitButton.disabled = true;
    orderForm.classList.add('loading');

    try {
        const formData = new FormData(e.target);
        const response = await fetch('/place_order', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            orderbooks[currentSymbol] = data.orderbook;
            updateOrderbook(data.orderbook);
            updatePortfolio(data.user);
            updateChart(currentSymbol, data.price_history);
            priceHistory[currentSymbol] = data.price_history;
            showMessage('Order placed successfully', 'success');
            e.target.reset();
            stockSelect.value = currentSymbol;
        } else {
            showMessage(data.message);
        }
    } catch (error) {
        showMessage('Error placing order. Please try again.');
        console.error('Error:', error);
    } finally {
        submitButton.disabled = false;
        orderForm.classList.remove('loading');
    }
});

// Initialize charts and orderbook on page load
window.addEventListener('load', () => {
    if (priceHistory) {
        Object.keys(priceHistory).forEach(symbol => {
            initializeChart(symbol, priceHistory[symbol]);
        });
    }
    updateOrderbook(orderbooks[currentSymbol] || {bids:[], asks: []});
});

// Handle visibility change to pause/resume chart updates
document.addEventListener('visibilitychange', () => {
    Object.values(charts).forEach(chart => {
        if (document.hidden) {
            chart.stop();
        } else {
            chart.start();
        }
    });
});
