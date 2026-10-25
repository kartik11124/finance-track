/**
 * Smart Personal Finance & Budget Management System
 * Core UI interactions, Theme Management (Dark/Light mode), and Dynamic Budget Calculations
 */

// Initialize Theme immediately to prevent flash of wrong theme
(function initTheme() {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    document.documentElement.setAttribute("data-theme", savedTheme);
  } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    document.documentElement.setAttribute("data-theme", "dark");
  } else {
    document.documentElement.setAttribute("data-theme", "light");
  }
})();

document.addEventListener("DOMContentLoaded", function () {
  // 1. Theme Toggle Setup
  const themeToggle = document.getElementById("themeToggle");
  const themeIcon = document.getElementById("themeIcon");

  function updateThemeIcon() {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
    if (themeIcon) {
      themeIcon.textContent = currentTheme === "dark" ? "☀️" : "🌙";
      themeToggle.setAttribute("title", currentTheme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode");
    }
  }

  updateThemeIcon();

  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
      const newTheme = currentTheme === "dark" ? "light" : "dark";

      document.documentElement.setAttribute("data-theme", newTheme);
      localStorage.setItem("theme", newTheme);
      updateThemeIcon();

      // Trigger custom event so Chart.js charts can adapt if needed
      window.dispatchEvent(new CustomEvent("themeChanged", { detail: { theme: newTheme } }));
    });
  }

  // 2. Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(function (alert) {
    const closeBtn = alert.querySelector(".alert-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 250);
      });
    }
    setTimeout(function () {
      alert.style.transition = "opacity 0.5s ease";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 500);
    }, 6000);
  });

  // 3. Client-side input validation for amounts (No negative numbers)
  const amountInputs = document.querySelectorAll('input[type="number"][name*="amount"], input[name="target_amount"], input[name="current_amount"], input[name="monthly_income"]');
  amountInputs.forEach(function (input) {
    input.addEventListener("input", function () {
      if (parseFloat(this.value) < 0) {
        this.value = "0";
      }
    });
  });

  // 4. Confirmation on delete actions
  const deleteForms = document.querySelectorAll('form[action*="delete"]');
  deleteForms.forEach(function (form) {
    form.addEventListener("submit", function (e) {
      const confirmed = confirm("Are you sure you want to delete this record? This action cannot be undone.");
      if (!confirmed) {
        e.preventDefault();
      }
    });
  });

  // 5. Smart Budget Allocation Mode Switcher (Algorithmic vs Custom)
  const modeTabs = document.querySelectorAll(".mode-tab-btn");
  const modeContents = document.querySelectorAll(".budget-mode-content");

  if (modeTabs.length > 0) {
    modeTabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        modeTabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");

        const targetMode = tab.getAttribute("data-target");
        modeContents.forEach(function (content) {
          if (content.id === targetMode) {
            content.style.display = "block";
          } else {
            content.style.display = "none";
          }
        });
      });
    });
  }

  // 6. Live Custom Budget Allocation Calculator
  const customInputs = document.querySelectorAll(".custom-budget-input");
  const customTotalEl = document.getElementById("customTotalAllocated");
  const customRemainingEl = document.getElementById("customRemainingBalance");
  const baseIncomeEl = document.getElementById("smartBaseIncome");

  function recalculateCustomBudget() {
    if (!customTotalEl || !baseIncomeEl) return;
    const baseIncome = parseFloat(baseIncomeEl.value) || 0;
    let allocatedSum = 0;

    customInputs.forEach(function (inp) {
      const val = parseFloat(inp.value) || 0;
      allocatedSum += val;
    });

    const remaining = baseIncome - allocatedSum;
    customTotalEl.textContent = "₹" + allocatedSum.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    
    if (customRemainingEl) {
      customRemainingEl.textContent = "₹" + remaining.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      if (remaining < 0) {
        customRemainingEl.style.color = "#ef4444";
      } else {
        customRemainingEl.style.color = "#10b981";
      }
    }
  }

  customInputs.forEach(function (inp) {
    inp.addEventListener("input", recalculateCustomBudget);
  });

  // 7. More Dropdown Menu Handler
  const moreDropdown = document.getElementById("moreDropdown");
  const moreDropdownBtn = document.getElementById("moreDropdownBtn");

  if (moreDropdown && moreDropdownBtn) {
    moreDropdownBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      const isOpen = moreDropdown.classList.contains("open");
      if (isOpen) {
        moreDropdown.classList.remove("open");
        moreDropdownBtn.setAttribute("aria-expanded", "false");
      } else {
        moreDropdown.classList.add("open");
        moreDropdownBtn.setAttribute("aria-expanded", "true");
      }
    });

    // Close when clicking anywhere outside
    document.addEventListener("click", function (e) {
      if (!moreDropdown.contains(e.target)) {
        moreDropdown.classList.remove("open");
        moreDropdownBtn.setAttribute("aria-expanded", "false");
      }
    });

    // Close on Escape key
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && moreDropdown.classList.contains("open")) {
        moreDropdown.classList.remove("open");
        moreDropdownBtn.setAttribute("aria-expanded", "false");
      }
    });
  }

  // 8. Mobile Navigation Drawer Toggle
  const mobileNavToggle = document.getElementById("mobileNavToggle");
  const mainNavLinks = document.getElementById("mainNavLinks");

  if (mobileNavToggle && mainNavLinks) {
    mobileNavToggle.addEventListener("click", function (e) {
      e.stopPropagation();
      mainNavLinks.classList.toggle("mobile-open");
    });

    // Close mobile nav when clicking outside
    document.addEventListener("click", function (e) {
      if (!mainNavLinks.contains(e.target) && !mobileNavToggle.contains(e.target)) {
        mainNavLinks.classList.remove("mobile-open");
      }
    });
  }
});
