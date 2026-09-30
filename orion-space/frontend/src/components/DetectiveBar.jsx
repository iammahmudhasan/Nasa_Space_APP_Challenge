import React, { useState } from 'react';
import { Search, Sparkles, Loader2, CornerDownLeft } from 'lucide-react';

const SUGGESTIONS = [
  "Which areas had significant warming in September?",
  "Is temperature correlated with soil wetness in May?",
  "Show climate profile and overview for Sylhet division",
  "How does rainfall trend vary across months in Bangladesh?",
  "Which month has the strongest warming rate?"
];

export default function DetectiveBar({ onQuerySubmit, isLoading }) {
  const [inputVal, setInputVal] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputVal.trim()) {
      onQuerySubmit(inputVal.trim());
    }
  };

  const handleChipClick = (suggestion) => {
    setInputVal(suggestion);
    onQuerySubmit(suggestion);
  };

  return (
    <div className="detective-bar-container">
      <form className="detective-input-row" onSubmit={handleSubmit}>
        <div className="search-icon-wrapper">
          {isLoading ? (
            <Loader2 size={20} className="animate-spin" />
          ) : (
            <Search size={20} />
          )}
        </div>

        <input
          type="text"
          className="detective-input"
          placeholder="Ask the Earth System Trend Detective... (e.g., 'Where is September warming most pronounced?')"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          disabled={isLoading}
          id="detective-query-input"
        />

        <button
          type="submit"
          className="btn btn-primary"
          disabled={isLoading || !inputVal.trim()}
          id="detective-submit-btn"
        >
          <Sparkles size={16} />
          <span>Investigate</span>
          <CornerDownLeft size={14} style={{ opacity: 0.6 }} />
        </button>
      </form>

      <div className="query-chips">
        <span className="query-chip-label">Verified Inquiries:</span>
        {SUGGESTIONS.map((s, idx) => (
          <button
            key={idx}
            type="button"
            className="chip-btn"
            onClick={() => handleChipClick(s)}
            disabled={isLoading}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
