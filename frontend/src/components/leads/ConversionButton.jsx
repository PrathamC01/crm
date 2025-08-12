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
        className="text-purple-600 hover:text-purple-900"
      >
        <span>Convert</span>
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