/**
 * AeroPredict - Frontend Application Logic
 * Fast, responsive interactive search, side-by-side comparisons, and heatmap rendering
 */

document.addEventListener("DOMContentLoaded", () => {
  // Application State
  const state = {
    sourceCity: "Mumbai",
    destinationCity: "Delhi",
    airlineChoice: "BOTH",
    travelDate: "",
    dateFlexibility: 1, // 0 = exact, 1 = +-1 day, 2 = +-2 days
    timeSlotChoice: "ANY",
    currentResults: null
  };

  // DOM Elements
  const sourceSelect = document.getElementById("source-city");
  const destSelect = document.getElementById("destination-city");
  const swapBtn = document.getElementById("swap-route-btn");
  const dateInput = document.getElementById("travel-date");
  const daysLeftBadge = document.getElementById("days-left-badge");
  const searchBtn = document.getElementById("search-btn");
  const resultsArea = document.getElementById("results-area");

  // Tab Elements
  const navSearchBtn = document.getElementById("nav-search-btn");
  const navMetricsBtn = document.getElementById("nav-metrics-btn");
  const navCalendarBtn = document.getElementById("nav-calendar-btn");

  const searchSection = document.getElementById("search-section");
  const metricsSection = document.getElementById("metrics-section");
  const calendarSection = document.getElementById("calendar-section");

  // 1. Initialize Date Input (Default: 22 days ahead from today)
  const padZero = (n) => String(n).padStart(2, "0");
  const formatDateLocal = (d) => `${d.getFullYear()}-${padZero(d.getMonth() + 1)}-${padZero(d.getDate())}`;

  function initDatePicker() {
    const today = new Date();
    const defaultDate = new Date();
    defaultDate.setDate(today.getDate() + 22);

    const maxDate = new Date();
    maxDate.setDate(today.getDate() + 60); // 2 months lookahead cap

    dateInput.min = formatDateLocal(today);
    dateInput.max = formatDateLocal(maxDate);
    dateInput.value = formatDateLocal(defaultDate);
    state.travelDate = dateInput.value;

    updateDaysLeft();
  }

  function updateDaysLeft() {
    if (!dateInput.value) return;
    const parts = dateInput.value.split("-").map(Number);
    if (parts.length !== 3) return;
    const selected = new Date(parts[0], parts[1] - 1, parts[2]);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    selected.setHours(0, 0, 0, 0);

    const diffDays = Math.round((selected - today) / (1000 * 60 * 60 * 24));
    state.travelDate = dateInput.value;

    if (diffDays < 0) {
      daysLeftBadge.textContent = "Date in the past";
      daysLeftBadge.style.color = "#f43f5e";
    } else if (diffDays > 60) {
      daysLeftBadge.textContent = `${diffDays} days left (Capped at 60 days max)`;
      daysLeftBadge.style.color = "#f59e0b";
    } else {
      daysLeftBadge.textContent = `${diffDays} days until departure (${diffDays <= 7 ? "High Urgency" : diffDays <= 21 ? "Standard Booking Window" : "Early Bird Window"})`;
      daysLeftBadge.style.color = diffDays <= 7 ? "#e11d48" : "#7c3aed";
    }
  }

  dateInput.addEventListener("input", updateDaysLeft);
  dateInput.addEventListener("change", updateDaysLeft);

  // 2. Route Handling & Swap
  sourceSelect.addEventListener("change", (e) => {
    state.sourceCity = e.target.value;
    if (state.sourceCity === state.destinationCity) {
      // Auto switch destination to different city
      const alternatives = ["Mumbai", "Delhi", "Bangalore"].filter(c => c !== state.sourceCity);
      state.destinationCity = alternatives[0];
      destSelect.value = state.destinationCity;
    }
  });

  destSelect.addEventListener("change", (e) => {
    state.destinationCity = e.target.value;
    if (state.sourceCity === state.destinationCity) {
      const alternatives = ["Mumbai", "Delhi", "Bangalore"].filter(c => c !== state.destinationCity);
      state.sourceCity = alternatives[0];
      sourceSelect.value = state.sourceCity;
    }
  });

  swapBtn.addEventListener("click", () => {
    const temp = state.sourceCity;
    state.sourceCity = state.destinationCity;
    state.destinationCity = temp;
    sourceSelect.value = state.sourceCity;
    destSelect.value = state.destinationCity;
  });

  // 3. Airline Segmented Buttons
  const airlineBtns = document.querySelectorAll("#airline-segmented .segment-btn");
  airlineBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      airlineBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.airlineChoice = btn.getAttribute("data-airline");
    });
  });

  // 4. Flexibility Segmented Buttons
  const flexBtns = document.querySelectorAll("#flex-segmented .segment-btn");
  flexBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      flexBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.dateFlexibility = parseInt(btn.getAttribute("data-flex"), 10);
    });
  });

  // 5. Time Slot Chips
  const slotChips = document.querySelectorAll("#time-slot-chips .slot-chip");
  slotChips.forEach(chip => {
    chip.addEventListener("click", () => {
      slotChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      state.timeSlotChoice = chip.getAttribute("data-slot");
    });
  });

  // 6. Navigation Tabs
  function switchTab(activeTab) {
    [navSearchBtn, navMetricsBtn, navCalendarBtn].forEach(b => b.classList.remove("active"));
    [searchSection, metricsSection, calendarSection].forEach(s => s.classList.add("hidden"));

    if (activeTab === "search") {
      navSearchBtn.classList.add("active");
      searchSection.classList.remove("hidden");
    } else if (activeTab === "metrics") {
      navMetricsBtn.classList.add("active");
      metricsSection.classList.remove("hidden");
      loadModelMetrics();
    } else if (activeTab === "calendar") {
      navCalendarBtn.classList.add("active");
      calendarSection.classList.remove("hidden");
      loadFestivalCalendar();
    }
  }

  navSearchBtn.addEventListener("click", () => switchTab("search"));
  navMetricsBtn.addEventListener("click", () => switchTab("metrics"));
  navCalendarBtn.addEventListener("click", () => switchTab("calendar"));

  // 7. Execute Flexible Search
  searchBtn.addEventListener("click", executeSearch);

  async function executeSearch() {
    searchBtn.disabled = true;
    searchBtn.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="spin">
        <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10"/>
      </svg>
      <span>Searching Fares Across Matrix...</span>
    `;

    try {
      const payload = {
        source_city: state.sourceCity,
        destination_city: state.destinationCity,
        airline_choice: state.airlineChoice,
        travel_date: state.travelDate || dateInput.value,
        date_flexibility: state.dateFlexibility,
        time_slot_choice: state.timeSlotChoice
      };

      const res = await fetch("/api/flexible-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Search request failed");
      }

      const data = await res.json();
      state.currentResults = data;
      renderResults(data);
    } catch (err) {
      alert("Error executing search: " + err.message);
    } finally {
      searchBtn.disabled = false;
      searchBtn.innerHTML = `
        <span class="btn-text">Predict Fares & Compare Options</span>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      `;
    }
  }

  // 8. Render Search Results
  function renderResults(data) {
    resultsArea.classList.remove("hidden");
    resultsArea.scrollIntoView({ behavior: "smooth", block: "start" });

    // A. Populate Best Value Pick Card
    const cheapest = data.cheapest_option;
    document.getElementById("cheapest-airline").textContent = `${cheapest.airline} · ${cheapest.stops === 0 ? "Non-Stop" : "1 Stop"}`;
    document.getElementById("cheapest-date-time").textContent = `${cheapest.display_date} (${cheapest.day_of_week}) · ${cheapest.departure_time_label.split(" ")[0]}`;
    document.getElementById("cheapest-price").textContent = `₹${cheapest.predicted_fare.toLocaleString("en-IN")}`;
    document.getElementById("cheapest-meta").textContent = `Base ML: ₹${cheapest.base_ml_fare} · ${cheapest.has_surge ? cheapest.surge_tag : "No Surge"} · Duration: ${cheapest.duration_text}`;

    // B. Populate Savings Card
    const savings = data.savings;
    const savingsEl = document.getElementById("savings-amount");
    const savingsDesc = document.getElementById("savings-description");
    const savingsBadge = document.getElementById("savings-percent");

    if (savings > 0) {
      savingsEl.textContent = `₹${savings.toLocaleString("en-IN")}`;
      savingsDesc.textContent = `Save by picking ${cheapest.airline} on ${cheapest.display_date} (${cheapest.departure_time_label.split(" ")[0]})`;
      savingsBadge.textContent = `${data.savings_pct}% Cheaper than first choice`;
      savingsBadge.style.display = "inline-block";
    } else {
      savingsEl.textContent = `₹0`;
      savingsDesc.textContent = `Your initial choice is already the cheapest fare!`;
      savingsBadge.textContent = `Optimal Choice`;
      savingsBadge.style.display = "inline-block";
    }

    // C. Populate Calendar Surge Card
    const firstChoice = data.first_choice;
    const surgeTagEl = document.getElementById("active-surge-tag");
    const surgeDescEl = document.getElementById("active-surge-desc");
    const surgeMultEl = document.getElementById("active-surge-mult");

    if (firstChoice.has_surge) {
      surgeTagEl.textContent = firstChoice.surge_tag;
      surgeDescEl.textContent = firstChoice.surge_reason;
      surgeMultEl.textContent = `Surge Factor: +${Math.round(firstChoice.surge_factor * 100)}% applied on Base Fare`;
      surgeMultEl.style.color = "#e11d48";
    } else {
      surgeTagEl.textContent = "Standard Base Fare";
      surgeDescEl.textContent = "No festive or weekend rush surcharge detected on your departure date.";
      surgeMultEl.textContent = "Base Machine Learning Rate (0% Surge)";
      surgeMultEl.style.color = "#059669";
    }

    // D. Side-by-Side Airline Comparison
    const sideBySideSection = document.getElementById("side-by-side-section");
    if (data.airlines.length > 1) {
      sideBySideSection.style.display = "block";
      const aiFlights = data.all_results.filter(f => f.airline === "Air India");
      const indigoFlights = data.all_results.filter(f => f.airline === "IndiGo");

      if (aiFlights.length > 0) {
        const minAi = aiFlights.reduce((prev, curr) => prev.predicted_fare < curr.predicted_fare ? prev : curr);
        document.getElementById("ai-lowest-fare").textContent = `₹${minAi.predicted_fare.toLocaleString("en-IN")}`;
        document.getElementById("ai-lr-fare").textContent = `Baseline: ₹${minAi.lr_baseline_fare ? minAi.lr_baseline_fare.toLocaleString("en-IN") : minAi.predicted_fare}`;
        document.getElementById("ai-avg-dur").textContent = minAi.duration_text;
      }

      if (indigoFlights.length > 0) {
        const minIndigo = indigoFlights.reduce((prev, curr) => prev.predicted_fare < curr.predicted_fare ? prev : curr);
        document.getElementById("6e-lowest-fare").textContent = `₹${minIndigo.predicted_fare.toLocaleString("en-IN")}`;
        document.getElementById("6e-lr-fare").textContent = `Baseline: ₹${minIndigo.lr_baseline_fare ? minIndigo.lr_baseline_fare.toLocaleString("en-IN") : minIndigo.predicted_fare}`;
        document.getElementById("6e-avg-dur").textContent = minIndigo.duration_text;
      }
    } else {
      sideBySideSection.style.display = "none";
    }

    // E. Render Heatmap Matrix Grid
    renderFareGrid(data);
  }

  // 9. Render Fare Grid Table
  function renderFareGrid(data) {
    const container = document.getElementById("grid-container");
    const { display_dates, time_slots, airlines, grid, cheapest_option } = data;

    // Calculate min and max fare for dynamic gradient tiering
    const allFares = data.all_results.map(r => r.predicted_fare);
    const minPrice = Math.min(...allFares);
    const maxPrice = Math.max(...allFares);
    const range = Math.max(1, maxPrice - minPrice);

    let html = `
      <table class="fare-matrix-table">
        <thead>
          <tr>
            <th class="time-slot-th">Departure Time Slot</th>
    `;

    display_dates.forEach(d => {
      html += `
        <th>
          <div class="th-date-title" style="${d.is_selected ? 'color:#818cf8; font-weight:800;' : ''}">${d.display}</div>
          <div class="th-day-sub" style="font-size:0.7rem; color:var(--text-muted); font-weight:500;">${d.day}</div>
        </th>
      `;
    });

    html += `</tr></thead><tbody>`;

    time_slots.forEach(slot => {
      const slotLabel = {
        "Early_Morning": "Early Morning (00-06)",
        "Morning": "Morning (06-12)",
        "Afternoon": "Afternoon (12-18)",
        "Evening": "Evening (18-22)",
        "Night": "Night (22-24)",
        "Late_Night": "Late Night (23-04)"
      }[slot] || slot;

      html += `
        <tr>
          <td style="font-weight:700; font-size:0.85rem; color:var(--text-main);">${slotLabel}</td>
      `;

      display_dates.forEach(d => {
        const dateStr = d.date;

        // If comparing both airlines, find cheapest or show both
        let primaryItem = null;
        let secondaryItem = null;

        if (airlines.length > 1) {
          const aiItem = grid["Air India"] && grid["Air India"][slot] && grid["Air India"][slot][dateStr];
          const indigoItem = grid["IndiGo"] && grid["IndiGo"][slot] && grid["IndiGo"][slot][dateStr];

          if (aiItem && indigoItem) {
            primaryItem = aiItem.predicted_fare <= indigoItem.predicted_fare ? aiItem : indigoItem;
            secondaryItem = primaryItem === aiItem ? indigoItem : aiItem;
          } else {
            primaryItem = aiItem || indigoItem;
          }
        } else {
          const air = airlines[0];
          primaryItem = grid[air] && grid[air][slot] && grid[air][slot][dateStr];
        }

        if (!primaryItem) {
          html += `<td><div class="grid-cell">--</div></td>`;
          return;
        }

        const isCheapest = primaryItem.predicted_fare === cheapest_option.predicted_fare;
        const isUserChoice = primaryItem.is_user_choice;

        // Color tiering
        const pct = (primaryItem.predicted_fare - minPrice) / range;
        let tierClass = "price-tier-low";
        if (pct > 0.65) tierClass = "price-tier-high";
        else if (pct > 0.3) tierClass = "price-tier-mid";

        html += `
          <td>
            <div class="grid-cell ${isCheapest ? 'cell-cheapest' : ''} ${isUserChoice ? 'cell-user-choice' : ''}"
                 onclick="alert('${primaryItem.airline} on ${primaryItem.display_date} (${slot}):\\nFare: ₹${primaryItem.predicted_fare}\\nBase ML Fare: ₹${primaryItem.base_ml_fare}\\nSurge: ${primaryItem.has_surge ? primaryItem.surge_tag + ' (+' + Math.round(primaryItem.surge_factor * 100) + '%)' : 'None'}\\nStops: ${primaryItem.stops === 0 ? 'Non-Stop' : '1 Stop'}\\nDuration: ${primaryItem.duration_text}')">
              <span class="cell-price ${tierClass}">₹${primaryItem.predicted_fare.toLocaleString("en-IN")}</span>
              <span class="cell-airline">${primaryItem.airline}</span>
              ${secondaryItem ? `<span style="font-size:0.65rem; color:var(--text-muted);">${secondaryItem.airline}: ₹${secondaryItem.predicted_fare}</span>` : ''}
              ${primaryItem.has_surge ? `<span class="cell-tag" style="background:rgba(244,63,94,0.18); color:#fb7185;">${primaryItem.surge_tag.split(" ")[0]}</span>` : ''}
            </div>
          </td>
        `;
      });

      html += `</tr>`;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
  }

  // 10. Load Model Metrics Tab
  let metricsLoaded = false;
  async function loadModelMetrics() {
    if (metricsLoaded) return;
    try {
      const res = await fetch("/api/metrics");
      if (!res.ok) return;
      const data = await res.json();
      metricsLoaded = true;

      // Update Metric Numbers
      const rf = data.models.random_forest;
      const lr = data.models.linear_regression;

      document.getElementById("rf-mae-val").textContent = `₹${rf.mae.toFixed(2)}`;
      document.getElementById("lr-mae-val").textContent = `₹${lr.mae.toFixed(2)}`;

      document.getElementById("rf-r2-val").textContent = `${rf.r2.toFixed(4)}`;
      document.getElementById("lr-r2-val").textContent = `${lr.r2.toFixed(4)}`;

      document.getElementById("rf-rmse-val").textContent = `₹${rf.rmse.toFixed(2)}`;
      document.getElementById("lr-rmse-val").textContent = `₹${lr.rmse.toFixed(2)}`;

      document.getElementById("rf-mape-val").textContent = `${rf.mape.toFixed(2)}%`;
      document.getElementById("lr-mape-val").textContent = `${lr.mape.toFixed(2)}%`;

      // Render Feature Bars
      const barsContainer = document.getElementById("feature-bars");
      const maxImp = Math.max(...data.feature_importances.map(f => f.importance));
      let barsHtml = "";

      data.feature_importances.forEach(f => {
        const barWidth = Math.round((f.importance / maxImp) * 100);
        const cleanName = f.feature.replace(/^(cat__|num__|pass__)/, "").replace(/_/g, " ");
        barsHtml += `
          <div class="feature-bar-row">
            <span class="feature-name">${cleanName}</span>
            <div class="bar-track">
              <div class="bar-fill" style="width: ${barWidth}%"></div>
            </div>
            <span class="bar-pct">${(f.importance * 100).toFixed(1)}%</span>
          </div>
        `;
      });
      barsContainer.innerHTML = barsHtml;

      // Render Airline Breakdown Table
      const tableBody = document.getElementById("airline-metrics-body");
      let tableHtml = "";
      for (const [airline, stat] of Object.entries(data.airline_breakdown)) {
        tableHtml += `
          <tr>
            <td style="font-weight:700; color:var(--text-main);">${airline}</td>
            <td>${stat.samples.toLocaleString()}</td>
            <td>₹${stat.avg_fare.toLocaleString("en-IN")}</td>
            <td style="color:var(--emerald-main); font-weight:700;">₹${stat.rf_mae.toFixed(2)}</td>
            <td>${stat.rf_mape.toFixed(2)}%</td>
            <td style="color:var(--text-muted);">₹${stat.lr_mae.toFixed(2)}</td>
          </tr>
        `;
      }
      tableBody.innerHTML = tableHtml;
    } catch (e) {
      console.error("Failed to load metrics:", e);
    }
  }

  // 11. Load Festival Calendar Tab
  let calendarLoaded = false;
  async function loadFestivalCalendar() {
    if (calendarLoaded) return;
    try {
      const res = await fetch("/api/festivals");
      if (!res.ok) return;
      const data = await res.json();
      calendarLoaded = true;

      const timeline = document.getElementById("festivals-timeline");
      let html = "";

      data.festivals.forEach(fest => {
        html += `
          <div class="festival-card">
            <div class="fest-header">
              <span class="fest-name">${fest.name}</span>
              <span class="fest-badge">+${Math.round(fest.surgeFactor * 100)}% Surge</span>
            </div>
            <span class="fest-dates">${fest.startDate} to ${fest.endDate}</span>
            <p class="fest-desc">${fest.description}</p>
          </div>
        `;
      });

      timeline.innerHTML = html;
    } catch (e) {
      console.error("Failed to load calendar:", e);
    }
  }

  // Initialize
  initDatePicker();
  // Auto-run default search on load to delight user immediately
  executeSearch();
});
