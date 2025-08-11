import React, { useState } from 'react';
import { ContactList, ContactForm, ContactView } from './modules/contact';

const ContactManagement = () => {
  const [currentView, setCurrentView] = useState('list');
  const [selectedContact, setSelectedContact] = useState(null);

  const handleCreate = () => {
    setSelectedContact(null);
    setCurrentView('form');
  };

  const handleEdit = (contact) => {
    setSelectedContact(contact);
    setCurrentView('form');
  };

  const handleView = (contact) => {
    setSelectedContact(contact);
    setCurrentView('view');
  };

  const handleSave = (savedContact) => {
    setCurrentView('list');
    setSelectedContact(null);
  };

  const handleCancel = () => {
    setCurrentView('list');
    setSelectedContact(null);
  };

  const handleDelete = (contactId) => {
    // Delete is handled within ContactList component
    // This could be used for additional logic if needed
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 text-left">Contact Management</h2>
          <p className="text-gray-600">Manage business contacts with role-based classification</p>
        </div>
        {currentView === 'list' && (
          <button
            onClick={handleCreate}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            <span className="mr-2">+</span>
            Add Contact
          </button>
        )}
      </div>

      {/* Content */}
      {currentView === 'list' && (
        <ContactList
          onEdit={handleEdit}
          onView={handleView}
          onDelete={handleDelete}
        />
      )}

      {currentView === 'form' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium mb-6">
            {selectedContact ? 'Edit Contact' : 'Create New Contact'}
          </h3>
          <ContactForm
            contact={selectedContact}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        </div>
      )}

      {currentView === 'view' && (
        <div className="bg-white rounded-lg shadow p-6">
          <ContactView
            contact={selectedContact}
            onEdit={handleEdit}
            onClose={handleCancel}
          />
        </div>
      )}

      {/* Business Rules Info */}
      {currentView === 'list' && (
        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Contact Role Types</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-blue-800">
            <div>
              <span className="font-semibold">Admin:</span> Administrative contacts
            </div>
            <div>
              <span className="font-semibold">Influencer:</span> Can influence decisions
            </div>
            <div>
              <span className="font-semibold">Decision Maker:</span> Can create opportunities
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContactManagement;