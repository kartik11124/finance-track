/**
 * Charts module for Smart Personal Finance & Budget Management System
 * Renders real backend-computed metrics using Chart.js with pure canvas fallback.
 * Automatically adapts styling to Dark Mode and Light Mode.
 */

const activeChartInstances = {};

function getThemeChartColors() {
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  return {
    textColor: isDark ? "#94a3b8" : "#64748b",
    gridColor: isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)",
    borderColor: isDark ? "#131b2e" : "#ffffff",
  };
}

function applyThemeToCharts() {
  if (typeof Chart === "undefined") return;
  const theme = getThemeChartColors();
  Chart.defaults.color = theme.textColor;
  Chart.defaults.borderColor = theme.gridColor;

  Object.values(activeChartInstances).forEach((chart) => {
    if (chart && typeof chart.update === "function") {
      if (chart.options.scales) {
        Object.values(chart.options.scales).forEach((scale) => {
          if (scale.ticks) scale.ticks.color = theme.textColor;
          if (scale.grid) scale.grid.color = theme.gridColor;
        });
      }
      chart.update();
    }
  });
}

window.addEventListener("themeChanged", function () {
  applyThemeToCharts();
});

function initFinanceCharts(chartData) {
  if (!chartData || typeof Chart === "undefined") return;

  const theme = getThemeChartColors();
  Chart.defaults.color = theme.textColor;
  Chart.defaults.borderColor = theme.gridColor;

  // 1. Income vs Expenses Chart
  const ctxCashFlow = document.getElementById("cashFlowChart");
  if (ctxCashFlow) {
    if (activeChartInstances.cashFlow) activeChartInstances.cashFlow.destroy();
    activeChartInstances.cashFlow = new Chart(ctxCashFlow, {
      type: "bar",
      data: {
        labels: ["Total Income", "Total Expenses", "Net Savings"],
        datasets: [
          {
            label: "Amount (₹)",
            data: [chartData.income || 0, chartData.expenses || 0, Math.max(0, chartData.savings || 0)],
            backgroundColor: ["#10b981", "#ef4444", "#3b82f6"],
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ₹${ctx.raw.toLocaleString("en-IN")}`,
            },
          },
        },
        scales: {
          x: {
            grid: { color: theme.gridColor },
            ticks: { color: theme.textColor },
          },
          y: {
            beginAtZero: true,
            grid: { color: theme.gridColor },
            ticks: {
              color: theme.textColor,
              callback: (val) => "₹" + val.toLocaleString("en-IN"),
            },
          },
        },
      },
    });
  }

  // 2. Expense Category Breakdown Chart
  const ctxCategory = document.getElementById("categoryChart");
  if (ctxCategory && chartData.category_labels && chartData.category_labels.length > 0) {
    if (activeChartInstances.category) activeChartInstances.category.destroy();
    activeChartInstances.category = new Chart(ctxCategory, {
      type: "doughnut",
      data: {
        labels: chartData.category_labels,
        datasets: [
          {
            data: chartData.category_values,
            backgroundColor: [
              "#3b82f6",
              "#10b981",
              "#f59e0b",
              "#ef4444",
              "#8b5cf6",
              "#ec4899",
              "#06b6d4",
              "#64748b",
              "#14b8a6",
            ],
            borderWidth: 2,
            borderColor: theme.borderColor,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "right",
            labels: { boxWidth: 12, font: { size: 11 }, color: theme.textColor },
          },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ₹${ctx.raw.toLocaleString("en-IN")}`,
            },
          },
        },
      },
    });
  }

  // 3. Budget Utilization Comparison Chart
  const ctxBudget = document.getElementById("budgetChart");
  if (ctxBudget && chartData.budget_labels && chartData.budget_labels.length > 0) {
    if (activeChartInstances.budget) activeChartInstances.budget.destroy();
    activeChartInstances.budget = new Chart(ctxBudget, {
      type: "bar",
      data: {
        labels: chartData.budget_labels,
        datasets: [
          {
            label: "Budgeted (₹)",
            data: chartData.budget_allocated,
            backgroundColor: "#64748b",
            borderRadius: 4,
          },
          {
            label: "Actual Spent (₹)",
            data: chartData.budget_spent,
            backgroundColor: "#ef4444",
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { color: theme.textColor } },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ₹${ctx.raw.toLocaleString("en-IN")}`,
            },
          },
        },
        scales: {
          x: {
            grid: { color: theme.gridColor },
            ticks: { color: theme.textColor },
          },
          y: {
            beginAtZero: true,
            grid: { color: theme.gridColor },
            ticks: {
              color: theme.textColor,
              callback: (val) => "₹" + val.toLocaleString("en-IN"),
            },
          },
        },
      },
    });
  }
}

/**
 * Initializes the Smart Budget Allocation summary doughnut chart
 */
function initAllocationChart(allocationData) {
  if (!allocationData || typeof Chart === "undefined") return;
  const ctx = document.getElementById("smartAllocationChart");
  if (!ctx) return;

  const theme = getThemeChartColors();
  if (activeChartInstances.allocation) activeChartInstances.allocation.destroy();

  activeChartInstances.allocation = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Essential Needs", "Lifestyle Wants", "Wealth & Investments"],
      datasets: [
        {
          data: [
            allocationData.needs_total || 0,
            allocationData.wants_total || 0,
            allocationData.invest_total || 0,
          ],
          backgroundColor: ["#3b82f6", "#f59e0b", "#10b981"],
          borderWidth: 2,
          borderColor: theme.borderColor,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: theme.textColor, boxWidth: 12 },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ₹${ctx.raw.toLocaleString("en-IN")}`,
          },
        },
      },
    },
  });
}
