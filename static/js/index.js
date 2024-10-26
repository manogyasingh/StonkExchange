let currentSymbol = document.getElementById('stockSelect').value;

function updateOrderbook(orderbook) {
    function createTable(orders) {
        return `<table>
            <tr><th>Price</th><th>Quantity</th><th>User</th></tr>
            ${orders.map(([price, qty, user]) => 
                `<tr><td>$${price}</td><td>${qty}</td><td>${user}</td></tr>`
            ).join('')}
        </table>`;
    }

    document.getElementById('bidsTable').innerHTML = createTable(orderbook.bids);
    document.getElementById('asksTable').innerHTML = createTable(orderbook.asks);
}

function updatePortfolio(user) {
    document.getElementById('userBalance').textContent = user.balance.toFixed(2);
    for (const [symbol, quantity] of Object.entries(user.stocks)) {
        const element = document.getElementById(`stock-${symbol}`);
        if (element) element.textContent = quantity;
    }
}

document.getElementById('stockSelect').onchange = (e) => {
    currentSymbol = e.target.value;
    updateOrderbook(orderbooks[currentSymbol]);
};

document.getElementById('orderForm').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
        const response = await fetch('/place_order', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.status === 'success') {
            orderbooks[currentSymbol] = data.orderbook;
            updateOrderbook(data.orderbook);
            updatePortfolio(data.user);
            e.target.reset();
            document.getElementById('stockSelect').value = currentSymbol;
        } else {
            alert(data.message);
        }
    } catch (error) {
        alert('Error placing order');
    }
};

// Initial orderbook update
updateOrderbook(orderbooks[currentSymbol]);
