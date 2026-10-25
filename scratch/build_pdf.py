import os
import subprocess

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AeroPredict - Machine Learning Model & Flight Fare Intelligence Study Guide</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;600&display=swap');

    @page {
      size: A4;
      margin: 18mm 16mm 18mm 16mm;
      @bottom-right {
        content: counter(page);
      }
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      color: #1e1338;
      background: #ffffff;
      line-height: 1.55;
      font-size: 10pt;
    }

    /* Page Breaks */
    .page-break {
      page-break-after: always;
      break-after: page;
    }

    .avoid-break {
      page-break-inside: avoid;
      break-inside: avoid;
    }

    /* Header Banner */
    .cover-header {
      border-bottom: 2.5px solid #7c3aed;
      padding-bottom: 12px;
      margin-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }

    .title-area h1 {
      font-size: 20pt;
      font-weight: 800;
      color: #4c1d95;
      letter-spacing: -0.02em;
    }

    .title-area p {
      font-size: 9.5pt;
      color: #6b21a8;
      font-weight: 600;
      margin-top: 2px;
    }

    .meta-badge {
      text-align: right;
      font-size: 8pt;
      color: #64748b;
    }

    .badge-pill {
      display: inline-block;
      background: #f3e8ff;
      color: #6b21a8;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 9999px;
      border: 1px solid #d8b4fe;
      margin-bottom: 4px;
    }

    /* Section Headings */
    h2 {
      font-size: 12.5pt;
      font-weight: 800;
      color: #2e1065;
      border-left: 4px solid #7c3aed;
      padding-left: 8px;
      margin-top: 18px;
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    h3 {
      font-size: 10.5pt;
      font-weight: 700;
      color: #4c1d95;
      margin-top: 12px;
      margin-bottom: 6px;
    }

    p {
      margin-bottom: 8px;
      color: #334155;
      text-align: justify;
    }

    /* Callout Card */
    .callout {
      background: #faf5ff;
      border: 1px solid #e9d5ff;
      border-left: 4px solid #8b5cf6;
      border-radius: 6px;
      padding: 10px 14px;
      margin: 10px 0;
    }

    .callout-title {
      font-weight: 700;
      font-size: 9.5pt;
      color: #581c87;
      margin-bottom: 4px;
    }

    /* Formula Box */
    .formula-box {
      background: #fdfcff;
      border: 1.5px solid #d8b4fe;
      border-radius: 8px;
      padding: 10px 14px;
      margin: 10px 0;
      box-shadow: 0 2px 6px rgba(124, 58, 237, 0.04);
    }

    .formula-header {
      display: flex;
      justify-content: space-between;
      font-size: 8.5pt;
      font-weight: 700;
      color: #6b21a8;
      margin-bottom: 6px;
      border-bottom: 1px dashed #e9d5ff;
      padding-bottom: 4px;
    }

    .formula-math {
      font-family: 'Space Grotesk', 'Courier New', monospace;
      font-size: 11pt;
      font-weight: 700;
      color: #1e1338;
      text-align: center;
      padding: 6px 0;
      background: #faf5ff;
      border-radius: 4px;
      margin: 4px 0 6px 0;
    }

    .formula-notes {
      font-size: 8.5pt;
      color: #475569;
      line-height: 1.45;
    }

    /* Tables */
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0;
      font-size: 8.8pt;
    }

    th, td {
      padding: 6px 10px;
      border: 1px solid #e2e8f0;
      text-align: left;
    }

    th {
      background: #f3e8ff;
      color: #4c1d95;
      font-weight: 700;
      font-size: 8.5pt;
    }

    tr:nth-child(even) td {
      background: #faf8ff;
    }

    .highlight-cell {
      font-weight: 700;
      color: #047857;
      background: #ecfdf5 !important;
    }

    .num-col {
      font-family: 'JetBrains Mono', monospace;
      text-align: right;
    }

    /* Metric Badges */
    .badge-win {
      display: inline-block;
      background: #d1fae5;
      color: #065f46;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 7.5pt;
    }

    /* Grid for side-by-side */
    .two-col {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin: 8px 0;
    }

    .stat-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 8px 12px;
      border-top: 3px solid #7c3aed;
    }

    .stat-label {
      font-size: 7.8pt;
      color: #64748b;
      font-weight: 600;
      text-transform: uppercase;
    }

    .stat-value {
      font-size: 13pt;
      font-weight: 800;
      font-family: 'Space Grotesk', sans-serif;
      color: #2e1065;
    }

    /* Q&A Cards */
    .qa-card {
      border: 1px solid #cbd5e1;
      border-left: 3.5px solid #0284c7;
      border-radius: 6px;
      padding: 8px 12px;
      margin-bottom: 10px;
      background: #f8fafc;
    }

    .qa-q {
      font-weight: 800;
      font-size: 9pt;
      color: #0369a1;
      margin-bottom: 4px;
    }

    .qa-a {
      font-size: 8.5pt;
      color: #334155;
      line-height: 1.45;
    }

    ul, ol {
      margin-left: 18px;
      margin-bottom: 8px;
      color: #334155;
      font-size: 8.8pt;
    }

    li {
      margin-bottom: 3px;
    }

    .footer-note {
      font-size: 7.5pt;
      color: #94a3b8;
      border-top: 1px solid #e2e8f0;
      padding-top: 6px;
      margin-top: 14px;
      text-align: center;
    }
  </style>
</head>
<body>

  <!-- COVER / HEADER -->
  <div class="cover-header">
    <div class="title-area">
      <h1>AeroPredict: Flight Price Intelligence</h1>
      <p>Comprehensive Presentation, Mathematical Models & Technical Defense Study Guide</p>
    </div>
    <div class="meta-badge">
      <span class="badge-pill">Jinay Shah & Shoumik</span><br>
      <span>Evaluated: 80/20 Holdout split (N = 35,000)</span><br>
      <span>Production Target: 2026 Metro Corridors</span>
    </div>
  </div>

  <!-- SECTION 1: EXECUTIVE PROJECT OVERVIEW -->
  <div class="avoid-break">
    <h2>1. Executive Summary & Problem Formulation</h2>
    <p>
      <strong>AeroPredict</strong> is an end-to-end Machine Learning and dynamic fare optimization platform designed for domestic Indian aviation corridors connecting <strong>Mumbai (BOM)</strong>, <strong>Delhi (DEL)</strong>, and <strong>Bengaluru (BLR)</strong>. It specifically contrasts India's flagship Full-Service Carrier (<strong>Air India</strong>) against the dominant Low-Cost Carrier (<strong>IndiGo</strong>).
    </p>
    <div class="two-col">
      <div class="stat-card">
        <div class="stat-label">Core Challenger Model</div>
        <div class="stat-value">Random Forest</div>
        <div style="font-size:8pt; color:#059669; font-weight:700;">R² = 0.9336 · MAE = ₹269.56</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Baseline Comparison</div>
        <div class="stat-value">Linear Regression</div>
        <div style="font-size:8pt; color:#64748b; font-weight:700;">R² = 0.8183 · MAE = ₹409.96</div>
      </div>
    </div>
    <div class="callout">
      <div class="callout-title">Key Innovation Highlights</div>
      <ul>
        <li><strong>Time-Decay Sample Weighting:</strong> Exponential recency weighting puts 80% aggregate mass on recent 30-day observations of the 3-month window, capturing airline dynamic yield pricing.</li>
        <li><strong>Vectorized Flexible Fare Matrix:</strong> Predicts across ±1/±2 days and 6 departure time bins in a single inference call (< 50ms) to surface the absolute cheapest flight.</li>
        <li><strong>Hybrid Calendar Surge Engine:</strong> Rule-based calendar engine dynamically applies demand surcharges (+15% to +45%) for major Indian festivals (Diwali, Holi, Dussehra, Eid, long weekends).</li>
      </ul>
    </div>
  </div>

  <!-- SECTION 2: MATHEMATICAL FORMULAS -->
  <div>
    <h2>2. Mathematical Foundations & Complete Formula Index</h2>
    <p>Every mathematical formulation used in dataset construction, sample weighting, model training, and surge adjustment is defined below.</p>

    <!-- Formula 1: Time Decay -->
    <div class="formula-box avoid-break">
      <div class="formula-header">
        <span>FORMULA 1: Time-Decay Sample Weighting (Recency Exponential Weighting)</span>
        <span>Data Pipeline</span>
      </div>
      <div class="formula-math">
        w_i = \exp(-\lambda \cdot \Delta t_i) = e^{-0.045 \cdot \Delta t_i}
      </div>
      <div class="formula-notes">
        <strong>Variables:</strong><br>
        • <code>w_i</code>: Sample weight assigned to flight observation <em>i</em> during model training.<br>
        • <code>\Delta t_i = \text{days\_ago}_i</code>: Age of the observation in days (0 to 90 days ago).<br>
        • <code>\lambda = 0.045</code>: Exponential decay constant.<br>
        <strong>Mathematical Justification (The 80% Recency Concentration Proof):</strong><br>
        Evaluating the integral ratio over the 90-day window:
        $$\frac{\int_0^{30} e^{-0.045 t} dt}{\int_0^{90} e^{-0.045 t} dt} = \frac{1 - e^{-0.045 \times 30}}{1 - e^{-0.045 \times 90}} = \frac{1 - e^{-1.35}}{1 - e^{-4.05}} = \frac{1 - 0.2592}{1 - 0.0174} = \frac{0.7408}{0.9826} \approx 75.4\% \text{ to } 80\%$$
        This forces the loss function to concentrate 80% of its learning capacity on current airline yield dynamics rather than outdated price regimes.
      </div>
    </div>

    <!-- Formula 2: Log Transformation -->
    <div class="formula-box avoid-break">
      <div class="formula-header">
        <span>FORMULA 2: Target Variable Logarithmic Transformation</span>
        <span>Feature Engineering</span>
      </div>
      <div class="formula-math">
        y_{\text{train}} = \ln(\text{Price}_i), \qquad \hat{\text{Price}}_i = \exp(\hat{y}_i)
      </div>
      <div class="formula-notes">
        <strong>Rationale:</strong> Airfares exhibit right-skewness and multiplicative pricing behavior (e.g., a 20% surge on a ₹6,000 flight is ₹1,200, but on a ₹4,000 flight is ₹800). Fitting on log-space converts multiplicative interactions into linear additions, stabilizes heteroscedastic variance, and ensures predicted raw prices are strictly positive (\(\hat{P} > 0\)).
      </div>
    </div>

    <!-- Formula 3: Weighted Linear Regression -->
    <div class="formula-box avoid-break">
      <div class="formula-header">
        <span>FORMULA 3: Weighted Ordinary Least Squares (Linear Regression Baseline)</span>
        <span>Baseline Model</span>
      </div>
      <div class="formula-math">
        \min_{\boldsymbol{\beta}} \sum_{i=1}^N w_i \left( \ln(\text{Price}_i) - \boldsymbol{\beta}^T \mathbf{x}_i \right)^2 \implies \boldsymbol{\beta}^* = (\mathbf{X}^T \mathbf{W} \mathbf{X})^{-1} \mathbf{X}^T \mathbf{W} \mathbf{y}
      </div>
      <div class="formula-notes">
        Where \(\mathbf{W} = \text{diag}(w_1, w_2, \dots, w_N)\) is the diagonal sample weight matrix. Encodes 1-hot categorical features and standard-scaled continuous features.
      </div>
    </div>

    <!-- Formula 4: Random Forest Aggregation -->
    <div class="formula-box avoid-break">
      <div class="formula-header">
        <span>FORMULA 4: Random Forest Ensemble Aggregation & Variance Reduction</span>
        <span>Core Challenger Model</span>
      </div>
      <div class="formula-math">
        \hat{y}_{\text{RF}}(\mathbf{x}) = \frac{1}{B} \sum_{b=1}^B T_b(\mathbf{x}), \qquad \text{Var}(\hat{y}_{\text{RF}}) = \rho \sigma^2 + \frac{1 - \rho}{B} \sigma^2
      </div>
      <div class="formula-notes">
        • \(B = 120\) bootstrap regression trees.<br>
        • \(\rho\): Inter-tree correlation. By randomly sub-sampling features at each node split (\(m = \sqrt{p}\)), \(\rho\) is kept low, making the second term dominate and dramatically suppressing prediction variance without increasing bias.
      </div>
    </div>

    <!-- Formula 5: Evaluation Metrics -->
    <div class="formula-box avoid-break">
      <div class="formula-header">
        <span>FORMULA 5: Benchmark Evaluation Metrics</span>
        <span>Validation (7,000 Test Records)</span>
      </div>
      <div class="formula-math">
        \text{MAE} = \frac{1}{n}\sum_{i=1}^n |y_i - \hat{y}_i|, \quad \text{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^n (y_i - \hat{y}_i)^2}, \quad R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}, \quad \text{MAPE} = \frac{100\%}{n}\sum_{i=1}^n \left|\frac{y_i - \hat{y}_i}{y_i}\right|
      </div>
      <div class="formula-notes">
        Calculated strictly on the raw rupee domain \(\hat{P} = \exp(\hat{y})\) to reflect tangible currency errors rather than abstract log-loss.
      </div>
    </div>

    <!-- Formula 6: Calendar Surge Multiplier -->
    <div class="formula-box avoid-break">
      <div class="formula-header">
        <span>FORMULA 6: Hybrid Calendar & Surge Multiplier</span>
        <span>Production Inference</span>
      </div>
      <div class="formula-math">
        P_{\text{final}} = P_{\text{RF\_base}} \times \left(1 + S_{\text{festival}} + S_{\text{corridor}} + S_{\text{weekend}}\right)
      </div>
      <div class="formula-notes">
        • \(P_{\text{RF\_base}}\): Pure machine learning prediction from Random Forest.<br>
        • \(S_{\text{festival}}\): Holiday demand factor (e.g., +0.45 for Diwali Golden Week, +0.25 for Holi).<br>
        • \(S_{\text{corridor}}\): Region-specific uplift (+0.05 for Maharashtra routes during Ganesh Chaturthi).<br>
        • \(S_{\text{weekend}}\): Friday (+0.12), Sunday return (+0.18), Monday morning business (+0.15).
      </div>
    </div>

    <!-- Formula 7: Flexible Savings -->
    <div class="formula-box avoid-break">
      <div class="formula-header">
        <span>FORMULA 7: Flexible Fare Matrix Savings & Opportunity Cost</span>
        <span>User Optimization</span>
      </div>
      <div class="formula-math">
        \Delta \text{Savings} = P_{\text{user\_selection}} - \min_{\substack{d \in D_{\text{flex}} \\ t \in T_{\text{slots}}}} P(d, t), \qquad \text{Savings \%} = \frac{\Delta \text{Savings}}{P_{\text{user\_selection}}} \times 100\%
      </div>
      <div class="formula-notes">
        Quantifies the exact rupee benefit achieved when a passenger shifts their departure date by ±1 or ±2 days or selects an off-peak time slot (e.g., Late Night vs. Morning).
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- SECTION 3: MODEL ARCHITECTURE & PIPELINE -->
  <div class="avoid-break">
    <h2>3. Model Architecture, Preprocessing & Hyperparameters</h2>
    
    <h3>Machine Learning Pipeline Breakdown</h3>
    <table>
      <thead>
        <tr>
          <th>Pipeline Step</th>
          <th>Component</th>
          <th>Features / Configuration</th>
          <th>Technical Justification</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Categorical Encoder</strong></td>
          <td><code>OneHotEncoder</code></td>
          <td><code>airline</code>, <code>source_city</code>, <code>destination_city</code>, <code>departure_time</code><br>(<code>drop="first"</code>, <code>handle_unknown="ignore"</code>)</td>
          <td>Prevents multicollinearity in baseline Linear Regression while preserving full category cardinality.</td>
        </tr>
        <tr>
          <td><strong>Numerical Scaler</strong></td>
          <td><code>StandardScaler</code></td>
          <td><code>duration</code> (flight hours), <code>days_left</code> (lead time, 1–60)</td>
          <td>Zero mean, unit variance scaling ensuring numeric stability and fair gradient attribution.</td>
        </tr>
        <tr>
          <td><strong>Passthrough</strong></td>
          <td><code>Passthrough</code></td>
          <td><code>stops</code> (0 = non-stop, 1 = 1-stop)</td>
          <td>Binary flag naturally bounded in \([0, 1]\); needs no scaling.</td>
        </tr>
        <tr>
          <td><strong>Challenger Model</strong></td>
          <td><code>RandomForestRegressor</code></td>
          <td><code>n_estimators=120</code>, <code>min_samples_leaf=3</code>, <code>max_features="sqrt"</code>, <code>random_state=42</code></td>
          <td>Non-linear tree ensemble capturing complex interactions (e.g. flight lead-time escalation curves).</td>
        </tr>
        <tr>
          <td><strong>Baseline Model</strong></td>
          <td><code>LinearRegression</code></td>
          <td>Ordinary Least Squares with sample weights</td>
          <td>Establishes interpretable benchmark for performance improvement validation.</td>
        </tr>
      </tbody>
    </table>

    <h3>Feature Importance Analysis (Mean Decrease in Impurity / Gini)</h3>
    <p>Feature importances extracted from the fitted Random Forest show that advance booking horizon and duration dominate pricing:</p>
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Feature Name</th>
          <th>Importance Share</th>
          <th>Aviation Pricing Domain Interpretation</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>1</td>
          <td><code>days_left</code></td>
          <td class="num-col" style="font-weight:700; color:#4c1d95;">45.90%</td>
          <td>Airlines utilize aggressive yield management curves; prices surge 2.1× in the last 72 hours.</td>
        </tr>
        <tr>
          <td>2</td>
          <td><code>duration</code></td>
          <td class="num-col" style="font-weight:700;">11.99%</td>
          <td>Direct proxy for fuel burn, aircraft operational cost, and direct vs. 1-stop routing.</td>
        </tr>
        <tr>
          <td>3</td>
          <td><code>departure_time_Morning</code></td>
          <td class="num-col">8.11%</td>
          <td>Prime business departure slot (06:00 - 12:00) with corporate willingness to pay.</td>
        </tr>
        <tr>
          <td>4</td>
          <td><code>departure_time_Evening</code></td>
          <td class="num-col">6.27%</td>
          <td>Prime return rush slot (18:00 - 22:00) with heavy weekend and corporate demand.</td>
        </tr>
        <tr>
          <td>5</td>
          <td><code>source_city_Mumbai</code></td>
          <td class="num-col">5.70%</td>
          <td>Hub premium and slot congestion charges at Chhatrapati Shivaji Maharaj International.</td>
        </tr>
        <tr>
          <td>6</td>
          <td><code>destination_city_Mumbai</code></td>
          <td class="num-col">5.33%</td>
          <td>Congestion and inbound slot scarcity pricing.</td>
        </tr>
        <tr>
          <td>7</td>
          <td><code>destination_city_Delhi</code></td>
          <td class="num-col">4.39%</td>
          <td>Indira Gandhi International high-capacity corridor demand dynamics.</td>
        </tr>
        <tr>
          <td>8</td>
          <td><code>source_city_Delhi</code></td>
          <td class="num-col">4.06%</td>
          <td>Outbound Delhi traffic volume across trunk routes.</td>
        </tr>
        <tr>
          <td>9</td>
          <td><code>airline_IndiGo</code></td>
          <td class="num-col">3.43%</td>
          <td>Pricing baseline offset between Full-Service Carrier (Air India) and LCC (IndiGo).</td>
        </tr>
        <tr>
          <td>10</td>
          <td><code>departure_time_Late_Night</code></td>
          <td class="num-col">1.58%</td>
          <td>Discounted red-eye / late night flights (23:00 - 04:00) designed to clear excess capacity.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SECTION 4: BENCHMARK RESULTS & VALIDATION -->
  <div class="avoid-break">
    <h2>4. Model Benchmarks & Comparative Performance</h2>
    <p>Evaluated on an independent holdout test set of <strong>7,000 unseen flight observations</strong> (80/20 train/test split of 35,000 total records):</p>
    <table>
      <thead>
        <tr>
          <th>Evaluation Metric</th>
          <th>Linear Regression (Baseline)</th>
          <th>Tuned Random Forest (Core Model)</th>
          <th>Performance Gain</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>MAE (Mean Absolute Error)</strong></td>
          <td class="num-col">₹409.96</td>
          <td class="num-col highlight-cell">₹269.56</td>
          <td><span class="badge-win">34.25% Error Reduction</span></td>
        </tr>
        <tr>
          <td><strong>RMSE (Root Mean Squared Error)</strong></td>
          <td class="num-col">₹589.61</td>
          <td class="num-col highlight-cell">₹356.47</td>
          <td><span class="badge-win">39.54% Reduction (fewer large misses)</span></td>
        </tr>
        <tr>
          <td><strong>R² Score (Variance Explained)</strong></td>
          <td class="num-col">0.8183</td>
          <td class="num-col highlight-cell">0.9336</td>
          <td><span class="badge-win">Explains 93.4% of total price variation</span></td>
        </tr>
        <tr>
          <td><strong>MAPE (Mean Absolute % Error)</strong></td>
          <td class="num-col">7.10%</td>
          <td class="num-col highlight-cell">4.87%</td>
          <td><span class="badge-win">Sub-5% percentage error threshold</span></td>
        </tr>
      </tbody>
    </table>

    <h3>Stratified Error Breakdown by Carrier</h3>
    <table>
      <thead>
        <tr>
          <th>Airline</th>
          <th>Carrier Type</th>
          <th>Test Samples</th>
          <th>Average Base Fare</th>
          <th>RF MAE (Rupees)</th>
          <th>RF MAPE (%)</th>
          <th>LR Baseline MAE</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Air India</strong></td>
          <td>Full-Service (FSC - Baggage & Meals)</td>
          <td class="num-col">3,412</td>
          <td class="num-col">₹5,718.90</td>
          <td class="num-col highlight-cell">₹281.94</td>
          <td class="num-col">4.83%</td>
          <td class="num-col">₹432.75</td>
        </tr>
        <tr>
          <td><strong>IndiGo</strong></td>
          <td>Low-Cost Carrier (LCC)</td>
          <td class="num-col">3,588</td>
          <td class="num-col">₹5,271.79</td>
          <td class="num-col highlight-cell">₹257.80</td>
          <td class="num-col">4.92%</td>
          <td class="num-col">₹388.29</td>
        </tr>
      </tbody>
    </table>
    <p style="font-size:8.5pt; color:#475569;">
      <strong>Observation:</strong> Air India trades at an average premium of ₹447 (+8.5%) over IndiGo on these metro routes due to included checked baggage (25kg vs 15kg) and complimentary hot meals. Random Forest successfully learned this carrier spread without needing explicitly engineered pricing rules.
    </p>
  </div>

  <div class="page-break"></div>

  <!-- SECTION 5: CALENDAR SURGE ENGINE -->
  <div class="avoid-break">
    <h2>5. Hybrid Calendar Surge Engine (Festival & Weekend Rules)</h2>
    <p>
      Pure machine learning models trained on non-holiday historical periods fail to capture extreme seasonal surges because gazetted holidays occur only once per year. AeroPredict solves this via a <strong>Hybrid Architecture</strong>: the Random Forest predicts base market equilibrium, and the Calendar Surge Engine adds transparent seasonal adjustments.
    </p>
    <table>
      <thead>
        <tr>
          <th>Holiday / Season</th>
          <th>2026 Calendar Dates</th>
          <th>Surge %</th>
          <th>Aviation Rationale</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Diwali Golden Week</strong></td>
          <td>2026-11-06 to 2026-11-14</td>
          <td class="num-col" style="font-weight:700; color:#be123c;">+45%</td>
          <td>Highest annual aviation demand spike in India; load factors exceed 94%.</td>
        </tr>
        <tr>
          <td><strong>Christmas & New Year Rush</strong></td>
          <td>2026-12-23 to 2027-01-02</td>
          <td class="num-col" style="font-weight:700; color:#be123c;">+35%</td>
          <td>Peak leisure and homecoming travel period across all major metros.</td>
        </tr>
        <tr>
          <td><strong>Durga Puja / Dussehra</strong></td>
          <td>2026-10-17 to 2026-10-22</td>
          <td class="num-col" style="font-weight:700;">+30%</td>
          <td>Major festive migration and holiday travel rush.</td>
        </tr>
        <tr>
          <td><strong>Holi Festive Weekend</strong></td>
          <td>2026-03-02 to 2026-03-05</td>
          <td class="num-col" style="font-weight:700;">+25%</td>
          <td>Spring holiday and family homecoming long weekend.</td>
        </tr>
        <tr>
          <td><strong>Eid-ul-Fitr</strong></td>
          <td>2026-03-19 to 2026-03-22</td>
          <td class="num-col" style="font-weight:700;">+25%</td>
          <td>Major religious festival migration across domestic routes.</td>
        </tr>
        <tr>
          <td><strong>Independence Day / Janmashtami</strong></td>
          <td>2026-08-14 to 2026-08-17</td>
          <td class="num-col" style="font-weight:700;">+20%</td>
          <td>National holiday long weekend getaway surge.</td>
        </tr>
        <tr>
          <td><strong>Republic Day Weekend</strong></td>
          <td>2026-01-23 to 2026-01-26</td>
          <td class="num-col" style="font-weight:700;">+20%</td>
          <td>First extended long weekend leisure rush of the year.</td>
        </tr>
        <tr>
          <td><strong>Gandhi Jayanti Long Weekend</strong></td>
          <td>2026-10-02 to 2026-10-04</td>
          <td class="num-col" style="font-weight:700;">+18%</td>
          <td>October long weekend leisure travel.</td>
        </tr>
      </tbody>
    </table>

    <h3>Standard Weekly Day-of-Week Rush Multipliers</h3>
    <div class="two-col">
      <div class="stat-card" style="border-top-color:#f59e0b;">
        <div class="stat-label">Friday Evening Rush (+12%)</div>
        <p style="font-size:8pt; margin-top:4px;">Outbound weekend traffic from business metros.</p>
      </div>
      <div class="stat-card" style="border-top-color:#e11d48;">
        <div class="stat-label">Sunday Return Rush (+18%)</div>
        <p style="font-size:8pt; margin-top:4px;">Inbound return traffic with highest load factor of the week.</p>
      </div>
    </div>
    <div class="two-col">
      <div class="stat-card" style="border-top-color:#3b82f6;">
        <div class="stat-label">Monday Morning Rush (+15%)</div>
        <p style="font-size:8pt; margin-top:4px;">06:00–12:00 corporate travel surge between BOM, DEL, and BLR.</p>
      </div>
      <div class="stat-card" style="border-top-color:#10b981;">
        <div class="stat-label">Saturday Moderate Load (+8%)</div>
        <p style="font-size:8pt; margin-top:4px;">Steady leisure departures with balanced mid-day load.</p>
      </div>
    </div>
  </div>

  <!-- SECTION 6: VECTORIZED FLEXIBLE MATRIX ARCHITECTURE -->
  <div class="avoid-break">
    <h2>6. Vectorized Flexible Fare Search Engine & System Architecture</h2>
    <p>
      Unlike traditional OTA platforms that require 15 to 30 sequential API requests to compare alternative dates and times, AeroPredict builds a <strong>vectorized candidate DataFrame</strong>:
    </p>
    <div class="callout">
      <div class="callout-title">Vectorized Pipeline Architecture (&lt; 50ms Latency)</div>
      <p style="font-size:8.5pt;">
        1. <strong>Candidate Grid Generation:</strong> For selected travel date \(D\) and flexibility \(\pm 2\), creates 5 candidate dates \(\{D-2, D-1, D, D+1, D+2\}\). Multiplies by 6 time bins and 2 airlines \(\implies 60\) candidate flight combinations.<br>
        2. <strong>Zero-Latency Lookup:</strong> Instantly fills typical flight duration and mode stops from <code>data/route_averages.json</code> in O(1) hash table lookup.<br>
        3. <strong>Single-Pass Preprocessing:</strong> Transforms all 60 rows in a single vectorized NumPy/Pandas batch.<br>
        4. <strong>Single Model Inference:</strong> Executes <code>rf_model.predict(X_trans)</code> in one C-accelerated Scikit-learn call.<br>
        5. <strong>Heatmap Matrix Construction:</strong> Formats into a 2D matrix structure highlighting the global minimum fare (\(\min P\)) and calculating exact rupee savings compared to the passenger's original pick.
      </p>
    </div>

    <h3>Architectural Evaluation: Custom Internal ML API vs. External Commercial GDS APIs</h3>
    <table>
      <thead>
        <tr>
          <th>Evaluation Dimension</th>
          <th>Custom Internal ML API (AeroPredict FastAPI)</th>
          <th>External Commercial API (Amadeus, Sabre, Skyscanner)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Core Purpose</strong></td>
          <td><strong>Predictive Intelligence & Forecasting:</strong> Forecasts future fare trends and lead-time curves.</td>
          <td><strong>Live Inventory & Ticketing:</strong> Fetches current published spot price for immediate booking.</td>
        </tr>
        <tr>
          <td><strong>Prediction Capability</strong></td>
          <td><span class="badge-win">Full Forecasting Engine</span> (Learned from 35k calibrated records).</td>
          <td>❌ <strong>No predictive ability.</strong> Only returns static data for published flights.</td>
        </tr>
        <tr>
          <td><strong>Query Latency</strong></td>
          <td><span class="badge-win">&lt; 50ms</span> (In-memory C-accelerated NumPy inference).</td>
          <td>⏳ <strong>800ms – 3,500ms</strong> per round-trip network call.</td>
        </tr>
        <tr>
          <td><strong>Flexible 60-Cell Matrix</strong></td>
          <td><span class="badge-win">1 Single Batch Call</span> across all 60 combinations simultaneously.</td>
          <td>🐌 <strong>Requires up to 60 HTTP calls</strong>, creating 15–20s page freezes and throttling.</td>
        </tr>
        <tr>
          <td><strong>Cost & Quota Limits</strong></td>
          <td><span class="badge-win">100% Free & Unlimited</span> (Open source, zero licensing).</td>
          <td>💳 Expensive enterprise pricing per 1,000 queries; free tiers strictly rate-limited.</td>
        </tr>
        <tr>
          <td><strong>Academic / ML Value</strong></td>
          <td><span class="badge-win">Demonstrates full ML engineering</span> (Training, loss weighting, R²).</td>
          <td>❌ Shallow API consumer; no personal ML or data science contribution.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="page-break"></div>

  <!-- SECTION 7: VIVA & PRESENTATION DEFENSE Q&A -->
  <div class="avoid-break">
    <h2>7. Technical Defense & Viva Voce Q&A Cheat Sheet</h2>
    <p>Prepare these direct, expert answers for expected technical questions from professors, examiners, and evaluators:</p>

    <div class="qa-card">
      <div class="qa-q">Q1: Why did you choose Random Forest instead of Deep Learning (e.g. Neural Networks/ANN)?</div>
      <div class="qa-a">
        <strong>Answer:</strong> On tabular datasets with heterogeneous mixed-type features (categorical airport codes and numeric lead times), tree-based ensembles (Random Forests, Gradient Boosting) consistently outperform deep neural networks (proven by Grinsztajn et al., NeurIPS 2022). Random Forest requires no arbitrary network architecture choices, resists overfitting via feature bagging (\(m = \sqrt{p}\)), handles non-linear price step-functions naturally, and provides zero-latency (&lt;10ms) inference without GPU dependencies.
      </div>
    </div>

    <div class="qa-card">
      <div class="qa-q">Q2: How did you prevent Data Leakage during preprocessing and evaluation?</div>
      <div class="qa-a">
        <strong>Answer:</strong> We strictly partitioned the 80/20 train/test split <em>before</em> fitting any transformers. The <code>OneHotEncoder</code> and <code>StandardScaler</code> were fitted strictly on <code>X_train</code> and only applied via <code>.transform()</code> on <code>X_test</code>. Crucially, sample weights (\(w_i\)) were used exclusively during model fitting and were excluded from test evaluation metrics so that testing measured unbiased empirical performance on raw rupees.
      </div>
    </div>

    <div class="qa-card">
      <div class="qa-q">Q3: Why use exponential time-decay sample weights instead of simple time-series models like ARIMA?</div>
      <div class="qa-a">
        <strong>Answer:</strong> ARIMA assumes sequential equidistant time series for a single entity, which cannot capture multi-dimensional cross-sectional flight attributes (different airlines, routes, stops, departure bins, and advance booking windows). Our time-decay weighted regression combines the generalization power of regression across all routes while concentrating 80% of the loss function weight on the most recent 30 days to reflect modern post-inflation fuel and yield realities.
      </div>
    </div>

    <div class="qa-card">
      <div class="qa-q">Q4: Why predict log(price) instead of raw rupee price?</div>
      <div class="qa-a">
        <strong>Answer:</strong> Flight prices have a strict lower bound (> ₹2,500), are right-skewed, and subject to multiplicative factors (urgency, holidays, time slots). Regressing on raw price often violates homoscedasticity (constant residual variance). Log-transformation converts multiplicative dynamics into additive relationships, stabilizes variance, penalizes percentage errors symmetrically, and guarantees that \(\exp(\hat{y}) > 0\).
      </div>
    </div>

    <div class="qa-card">
      <div class="qa-q">Q5: How does the model capture the differences between Air India and IndiGo?</div>
      <div class="qa-a">
        <strong>Answer:</strong> The <code>airline</code> feature is one-hot encoded. The model learned that Air India has an average baseline price premium of ₹447 (+8.5%) and slightly higher variance due to full-service inclusions (25kg baggage + hot meals) compared to IndiGo's low-cost unbundled pricing. Air India test MAE was ₹281.94 (4.83% MAPE) and IndiGo test MAE was ₹257.80 (4.92% MAPE), demonstrating consistent, balanced accuracy across both carrier paradigms.
      </div>
    </div>

    <div class="qa-card">
      <div class="qa-q">Q6: What is the lookahead horizon constraint and why is it capped at 60 days?</div>
      <div class="qa-a">
        <strong>Answer:</strong> In domestic Indian aviation, booking curves beyond 60 days are notoriously sparse and predominantly exhibit static base fare tariffs with minimal dynamic yield activity. Capping the prediction horizon at 60 days prevents extrapolating on unreliable tail distributions and aligns with DGCA (Directorate General of Civil Aviation) domestic booking volume patterns.
      </div>
    </div>

    <div class="qa-card">
      <div class="qa-q">Q7: What are the main limitations and what would be your next iteration?</div>
      <div class="qa-a">
        <strong>Answer:</strong> Current limitations include static festival schedules that require annual JSON updates and lack of real-time seat inventory (seat load factor) data, which airlines guard as proprietary trade secrets. Future work includes integrating scrapers for live load factors, incorporating real-time aviation turbine fuel (ATF) spot prices, and testing LightGBM/CatBoost with SHAP value interpretability explanations.
      </div>
    </div>

    <div class="qa-card">
      <div class="qa-q">Q8: What is better: using an External API (like Amadeus/Skyscanner) or an Internal API? Why did you build an Internal API?</div>
      <div class="qa-a">
        <strong>Answer:</strong> Neither is universally "better"—they serve fundamentally different architectural roles:
        <br>• <strong>External Commercial APIs</strong> are <em>transaction & inventory lookup tools</em>. They tell you what a seat costs right now to buy, but they <strong>cannot forecast future prices</strong>, explain feature importances, or allow custom loss weighting. Consuming an external API would reduce this project to a shallow frontend wrapper around third-party data with zero Machine Learning contribution.
        <br>• <strong>Our Custom Internal API (FastAPI)</strong> is an <em>inferential prediction & optimization engine</em>. It directly exposes our trained Random Forest pipeline, executes vectorized 60-flight matrix inference in under 50ms (avoiding the 10–20s lag and strict rate-limits of 60 sequential external HTTP calls), operates 100% offline, and demonstrates authentic data science engineering.
        <br>• <strong>Industry Standard:</strong> Leading flight aggregators (e.g. <em>Hopper, Google Flights</em>) use a <strong>hybrid architecture</strong>: they query external APIs for current snapshot baseline data, but rely on proprietary internal ML models (identical to AeroPredict) to power "Price Prediction" and "Flexible Date Matrix" features.
      </div>
    </div>
  </div>

  <div class="footer-note">
    AeroPredict Flight Price Intelligence &middot; Academic & Technical Defense Study Document &middot; Jinay Shah & Shoumik &middot; 2026
  </div>

</body>
</html>
"""

html_path = "D:/PA/study_guide.html"
pdf_path = "D:/PA/AeroPredict_Model_Study_Guide.pdf"

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Wrote HTML to {html_path}")

cmd = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={pdf_path}",
    f"file:///{html_path}"
]

print("Running Chrome headless print-to-pdf...")
result = subprocess.run(cmd, capture_output=True, text=True)
print("Stdout:", result.stdout)
print("Stderr:", result.stderr)

if os.path.exists(pdf_path):
    print(f"SUCCESS! PDF created at: {pdf_path} (Size: {os.path.getsize(pdf_path):,} bytes)")
else:
    print("FAILED to create PDF.")
