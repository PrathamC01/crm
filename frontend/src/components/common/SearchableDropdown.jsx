import React, { useState, useRef, useEffect } from 'react';

const SearchableDropdown = ({ 
  options = [], 
  value, 
  onChange, 
  onAddNew,
  placeholder = "Select option...",
  searchPlaceholder = "Search...",
  emptyMessage = "No options found",
  addNewLabel = "Add New",
  disabled = false,
  required = false,
  className = ""
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredOptions, setFilteredOptions] = useState(options);
  const dropdownRef = useRef(null);
  const searchInputRef = useRef(null);

  // Find selected option for display
  const selectedOption = options.find(option => option.value === value);

  useEffect(() => {
    // Filter options based on search term
    const filtered = options.filter(option =>
      option.label.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredOptions(filtered);
  }, [options, searchTerm]);

  useEffect(() => {
    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleToggle = () => {
    if (disabled) return;
    setIsOpen(!isOpen);
    if (!isOpen) {
      setSearchTerm('');
      // Focus search input when opening
      setTimeout(() => {
        if (searchInputRef.current) {
          searchInputRef.current.focus();
        }
      }, 100);
    }
  };

  const handleOptionSelect = (option) => {
    onChange(option.value);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleAddNew = () => {
    setIsOpen(false);
    setSearchTerm('');
    if (onAddNew) {
      onAddNew();
    }
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredOptions.length === 1) {
        handleOptionSelect(filteredOptions[0]);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      setSearchTerm('');
    }
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Dropdown Toggle Button */}
      <button
        type="button"
        onClick={handleToggle}
        disabled={disabled}
        className={`
          relative w-full bg-white border rounded-md shadow-sm px-3 py-2 text-left cursor-pointer
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'hover:border-gray-400'}
          ${required && !value ? 'border-red-300' : 'border-gray-300'}
        `}
      >
        <span className={`block truncate ${!selectedOption ? 'text-gray-500' : 'text-gray-900'}`}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
          <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L10 5.414 7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3zm-3.707 9.293a1 1 0 011.414 0L10 14.586l2.293-2.293a1 1 0 011.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </span>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none">
          {/* Search Input */}
          <div className="sticky top-0 bg-white px-3 py-2 border-b border-gray-200">
            <input
              ref={searchInputRef}
              type="text"
              value={searchTerm}
              onChange={handleSearchChange}
              onKeyDown={handleKeyDown}
              className="w-full px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm"
              placeholder={searchPlaceholder}
            />
          </div>

          {/* Add New Button */}
          {onAddNew && (
            <div className="border-b border-gray-200">
              <button
                type="button"
                onClick={handleAddNew}
                className="w-full px-3 py-2 text-left text-sm text-blue-600 hover:bg-blue-50 focus:outline-none focus:bg-blue-50 flex items-center"
              >
                <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                {addNewLabel}
                {searchTerm && ` "${searchTerm}"`}
              </button>
            </div>
          )}

          {/* Options List */}
          <div className="py-1">
            {filteredOptions.length === 0 ? (
              <div className="px-3 py-2 text-sm text-gray-500 italic">
                {emptyMessage}
              </div>
            ) : (
              filteredOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleOptionSelect(option)}
                  className={`
                    w-full px-3 py-2 text-left text-sm hover:bg-gray-100 focus:outline-none focus:bg-gray-100
                    ${value === option.value ? 'bg-blue-100 text-blue-900' : 'text-gray-900'}
                  `}
                >
                  <div className="flex justify-between items-center">
                    <span className="truncate">{option.label}</span>
                    {option.abbreviation && (
                      <span className="ml-2 text-xs text-gray-500 bg-gray-200 px-1 rounded">
                        {option.abbreviation}
                      </span>
                    )}
                  </div>
                  {option.description && (
                    <div className="text-xs text-gray-500 mt-1">
                      {option.description}
                    </div>
                  )}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchableDropdown;