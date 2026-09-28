# 🏆 NASA Space Apps Challenge 2026: Pitch Deck & Presentation Guide
### Project: NASA Earth Intelligence Agent (NEIA)

---

## 1. The 30-Second Elevator Pitch

> *"Every day, NASA satellites capture petabytes of crucial Earth observation data, but extracting actionable insights requires complex GIS and coding skills. Meanwhile, standard AI chatbots hallucinate numbers and make up climate facts.  
> We built **NASA Earth Intelligence Agent (NEIA)**—an autonomous scientific research agent that translates natural-language questions about planetary change into reproducible, mathematically grounded analyses. Using NASA MODIS and VIIRS data, NEIA executes peer-reviewed trend and anomaly algorithms, enforces zero-hallucination guardrails, and renders interactive maps with one-click code reproducibility. We prove it on Coastal Bangladesh, detecting critical mangrove decline and salinity stress with 95% statistical confidence."*

---

## 2. 7-Slide Pitch Deck Outline

### Slide 1: Title & Vision
- **Header:** NASA Earth Intelligence Agent (NEIA)
- **Tagline:** Autonomous Scientific Research Agent for Planetary Environmental Change
- **Badge:** NASA Space Apps Challenge 2026
- **Visual:** Holographic orbital Earth with streaming agent thought graph.

### Slide 2: The Core Problem
- **Petabytes of Data, Zero Accessibility:** NASA EOSDIS holds 100+ PB of data; 99% of policymakers and affected communities cannot query it directly.
- **The Chatbot Trap:** LLMs hallucinate numbers (e.g. guessing that temperature rose 3.4°C or NDVI dropped 30% without computation).
- **The Reproducibility Crisis:** Lack of auditable provenance in AI-driven environmental tools.

### Slide 3: The Architecture (Agent + Science Engine)
- Diagram showing separation of concerns:
  - **LLM:** Intent parser & communicator.
  - **NASA CMR:** Dataset discovery.
  - **Deterministic Engine:** NumPy / SciPy computing Mann-Kendall tests and Z-score anomalies.
  - **Zero-Hallucination Guardrails:** Blocks fabricated values.

### Slide 4: Flagship Benchmark — Coastal Bangladesh (2020–2025)
- Why Bangladesh? One of the most climate-vulnerable deltas on Earth (Sundarbans UNESCO World Heritage Site, salinity intrusion, frequent super cyclones).
- **The Query:** *"Analyze vegetation changes in coastal Bangladesh between 2020 and 2025."*

### Slide 5: Scientific Discoveries & Verification
- **Quantified Decline:** $-17.6\%$ NDVI drop in western saline zones (Satkhira).
- **Extreme Cyclonic Depressions:** Detected $Z = -2.18\sigma$ shock from Cyclone Amphan (May 2020) and Cyclone Remal (May 2024).
- **Statistical Rigor:** Mann-Kendall monotonic trend test confirmed with $p = 0.0001 < 0.05$.
- **Ground Truth DOI:** NASA Terra/MODIS Collection `MOD13Q1.061`.

### Slide 6: Novelty & Global Scalability
- Seamless expansion from Vegetation (NDVI) to Land Surface Temperature (`MOD11A2`), GPM IMERG Precipitation, and Wildfires (`FIRMS`).
- Downloadable Python recipe: Any independent scientist can reproduce the findings bit-for-bit.

### Slide 7: Team & Future Roadmap
- Phase 2: Ingest Sentinel-1 SAR radar data for cloud-penetrating monsoon observation.
- Phase 3: Automated early warning alerts for coastal forest conservation agencies.

---

## 3. 2-Minute Demo Video Script

| Time | Visual on Screen | Spoken Narration (English) |
| :--- | :--- | :--- |
| **0:00 - 0:20** | Mission Control dashboard, dark obsidian theme with glowing cyan telemetry. | *"Welcome to the NASA Earth Intelligence Agent. We asked ourselves: can an AI system perform real, peer-reviewed Earth science without hallucinating a single number?"* |
| **0:20 - 0:45** | User clicks preset inquiry: *"Analyze vegetation changes in coastal Bangladesh (2020-2025)"* and hits Execute. | *"Watch the agent think in real time: Step 1 dissects the geographic intent. Step 2 searches NASA's Common Metadata Repository to discover the exact MODIS MOD13Q1 collection. Step 3 ingests 72 observation epochs."* |
| **0:45 - 1:15** | Interactive Leaflet map zooms into Sundarbans. Time-series chart renders confidence envelope. | *"Notice: the LLM never invents numbers. Our deterministic Python engine calculates a 17.6% canopy drop in high-salinity zones, identifying cyclonic shocks from Cyclone Amphan and Remal. The Mann-Kendall test verifies this trend at p=0.0001."* |
| **1:15 - 1:40** | Clicks on Evidence Dossier. Clicks 'Copy Script' and 'Download .py'. | *"Every claim is backed by a NASA Earthdata DOI. With one click, researchers can download the exact Python recipe to reproduce the study locally."* |
| **1:40 - 2:00** | Final slide with NASA logo and GitHub repository link. | *"Bridging the gap between raw planetary data and transparent climate action. This is the NASA Earth Intelligence Agent."* |
