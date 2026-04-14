window.renderFinanceChart = function renderFinanceChart(chartData) {
    const canvas = document.getElementById("financeChart");
    if (!canvas || !chartData) return;

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: chartData.labels,
            datasets: [
                { label: "Receitas", data: chartData.revenues, backgroundColor: "#0f766e", borderRadius: 6 },
                { label: "Despesas", data: chartData.expenses, backgroundColor: "#f97316", borderRadius: 6 },
                { label: "Saldo", data: chartData.balances, type: "line", borderColor: "#1d4ed8", tension: 0.3 },
            ],
        },
        options: {
            responsive: true,
            plugins: { legend: { position: "bottom" } },
        },
    });
};
