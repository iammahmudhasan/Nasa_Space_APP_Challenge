# 🔬 Scientific Methodology & Mathematical Formulations
### NASA Earth Intelligence Agent (NEIA) — Scientific Integrity Framework

---

## 1. Remote Sensing Physics: Normalized Difference Vegetation Index (NDVI)

The Normalized Difference Vegetation Index (NDVI) utilizes the differential reflectance between the Red chlorophyll absorption band and the Near-Infrared (NIR) mesophyll scattering band:

$$\text{NDVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + \rho_{\text{Red}}}$$

In the **MODIS MOD13Q1** product:
- $\rho_{\text{Red}}$: Band 1 ($620 - 670\,\text{nm}$)
- $\rho_{\text{NIR}}$: Band 2 ($841 - 876\,\text{nm}$)
- Compositing Period: 16-day Maximum Value Composite (MVC) to minimize atmospheric cloud and aerosol contamination.

---

## 2. Temporal Trend Testing: The Mann-Kendall Non-Parametric Test

To determine whether the multi-year trajectory represents a monotonic environmental decline rather than random stochastic variance, NEIA implements the Mann-Kendall test (Mann 1945; Kendall 1975):

$$S = \sum_{k=1}^{n-1}\sum_{j=k+1}^{n}\operatorname{sgn}(x_j - x_k)$$

Where:
$$\operatorname{sgn}(\theta) = \begin{cases} +1 & \text{if } \theta > 0 \\ 0 & \text{if } \theta = 0 \\ -1 & \text{if } \theta < 0 \end{cases}$$

Under the null hypothesis $H_0$ (no trend), the variance of $S$ with tie corrections is:
$$\operatorname{Var}(S) = \frac{n(n-1)(2n+5) - \sum_{i=1}^{m} t_i(t_i - 1)(2t_i + 5)}{18}$$

The standard normal test statistic $Z_{\text{MK}}$ is:
$$Z_{\text{MK}} = \begin{cases} \frac{S-1}{\sqrt{\operatorname{Var}(S)}} & \text{if } S > 0 \\ 0 & \text{if } S = 0 \\ \frac{S+1}{\sqrt{\operatorname{Var}(S)}} & \text{if } S < 0 \end{cases}$$

**Statistical Significance Criterion:**  
If the two-tailed $p$-value derived from $Z_{\text{MK}}$ satisfies $p < 0.05$, $H_0$ is rejected, confirming a statistically significant ecological shift with $\ge 95\%$ confidence.

---

## 3. Climatological Z-Score Anomaly Formulation

To capture acute episodic events (such as **Super Cyclone Amphan** in May 2020 and **Cyclone Remal** in May 2024), standard deviations from historical monthly baselines are calculated:

$$Z_t = \frac{X_t - \mu_{\text{month}}}{\sigma_{\text{month}}}$$

Where:
- $X_t$ is the composite NDVI at epoch $t$.
- $\mu_{\text{month}}$ is the multi-year monthly mean for that calendar month.
- $\sigma_{\text{month}}$ is the climatological standard deviation.

A departure of $Z_t \le -2.0$ represents an extreme anomalous disturbance exceeding $97.7\%$ of historical natural variability.

---

## 4. Provenance & Reproducibility Standard

Every analytical execution produces a verifiable cryptographic digest:
$$\text{Digest} = \operatorname{SHA-256}\Big(\text{RunID} \,\|\, \text{DOI} \,\|\, \Delta\text{NDVI} \,\|\, p\text{-value}\Big)$$

This guarantees full scientific auditability: any peer reviewer can feed the generated recipe into an open-source Python environment to inspect raw granules and re-compute identical statistics.
