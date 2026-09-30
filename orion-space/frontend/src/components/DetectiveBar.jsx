import React, { useRef, useState } from 'react';
import { ArrowUpRight, LoaderCircle, Send } from 'lucide-react';

const SUGGESTIONS = [
  'Where is warming strongest?',
  'How did rainfall change?',
  'Do rain and soil moisture relate?',
];

export default function DetectiveBar({ onQuerySubmit, isLoading, error }) {
  const [inputVal, setInputVal] = useState('');
  const inputRef = useRef(null);

  const submitQuestion = (question) => {
    const cleanQuestion = question.trim();
    if (!cleanQuestion || isLoading) return;
    onQuerySubmit(cleanQuestion);
    setInputVal('');
    if (inputRef.current) inputRef.current.style.height = 'auto';
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    submitQuestion(inputVal);
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      submitQuestion(inputVal);
    }
  };

  const handleInput = (event) => {
    setInputVal(event.target.value);
    event.target.style.height = 'auto';
    event.target.style.height = `${Math.min(event.target.scrollHeight, 160)}px`;
  };

  return (
    <div className="chat-composer-wrap">
      <form className={`chat-composer ${isLoading ? 'is-busy' : ''}`} onSubmit={handleSubmit}>
        <textarea
          ref={inputRef}
          className="question-input"
          placeholder="Ask anything about Bangladesh’s climate…"
          aria-label="Ask Orion about Bangladesh’s climate"
          value={inputVal}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={isLoading}
        />
        <div className="composer-bottom-row">
          <span className="composer-hint"><kbd>Enter</kbd> to ask <span>·</span> <kbd>Shift + Enter</kbd> for a new line</span>
          <span className="composer-data-note">34 mapped locations</span>
          <button type="submit" className="question-submit" disabled={isLoading || !inputVal.trim()} aria-label={isLoading ? 'Orion is reading the data' : 'Send question'}>
            {isLoading ? <LoaderCircle size={17} className="animate-spin" aria-hidden="true" /> : <Send size={17} aria-hidden="true" />}
          </button>
        </div>
      </form>
      {error && <div className="question-error" role="alert">{error}</div>}
      <div className="question-examples" aria-label="Example questions">
        <span className="examples-label">TRY ASKING</span>
        {SUGGESTIONS.map((suggestion) => (
          <button type="button" key={suggestion} onClick={() => submitQuestion(suggestion)} disabled={isLoading}>
            {suggestion}<ArrowUpRight size={13} aria-hidden="true" />
          </button>
        ))}
      </div>
    </div>
  );
}
