const charts = {};

function initializeChart(symbol, history) {
    const ctx = document.getElementById(`admin-chart-${symbol}`);
    if (!ctx) return;

    if (charts[symbol]) {
        charts[symbol].destroy();
    }

    const chartConfig = {
        type: 'line',
        data: {
            datasets: [{
                label: 'Price',
                data: history.map(h => ({
                    x: new Date(h.time),
                    y: h.price
                })),
                borderColor: '#1a73e8',
                tension: 0.1,
                pointRadius: 2,
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: {
                duration: 0
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
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return '$' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            }
        }
    };

    charts[symbol] = new Chart(ctx, chartConfig);
}

window.addEventListener('load', function() {
    if (typeof priceHistory !== 'undefined') {
        for (const [symbol, history] of Object.entries(priceHistory)) {
            if (history && history.length > 0) {
                initializeChart(symbol, history);
            }
        }
    }
});

document.addEventListener('visibilitychange', function() {
    for (const chart of Object.values(charts)) {
        if (document.hidden) {
            chart.stop();
        } else {
            chart.start();
        }
    }
});
