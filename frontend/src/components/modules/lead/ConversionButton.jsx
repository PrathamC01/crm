import React, { useState } from 'react';
import ConversionWorkflow from './ConversionWorkflow';

const ConversionButton = ({ lead, currentUser, onUpdate }) => {
  const [showWorkflow, setShowWorkflow] = useState(false);

  // Only show for qualified leads that aren't converted
  if (lead.status !== 'Qualified' || lead.converted) {
    return null;
  }

  return (
    <>
      <button
        onClick={() => setShowWorkflow(true)}
        className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <span>Convert to Opportunity</span>
      </button>

      {showWorkflow && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <ConversionWorkflow
            lead={lead}
            currentUser={currentUser}
            onUpdate={() => {
              onUpdate();
              setShowWorkflow(false);
            }}
            onClose={() => setShowWorkflow(false)}
          />
        </div>
      )}
    </>
  );
};

export default ConversionButton;