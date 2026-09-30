import React from 'react';
import { ChevronDown, CloudRain, Droplets, SlidersHorizontal, Sun, Thermometer } from 'lucide-react';

const VARIABLES = [
  { id: 'T2M', label: 'Temperature', short: 'T2M', icon: Thermometer },
  { id: 'PRECTOTCORR', label: 'Rainfall', short: 'RAIN', icon: CloudRain },
  { id: 'GWETTOP', label: 'Soil moisture', short: 'SOIL', icon: Droplets },
  { id: 'ALLSKY_SFC_SW_DWN', label: 'Sunlight', short: 'SUN', icon: Sun },
];

const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const SIGNIFICANCE_OPTIONS = [
  ['fdr', 'Corrected', 'Keeps results that remain significant after multiple-test correction.'],
  ['raw', 'Uncorrected', 'Uses the raw p-value threshold before correction.'],
  ['all', 'All cells', 'Shows every grid cell, including results without a significant trend.'],
];
const METHOD_OPTIONS = [
  ['OLS', 'Linear fit', 'A fitted line summarizes the overall trend.'],
  ['Mann-Kendall', 'Robust slope', 'Sen’s slope is less sensitive to outliers.'],
];

function ChoiceGroup({ label, value, setValue, options }) {
  return (
    <fieldset className="settings-group">
      <legend>{label}</legend>
      <div className="settings-options">
        {options.map(([optionValue, optionLabel, description]) => (
          <button
            type="button"
            key={optionValue}
            className={`settings-choice ${value === optionValue ? 'selected' : ''}`}
            aria-pressed={value === optionValue}
            title={description}
            onClick={() => setValue(optionValue)}
          >
            {optionLabel}
          </button>
        ))}
      </div>
      <p>{options.find(([optionValue]) => optionValue === value)?.[2]}</p>
    </fieldset>
  );
}

export default function ControlPanel({
  selectedVariable,
  setSelectedVariable,
  selectedMonth,
  setSelectedMonth,
  selectedDivision = 'All Bangladesh',
  setSelectedDivision = () => {},
  sigFilter,
  setSigFilter,
  testType,
  setTestType,
  divisions = [],
  isUpdating = false,
}) {
  const divisionOptions = divisions.includes('All Bangladesh') ? divisions : ['All Bangladesh', ...divisions];
  const selectedSignificance = SIGNIFICANCE_OPTIONS.find(([value]) => value === sigFilter)?.[1] || 'Corrected';
  const selectedMethod = METHOD_OPTIONS.find(([value]) => value === testType)?.[1] || 'Linear fit';

  return (
    <section className="explore-controls" aria-label="Choose the climate data to explore">
      <div className="controls-heading">
        <div>
          <h2>Choose what to explore</h2>
          <p>Pick a measure and month. The map and results update together.</p>
        </div>
        <span className={`update-status ${isUpdating ? 'updating' : ''}`} role="status" aria-live="polite">
          <i aria-hidden="true" />{isUpdating ? 'Updating results' : '34 grid locations'}
        </span>
      </div>

      <div className="controls-primary">
        <div className="variable-control">
          <span className="control-caption">Climate measure</span>
          <div className="variable-picker" role="group" aria-label="Climate measure">
            {VARIABLES.map(({ id, label, short, icon: Icon }) => (
              <button
                type="button"
                key={id}
                className={`variable-option ${selectedVariable === id ? 'active' : ''}`}
                aria-pressed={selectedVariable === id}
                onClick={() => setSelectedVariable(id)}
              >
                <Icon size={17} strokeWidth={1.8} aria-hidden="true" />
                <span>{label}</span>
                <small>{short}</small>
              </button>
            ))}
          </div>
        </div>

        <label className="filter-select">
          <span className="control-caption">Month</span>
          <select value={selectedMonth} onChange={(event) => setSelectedMonth(Number(event.target.value))}>
            {MONTH_NAMES.map((name, index) => <option key={name} value={index + 1}>{name}</option>)}
          </select>
        </label>

        <label className="filter-select region-select">
          <span className="control-caption">Region</span>
          <select value={selectedDivision} onChange={(event) => setSelectedDivision(event.target.value)}>
            {divisionOptions.map((name) => <option key={name} value={name}>{name}</option>)}
          </select>
        </label>
      </div>

      <details className="advanced-settings">
        <summary>
          <span><SlidersHorizontal size={15} aria-hidden="true" /> Advanced analysis</span>
          <span className="settings-current">{selectedSignificance} · {selectedMethod}</span>
          <ChevronDown size={15} className="settings-chevron" aria-hidden="true" />
        </summary>
        <div className="settings-content">
          <ChoiceGroup label="Significance" value={sigFilter} setValue={setSigFilter} options={SIGNIFICANCE_OPTIONS} />
          <ChoiceGroup label="Trend method" value={testType} setValue={setTestType} options={METHOD_OPTIONS} />
        </div>
      </details>
    </section>
  );
}