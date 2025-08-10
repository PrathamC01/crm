import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const UOMsPage = () => {
  const [uoms, setUoms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingUom, setEditingUom] = useState(null);

  useEffect(() => {
    fetchUoms();
  }, []);

  const fetchUoms = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.masters.getUOMs();
      if (response.data?.data?.uoms) {
        setUoms(response.data.data.uoms);
      } else {
        setUoms([]);
      }
    } catch (error) {
      console.error('Error fetching UOMs:', error);
      setUoms([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUom = () => {
    setEditingUom(null);
    setShowCreateModal(true);
  };

  const handleEditUom = (uom) => {
    setEditingUom(uom);
    setShowCreateModal(true);
  };

  const columns = [
    { key: 'uom_name', label: 'UOM Name' },
    { key: 'uom_code', label: 'UOM Code' },
    { key: 'base_unit', label: 'Base Unit' },
    { key: 'conversion_factor_to_base', label: 'Conversion Factor' }
  ];

  const actions = [
    {
      label: 'Edit',
      onClick: handleEditUom,
      className: 'text-blue-600 hover:text-blue-900'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Unit of Measures</h1>
          <p className="text-gray-600">Manage measurement units for your products</p>
        </div>
        <button
          onClick={handleCreateUom}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Create UOM
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
            data={uoms}
            actions={actions}
            emptyMessage={uoms.length === 0 ? "No UOMs found. Create your first unit of measure to get started." : ""}
          />
        )}
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title={editingUom ? "Edit UOM" : "Create New UOM"}
      >
        <div className="p-6">
          <p className="text-gray-600">
            {editingUom ? "Edit UOM form" : "Create UOM form"} will be implemented here.
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
              {editingUom ? "Update" : "Create"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default UOMsPage;