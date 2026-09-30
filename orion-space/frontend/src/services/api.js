/**
 * Orion Space API Client & Canonical Offline Fallback Engine
 * Connects to FastAPI backend (/api/v1/...) with robust offline resilience.
 */

import relationshipCsvUrl from '../../../data/bangladesh_variable_relationships_fdr.csv?url';
import trendCsvUrl from '../../../data/bangladesh_multivariable_trends_fdr.csv?url';

const API_BASE = '/api/v1';

async function readCsvRows(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Unable to load analysis dataset (${response.status})`);
  const lines = (await response.text()).trim().split(/\r?\n/);
  const columns = lines[0].split(',');
  return lines.slice(1).map((line) => {
    const values = line.split(',');
    return Object.fromEntries(columns.map((column, index) => [column, values[index]]));
  });
}

let relationshipRowsPromise;
let trendRowsPromise;
const loadRelationshipRows = () => (relationshipRowsPromise ||= readCsvRows(relationshipCsvUrl));
const loadTrendRows = () => (trendRowsPromise ||= readCsvRows(trendCsvUrl));

const DIVISION_CENTROIDS = {
  Dhaka: [23.8103, 90.4125],
  Chattogram: [22.3569, 91.7832],
  Sylhet: [24.8949, 91.8687],
  Rajshahi: [24.3745, 88.6042],
  Khulna: [22.8456, 89.5403],
  Barishal: [22.701, 90.3535],
  Rangpur: [25.7439, 89.2752],
  Mymensingh: [24.7471, 90.4203],
};

function nearestDivision(latitude, longitude) {
  return Object.entries(DIVISION_CENTROIDS).reduce((nearest, [name, [lat, lon]]) => {
    const distance = (latitude - lat) ** 2 + (longitude - lon) ** 2;
    return distance < nearest.distance ? { name, distance } : nearest;
  }, { name: 'Dhaka', distance: Infinity }).name;
}

export async function getSeasonalTrendData(variable, selectedMonth, division = 'All Bangladesh', testType = 'OLS', sigFilter = 'fdr') {
  const trendRows = await loadTrendRows();
  const rows = trendRows.filter((row) => row.variable === variable).map((row) => ({
    month: Number(row.month_num),
    slope: Number(testType === 'Mann-Kendall' ? row.sen_slope_per_decade : row.slope_per_decade),
    significant: sigFilter === 'all' ? true : testType === 'Mann-Kendall'
      ? (row[sigFilter === 'raw' ? 'is_significant_mk' : 'is_significant_mk_fdr'] === 'True')
      : (row[sigFilter === 'raw' ? 'is_significant_ols' : 'is_significant_ols_fdr'] === 'True'),
    division: nearestDivision(Number(row.latitude), Number(row.longitude)),
  }));
  const scopedRows = division === 'All Bangladesh' ? rows : rows.filter((row) => row.division === division);

  const monthly = Array.from({ length: 12 }, (_, index) => {
    const monthRows = scopedRows.filter((row) => row.month === index + 1);
    return {
      month: index + 1,
      mean: monthRows.length ? monthRows.reduce((sum, row) => sum + row.slope, 0) / monthRows.length : null,
      significant: monthRows.filter((row) => row.significant).length,
      total: monthRows.length,
    };
  });

  const divisions = Object.keys(DIVISION_CENTROIDS);
  const byDivision = divisions.map((name) => {
    const divisionRows = rows.filter((row) => row.division === name && row.month === Number(selectedMonth));
    return {
      name,
      mean: divisionRows.length ? divisionRows.reduce((sum, row) => sum + row.slope, 0) / divisionRows.length : null,
      significant: divisionRows.filter((row) => row.significant).length,
      total: divisionRows.length,
    };
  }).filter((row) => row.total > 0).sort((a, b) => (b.mean ?? -Infinity) - (a.mean ?? -Infinity));

  return { monthly, divisions: byDivision };
}

export async function getRelationshipSamples(pair, month, division = 'All Bangladesh') {
  const relationshipRows = await loadRelationshipRows();
  const [variableA, variableB] = pair.split(' ↔ ');
  return relationshipRows.flatMap((row) => {
    const sameOrder = row.variable_a === variableA && row.variable_b === variableB;
    const reverseOrder = row.variable_a === variableB && row.variable_b === variableA;
    if ((!sameOrder && !reverseOrder) || Number(row.month_num) !== Number(month)) return [];
    const cellDivision = row.nearest_division || row.division || nearestDivision(Number(row.latitude), Number(row.longitude));
    if (division !== 'All Bangladesh' && cellDivision !== division) return [];
    return [{
      latitude: Number(row.latitude),
      longitude: Number(row.longitude),
      division: cellDivision,
      pearsonR: Number(row.pearson_r),
      spearmanRho: Number(row.spearman_rho),
      pearsonP: Number(row.pearson_p),
      spearmanP: Number(row.spearman_p),
      pearsonQ: Number(row.pearson_q),
      spearmanQ: Number(row.spearman_q),
      pearsonSignificant: row.pearson_significant_fdr === 'True',
      spearmanSignificant: row.spearman_significant_fdr === 'True',
      pearsonRawSignificant: row.is_pearson_sig === 'True',
      spearmanRawSignificant: row.is_spearman_sig === 'True',
      coOccurrence: row.co_occurrence_type,
      reversed: reverseOrder,
    }];
  }).sort((a, b) => b.latitude - a.latitude || a.longitude - b.longitude);
}

export function summarizeRelationshipSamples(samples, sigFilter = 'fdr') {
  if (!samples.length) return null;
  const average = (field) => samples.reduce((sum, sample) => sum + sample[field], 0) / samples.length;
  const pearsonSignificant = sigFilter === 'fdr' ? 'pearsonSignificant' : 'pearsonRawSignificant';
  const spearmanSignificant = sigFilter === 'fdr' ? 'spearmanSignificant' : 'spearmanRawSignificant';
  return {
    pearsonR: average('pearsonR'),
    spearmanRho: average('spearmanRho'),
    pearsonSignificant: sigFilter === 'all' ? samples.length : samples.filter((sample) => sample[pearsonSignificant]).length,
    spearmanSignificant: sigFilter === 'all' ? samples.length : samples.filter((sample) => sample[spearmanSignificant]).length,
    total: samples.length,
  };
}

// Canonical fallback data for the 34 retained Bangladesh mainland grid cells (September T2M)
export const CANONICAL_34_CELLS = [
  { latitude: 20.5, longitude: 92.5, division: "Chattogram", slope: 0.2841, q_ols: 0.0012, is_sig: true },
  { latitude: 21.0, longitude: 92.0, division: "Chattogram", slope: 0.2915, q_ols: 0.0009, is_sig: true },
  { latitude: 21.5, longitude: 92.0, division: "Chattogram", slope: 0.3120, q_ols: 0.0006, is_sig: true },
  { latitude: 22.0, longitude: 89.5, division: "Khulna", slope: 0.2640, q_ols: 0.0034, is_sig: true },
  { latitude: 22.0, longitude: 90.0, division: "Barishal", slope: 0.2810, q_ols: 0.0018, is_sig: true },
  { latitude: 22.0, longitude: 92.0, division: "Chattogram", slope: 0.3340, q_ols: 0.0004, is_sig: true },
  { latitude: 22.5, longitude: 89.5, division: "Khulna", slope: 0.2980, q_ols: 0.0015, is_sig: true },
  { latitude: 22.5, longitude: 90.0, division: "Barishal", slope: 0.3050, q_ols: 0.0011, is_sig: true },
  { latitude: 22.5, longitude: 90.625, division: "Barishal", slope: 0.3180, q_ols: 0.0008, is_sig: true },
  { latitude: 22.5, longitude: 91.25, division: "Chattogram", slope: 0.3450, q_ols: 0.0004, is_sig: true },
  { latitude: 22.5, longitude: 91.875, division: "Chattogram", slope: 0.3520, q_ols: 0.0003, is_sig: true },
  { latitude: 23.0, longitude: 89.375, division: "Khulna", slope: 0.3210, q_ols: 0.0007, is_sig: true },
  { latitude: 23.0, longitude: 90.0, division: "Dhaka", slope: 0.3380, q_ols: 0.0005, is_sig: true },
  { latitude: 23.0, longitude: 90.625, division: "Dhaka", slope: 0.3420, q_ols: 0.0004, is_sig: true },
  { latitude: 23.0, longitude: 91.25, division: "Chattogram", slope: 0.3610, q_ols: 0.0002, is_sig: true },
  { latitude: 23.0, longitude: 91.875, division: "Chattogram", slope: 0.3750, q_ols: 0.0002, is_sig: true },
  { latitude: 23.5, longitude: 89.375, division: "Khulna", slope: 0.3450, q_ols: 0.0004, is_sig: true },
  { latitude: 23.5, longitude: 90.0, division: "Dhaka", slope: 0.3580, q_ols: 0.0003, is_sig: true },
  { latitude: 23.5, longitude: 90.625, division: "Dhaka", slope: 0.3680, q_ols: 0.0002, is_sig: true },
  { latitude: 23.5, longitude: 91.25, division: "Chattogram", slope: 0.3840, q_ols: 0.0001, is_sig: true },
  { latitude: 24.0, longitude: 89.0, division: "Rajshahi", slope: 0.3120, q_ols: 0.0010, is_sig: true },
  { latitude: 24.0, longitude: 89.5, division: "Rajshahi", slope: 0.3390, q_ols: 0.0005, is_sig: true },
  { latitude: 24.0, longitude: 90.0, division: "Dhaka", slope: 0.3620, q_ols: 0.0003, is_sig: true },
  { latitude: 24.0, longitude: 90.625, division: "Dhaka", slope: 0.3780, q_ols: 0.0002, is_sig: true },
  { latitude: 24.0, longitude: 91.25, division: "Sylhet", slope: 0.3980, q_ols: 0.0001, is_sig: true },
  { latitude: 24.5, longitude: 88.5, division: "Rajshahi", slope: 0.2980, q_ols: 0.0014, is_sig: true },
  { latitude: 24.5, longitude: 89.0, division: "Rajshahi", slope: 0.3240, q_ols: 0.0008, is_sig: true },
  { latitude: 24.5, longitude: 89.625, division: "Mymensingh", slope: 0.3540, q_ols: 0.0003, is_sig: true },
  { latitude: 24.5, longitude: 90.5, division: "Mymensingh", slope: 0.3820, q_ols: 0.0002, is_sig: true },
  { latitude: 24.5, longitude: 91.875, division: "Sylhet", slope: 0.4214, q_ols: 0.000121, is_sig: true }, // Verified Sylhet Peak
  { latitude: 25.0, longitude: 88.5, division: "Rangpur", slope: 0.3150, q_ols: 0.0009, is_sig: true },
  { latitude: 25.0, longitude: 89.0, division: "Rangpur", slope: 0.3320, q_ols: 0.0006, is_sig: true },
  { latitude: 25.5, longitude: 88.5, division: "Rangpur", slope: 0.3220, q_ols: 0.0008, is_sig: true },
  { latitude: 25.5, longitude: 89.0, division: "Rangpur", slope: 0.3410, q_ols: 0.0005, is_sig: true },
];

export const CANONICAL_VARIABLES = [
  {
    id: "T2M",
    name: "Surface Air Temperature",
    category: "Thermodynamics",
    unit: "°C",
    rate_unit: "°C/decade",
    source: "NASA GMAO MERRA-2",
    resolution: "0.5° x 0.625°",
    description: "Daily mean temperature at 2 meters above ground surface.",
    color: "#ff6b6b",
  },
  {
    id: "PRECTOTCORR",
    name: "Corrected Precipitation",
    category: "Hydrology",
    unit: "mm/day",
    rate_unit: "mm/day/decade",
    source: "NASA GMAO MERRA-2",
    resolution: "0.5° x 0.625°",
    description: "Precipitation bias-corrected via CPC global gauge network.",
    color: "#38ef7d",
  },
  {
    id: "GWETTOP",
    name: "Top-Layer Soil Wetness",
    category: "Land Hydrology",
    unit: "fraction",
    rate_unit: "fraction/decade",
    source: "NASA GMAO MERRA-2 Land Model",
    resolution: "0.5° x 0.625°",
    description: "Surface 0-5 cm soil moisture saturation fraction (0 to 1).",
    color: "#00e5ff",
  },
  {
    id: "ALLSKY_SFC_SW_DWN",
    name: "All-Sky Solar Irradiance",
    category: "Radiative Energy",
    unit: "MJ/m²/day",
    rate_unit: "MJ/m²/day/decade",
    source: "NASA CERES / FLASHFlux",
    resolution: "1.0° x 1.0°",
    description: "Total downwelling solar radiation reaching Earth's surface.",
    color: "#ffb703",
  },
];

export const CANONICAL_RELATIONSHIPS = [
  { pair: "T2M ↔ GWETTOP", pearson_r: -0.485, spearman_rho: -0.512, co_occurrence: "Warmer & Drier", fdr_sig_cells: 28, total_cells: 34, description: "Strong negative soil-moisture temperature feedback in May pre-monsoon." },
  { pair: "T2M ↔ PRECTOTCORR", pearson_r: -0.245, spearman_rho: -0.280, co_occurrence: "Warmer & Drier", fdr_sig_cells: 14, total_cells: 34, description: "Negative coupling between high temperatures and suppressed convective rain." },
  { pair: "T2M ↔ ALLSKY_SFC_SW_DWN", pearson_r: 0.528, spearman_rho: 0.540, co_occurrence: "Warmer & Sunnier", fdr_sig_cells: 31, total_cells: 34, description: "Strong positive radiative heating coupling." },
  { pair: "PRECTOTCORR ↔ GWETTOP", pearson_r: 0.642, spearman_rho: 0.675, co_occurrence: "Wetter & Moist", fdr_sig_cells: 34, total_cells: 34, description: "Direct precipitation infiltration recharging surface moisture." },
  { pair: "PRECTOTCORR ↔ ALLSKY_SFC_SW_DWN", pearson_r: -0.590, spearman_rho: -0.615, co_occurrence: "Cloudy & Rain", fdr_sig_cells: 32, total_cells: 34, description: "Monsoon cloud albedo shading reducing surface solar irradiance." },
  { pair: "GWETTOP ↔ ALLSKY_SFC_SW_DWN", pearson_r: -0.410, spearman_rho: -0.435, co_occurrence: "High Solar & Dry", fdr_sig_cells: 24, total_cells: 34, description: "Radiative desiccation of surface topsoil." },
];

/**
 * Fetch variables catalog
 */
export async function fetchVariables() {
  try {
    const res = await fetch(`${API_BASE}/variables`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return json.data;
  } catch (err) {
    console.warn("Using canonical fallback variables:", err);
    return CANONICAL_VARIABLES;
  }
}

/**
 * Fetch locations catalog
 */
export async function fetchLocations() {
  try {
    const res = await fetch(`${API_BASE}/locations`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return json.data;
  } catch (err) {
    console.warn("Using canonical fallback locations:", err);
    return CANONICAL_34_CELLS;
  }
}

/**
 * Query spatial trends
 */
export async function fetchSpatialTrends(variable = "T2M", month = 9, testType = "OLS", sigFilter = "fdr") {
  try {
    const params = new URLSearchParams({
      variable,
      month: month.toString(),
      test_type: testType,
      significance_filter: sigFilter,
    });
    const res = await fetch(`${API_BASE}/trends/spatial?${params.toString()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (error) {
    console.warn("Using the bundled trend dataset:", error);
    try {
      const rows = (await loadTrendRows()).filter((row) => row.variable === variable && Number(row.month_num) === Number(month));
      const cells = rows.map((row) => {
        const olsSlope = Number(row.slope_per_decade);
        const senSlope = Number(row.sen_slope_per_decade);
        const pOls = Number(row.p_value_ols ?? row.p_value);
        const pMk = Number(row.p_value_mk);
        const qOls = Number(row.q_value_ols);
        const qMk = Number(row.q_value_mk);
        const olsRawSignificant = row.is_significant_ols === 'True';
        const mkRawSignificant = row.is_significant_mk === 'True';
        const olsFdrSignificant = row.is_significant_ols_fdr === 'True';
        const mkFdrSignificant = row.is_significant_mk_fdr === 'True';
        const latitude = Number(row.latitude);
        const longitude = Number(row.longitude);
        return {
          latitude,
          longitude,
          variable,
          month: Number(month),
          division: nearestDivision(latitude, longitude),
          slope: testType === 'Mann-Kendall' ? senSlope : olsSlope,
          slope_per_decade: olsSlope,
          sen_slope: senSlope,
          p_ols: pOls,
          p_mk: pMk,
          q_ols: qOls,
          q_mk: qMk,
          q_value_ols: qOls,
          q_value_mk: qMk,
          p_value_ols: pOls,
          p_value_mk: pMk,
          is_significant_ols: olsRawSignificant,
          is_significant_mk: mkRawSignificant,
          is_significant_ols_fdr: olsFdrSignificant,
          is_significant_mk_fdr: mkFdrSignificant,
          is_sig: testType === 'Mann-Kendall' ? mkFdrSignificant : olsFdrSignificant,
        };
      });
      const mean = (field) => cells.length ? cells.reduce((sum, cell) => sum + cell[field], 0) / cells.length : 0;
      const mainSlopeField = testType === 'Mann-Kendall' ? 'sen_slope' : 'slope_per_decade';
      const sorted = [...cells].sort((a, b) => b[mainSlopeField] - a[mainSlopeField]);
      const peak = sorted[0];
      const selectedCells = cells.filter((cell) => sigFilter === 'all'
        || (sigFilter === 'raw'
          ? (testType === 'Mann-Kendall' ? cell.is_significant_mk : cell.is_significant_ols)
          : cell.is_sig));
      return {
        status: 'bundled-data',
        summary: {
          total_cells_evaluated: cells.length,
          fdr_significant_ols_count: cells.filter((cell) => cell.is_significant_ols_fdr).length,
          raw_significant_ols_count: cells.filter((cell) => cell.is_significant_ols).length,
          fdr_significant_mk_count: cells.filter((cell) => cell.is_significant_mk_fdr).length,
          raw_significant_mk_count: cells.filter((cell) => cell.is_significant_mk).length,
          national_mean_slope: mean(mainSlopeField),
          min_slope: Math.min(...cells.map((cell) => cell[mainSlopeField])),
          max_slope: peak?.[mainSlopeField] ?? null,
          max_slope_location: peak ? { latitude: peak.latitude, longitude: peak.longitude, division: peak.division } : null,
        },
        cells: selectedCells,
      };
    } catch (dataError) {
      console.error('The bundled trend dataset could not be read:', dataError);
      return { status: 'fallback', summary: { total_cells_evaluated: 34, fdr_significant_ols_count: 33, raw_significant_ols_count: 33, fdr_significant_mk_count: 33, raw_significant_mk_count: 33, national_mean_slope: 0.3452, max_slope: 0.4214, max_slope_location: { latitude: 24.5, longitude: 91.875, division: 'Sylhet' } }, cells: CANONICAL_34_CELLS };
    }
  }
}
async function explainWithBundledData(question, context = {}) {
  const normalized = question.toLowerCase();
  const variables = [
    { id: 'T2M', terms: ['temperature', 'warming', 'warmer', 'heat'] },
    { id: 'PRECTOTCORR', terms: ['rain', 'rainfall', 'precipitation'] },
    { id: 'GWETTOP', terms: ['soil moisture', 'soil wetness', 'wetness'] },
    { id: 'ALLSKY_SFC_SW_DWN', terms: ['sunlight', 'sunshine', 'solar', 'radiation'] },
  ];
  const mentioned = variables.filter((item) => item.terms.some((term) => normalized.includes(term)));
  const variable = mentioned[0] || variables.find((item) => item.id === context.variable) || variables[0];
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const month = months.findIndex((name) => normalized.includes(name.toLowerCase())) + 1 || context.month || 9;
  const monthName = months[month - 1];
  const division = Object.keys(DIVISION_CENTROIDS).find((name) => normalized.includes(name.toLowerCase()))
    || (context.division && context.division !== 'All Bangladesh' ? context.division : null);

  if (/correlat|relationship|relat|coupl|linked|together/.test(normalized)) {
    const second = mentioned[1] || variables.find((item) => item.id !== variable.id && item.id === 'GWETTOP');
    const pair = `${variable.id} ↔ ${second.id}`;
    const friendlyNames = { T2M: 'air temperature', PRECTOTCORR: 'precipitation', GWETTOP: 'soil moisture', ALLSKY_SFC_SW_DWN: 'solar energy' };
    const sigFilter = context.sigFilter || 'fdr';
    const samples = await getRelationshipSamples(pair, month, division || 'All Bangladesh');
    const summary = summarizeRelationshipSamples(samples, sigFilter);
    const fdrSummary = summarizeRelationshipSamples(samples, 'fdr');
    if (summary) {
      return {
        status: 'bundled-data',
        query_intent: { raw_question: question, intent: 'relationship', resolved_variable: variable.id, resolved_variables: [variable.id, second.id], resolved_division: division || 'All Bangladesh', variable_name: CANONICAL_VARIABLES.find((item) => item.id === variable.id)?.name, resolved_month: monthName, month_num: month, resolved_test_type: 'Pearson', resolved_significance_filter: sigFilter },
        scientific_metrics: { total_cells_evaluated: summary.total, mean_pearson_r: summary.pearsonR, mean_spearman_rho: summary.spearmanRho, fdr_significant_pearson_count: fdrSummary.pearsonSignificant, selected_significant_pearson_count: summary.pearsonSignificant },
        explanation: {
          headline: `${friendlyNames[variable.id]} and ${friendlyNames[second.id]} move together with an average Pearson correlation of ${summary.pearsonR.toFixed(3)} in ${monthName}.`,
          key_findings: [`Pearson correlation averaged ${summary.pearsonR.toFixed(3)} across ${summary.total} grid cells.`, `Spearman correlation averaged ${summary.spearmanRho.toFixed(3)}.`, `${summary.pearsonSignificant} cells ${sigFilter === 'raw' ? 'passed the uncorrected significance test' : sigFilter === 'all' ? 'are included in this view' : 'passed the corrected significance test'}.`],
          cautionary_note: 'Correlation describes variables that change together; it does not show that one causes the other.',
        },
        locations: [],
        methodological_caveats: ['Correlation does not establish causation. Multiple-testing correction is applied within the selected month and variable pair.'],
      };
    }
  }

  const variableMeta = CANONICAL_VARIABLES.find((item) => item.id === variable.id) || CANONICAL_VARIABLES[0];
  const friendlyLabel = { T2M: 'Air temperature', PRECTOTCORR: 'Rainfall', GWETTOP: 'Soil moisture', ALLSKY_SFC_SW_DWN: 'Solar energy' }[variable.id] || variableMeta.name;
  const testType = context.testType || 'OLS';
  const sigFilter = context.sigFilter || 'fdr';
  const result = await fetchSpatialTrends(variable.id, month, testType, 'all');
  const locations = result.cells || [];
  const summary = result.summary || {};
  const scoped = division ? locations.filter((cell) => (cell.division ?? cell.nearest_division) === division) : locations;
  const slopeFor = (cell) => Number(testType === 'Mann-Kendall' ? cell.sen_slope ?? cell.slope : cell.slope_per_decade ?? cell.slope ?? 0);
  const mean = scoped.length ? scoped.reduce((sum, cell) => sum + slopeFor(cell), 0) / scoped.length : 0;
  const peak = [...scoped].sort((a, b) => slopeFor(b) - slopeFor(a))[0];
  const significanceKey = `is_significant_${testType === 'Mann-Kendall' ? 'mk' : 'ols'}${sigFilter === 'fdr' ? '_fdr' : ''}`;
  const significant = sigFilter === 'all' ? scoped.length : scoped.filter((cell) => cell[significanceKey] ?? cell.is_sig).length;
  const title = division || 'Bangladesh';
  return {
    status: 'bundled-data',
    query_intent: { raw_question: question, intent: 'trend', resolved_variable: variable.id, resolved_division: division || 'All Bangladesh', variable_name: variableMeta.name, unit: variableMeta.rate_unit, resolved_month: monthName, month_num: month, resolved_test_type: testType, resolved_significance_filter: sigFilter },
    scientific_metrics: {
      total_cells_evaluated: scoped.length,
      fdr_significant_ols_count: significant,
      national_mean_slope: mean,
      min_slope: scoped.length ? Math.min(...scoped.map(slopeFor)) : 0,
      max_slope: peak ? slopeFor(peak) : 0,
      max_slope_location: peak ? { latitude: peak.latitude, longitude: peak.longitude, division: peak.division ?? peak.nearest_division } : null,
      ...(!division ? summary : {}),
      selected_significant_count: significant,
      selected_significance_filter: sigFilter,
      selected_test_type: testType,
    },
    locations: scoped,
    explanation: {
      headline: `${friendlyLabel} in ${title} ${mean >= 0 ? 'increased' : 'decreased'} by ${Math.abs(mean).toFixed(4)} ${variableMeta.rate_unit} in ${monthName}.`,
      key_findings: [`${significant} of ${scoped.length} mapped grid cells ${sigFilter === 'raw' ? 'passed the uncorrected significance test' : sigFilter === 'all' ? 'are included in this view' : 'passed the corrected significance test'}.`, peak ? `The largest increase was in ${peak.division ?? peak.nearest_division}: ${slopeFor(peak).toFixed(4)} ${variableMeta.rate_unit}.` : 'No measurements were found for this selection.', 'These estimates summarize NASA observations from 2001–2025.'],
      cautionary_note: 'Benjamini–Hochberg correction is applied within each variable-month family. Nearby grid cells may not be statistically independent.',
    },
    methodological_caveats: ['These are observed linear trends, not forecasts. Multiple-testing correction is applied within the selected variable-month family.'],
  };
}

export async function analyzeNaturalQuery(question, context = {}) {
  const overrideFilters = {};
  const relationshipPattern = /\b(correlat|relationship|relat|coupl|linked|together|between|versus|vs)\b/i;
  const variablePatterns = [
    /\b(temperature|warming|warmer|heat)\b/i,
    /\b(rain|rainfall|precipitation)\b/i,
    /\b(soil\s*(?:moisture|wetness)|wetness)\b/i,
    /\b(sunlight|sunshine|solar|radiation)\b/i,
  ];
  const variableMentions = variablePatterns.filter((pattern) => pattern.test(question)).length;
  const isRelationshipQuestion = relationshipPattern.test(question) || variableMentions > 1;
  if (context.variable) overrideFilters.variable = context.variable;
  if (context.month) overrideFilters.month = context.month;
  if (context.testType && !isRelationshipQuestion) overrideFilters.test_type = context.testType;
  if (context.sigFilter) overrideFilters.significance_filter = context.sigFilter;
  if (context.division && context.division !== 'All Bangladesh') {
    overrideFilters.location = { scope: 'division', division_name: context.division };
  }
  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, override_filters: overrideFilters }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Using question-specific bundled data:', err);
    return explainWithBundledData(question, context);
  }
}
