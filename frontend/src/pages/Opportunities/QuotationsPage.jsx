import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const QuotationsPage = () => {
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingQuotation, setEditingQuotation] = useState(null);

  useEffect(() => {
    fetchQuotations();
  }, []);

  const fetchQuotations = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.quotations.getQuotations();
      if (response.data?.data?.quotations) {
        setQuotations(response.data.data.quotations);
      } else {
        setQuotations([]);
      }
    } catch (error) {
      console.error('Error fetching quotations:', error);
      setQuotations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateQuotation = () => {
    setEditingQuotation(null);
    setShowCreateModal(true);
  };

  const handleEditQuotation = (quotation) => {
    setEditingQuotation(quotation);
    setShowCreateModal(true);
  };

  const handleGeneratePDF = (quotation) => {
    console.log('Generating PDF for quotation:', quotation.id);
    // Implement PDF generation
  };

  const columns = [
    { key: 'quotation_number', label: 'Quotation #' },
    { key: 'opportunity_name', label: 'Opportunity' },
    { key: 'customer_name', label: 'Customer' },
    { key: 'total_amount', label: 'Total Amount' },
    { key: 'status', label: 'Status' },
    { key: 'created_at', label: 'Created Date' }
  ];

  const actions = [
    {
      label: 'View',
      onClick: (quotation) => console.log('View quotation:', quotation.id),
      className: 'text-blue-600 hover:text-blue-900'
    },
    {
      label: 'Edit',
      onClick: handleEditQuotation,
      className: 'text-green-600 hover:text-green-900'
    },
    {
      label: 'PDF',
      onClick: handleGeneratePDF,
      className: 'text-purple-600 hover:text-purple-900'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quotations</h1>
          <p className="text-gray-600">Manage and track your sales quotations</p>
        </div>
        <button
          onClick={handleCreateQuotation}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Create Quotation
        </button>
      </div>

      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-8 text-center">
            <LoadingSpinner />
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={quotations}
            actions={actions}
            emptyMessage={quotations.length === 0 ? "No quotations found. Create quotations from opportunities to start generating proposals." : ""}
          />
        )}
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title={editingQuotation ? "Edit Quotation" : "Create New Quotation"}
        size="large"
      >
        <div className="p-6">
          <p className="text-gray-600">
            {editingQuotation ? "Edit quotation form" : "Create quotation form"} will be implemented here.
          </p>
          <div className="flex justify-end space-x-3 mt-4">
            <button
              onClick={() => setShowCreateModal(false)}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={() => setShowCreateModal(false)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              {editingQuotation ? "Update" : "Create"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default QuotationsPage;