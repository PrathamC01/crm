import React, { useState, useEffect } from 'react';
import { apiMethods } from '../../utils/api';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const PriceListsPage = () => {
  const [priceLists, setPriceLists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingPriceList, setEditingPriceList] = useState(null);

  useEffect(() => {
    fetchPriceLists();
  }, []);

  const fetchPriceLists = async () => {
    try {
      setLoading(true);
      const response = await apiMethods.masters.getPriceLists();
      if (response.data?.data?.price_lists) {
        setPriceLists(response.data.data.price_lists);
      } else {
        setPriceLists([]);
      }
    } catch (error) {
      console.error('Error fetching price lists:', error);
      setPriceLists([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePriceList = () => {
    setEditingPriceList(null);
    setShowCreateModal(true);
  };

  const handleEditPriceList = (priceList) => {
    setEditingPriceList(priceList);
    setShowCreateModal(true);
  };

  const columns = [
    { key: 'price_list_name', label: 'Price List Name' },
    { key: 'valid_upto', label: 'Valid Until' },
    { key: 'is_approved', label: 'Status', render: (item) => item.is_approved ? 'Approved' : 'Pending' }
  ];

  const actions = [
    {
      label: 'Edit',
      onClick: handleEditPriceList,
      className: 'text-blue-600 hover:text-blue-900'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Price Lists</h1>
          <p className="text-gray-600">Manage pricing configurations for your products</p>
        </div>
        <button
          onClick={handleCreatePriceList}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Create Price List
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
            data={priceLists}
            actions={actions}
            emptyMessage={priceLists.length === 0 ? "No price lists found. Create your first price list to manage product pricing." : ""}
          />
        )}
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title={editingPriceList ? "Edit Price List" : "Create New Price List"}
      >
        <div className="p-6">
          <p className="text-gray-600">
            {editingPriceList ? "Edit price list form" : "Create price list form"} will be implemented here.
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
              {editingPriceList ? "Update" : "Create"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default PriceListsPage;