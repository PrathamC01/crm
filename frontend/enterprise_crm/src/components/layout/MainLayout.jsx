import React, { useState, useEffect } from 'react';
import { 
  HomeIcon, 
  UserGroupIcon, 
  BriefcaseIcon, 
  CogIcon,
  ChartBarIcon,
  DocumentTextIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';

const MainLayout = ({ children, activeTab, onTabChange, user }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigationTabs = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: HomeIcon,
      href: '/dashboard'
    },
    {
      id: 'leads',
      name: 'Leads',
      icon: UserGroupIcon,
      href: '/leads',
      subMenus: [
        { id: 'contacts', name: 'Contact Management', href: '/leads/contacts' },
        { id: 'companies', name: 'Company Management', href: '/leads/companies' },
        { id: 'leads', name: 'Lead Management', href: '/leads' }
      ]
    },
    {
      id: 'opportunities',
      name: 'Opportunities',
      icon: BriefcaseIcon,
      href: '/opportunities',
      subMenus: [
        { id: 'opportunities', name: 'Opportunity Management', href: '/opportunities' },
        { id: 'quotations', name: 'Quotation Management', href: '/opportunities/quotations' }
      ]
    },
    {
      id: 'masters',
      name: 'Masters',
      icon: CogIcon,
      href: '/masters',
      subMenus: [
        { id: 'products', name: 'Product Master', href: '/masters/products' },
        { id: 'pricing', name: 'Price Lists', href: '/masters/pricing' },
        { id: 'users', name: 'User Management', href: '/masters/users' },
        { id: 'lookups', name: 'Lookup Data', href: '/masters/lookups' }
      ]
    }
  ];

  const departmentDashboards = {
    sales: { name: 'Sales Dashboard', icon: ChartBarIcon },
    presales: { name: 'Presales Dashboard', icon: DocumentTextIcon },
    product: { name: 'Product Dashboard', icon: BuildingOfficeIcon }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Left side - Logo and Navigation */}
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-gray-900">
                  Enterprise CRM
                </h1>
              </div>
              
              {/* Main Navigation Tabs */}
              <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
                {navigationTabs.map((tab) => (
                  <div key={tab.id} className="relative group">
                    <button
                      onClick={() => onTabChange(tab.id)}
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                        activeTab === tab.id
                          ? 'border-blue-500 text-gray-900'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <tab.icon className="h-5 w-5 mr-2" />
                      {tab.name}
                    </button>
                    
                    {/* Dropdown Menu for tabs with subMenus */}
                    {tab.subMenus && (
                      <div className="absolute left-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                        <div className="py-1">
                          {tab.subMenus.map((subMenu) => (
                            <a
                              key={subMenu.id}
                              href={subMenu.href}
                              className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                            >
                              {subMenu.name}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Right side - Department Dashboards and User Menu */}
            <div className="flex items-center space-x-4">
              {/* Department Dashboard Selector */}
              {activeTab === 'dashboard' && (
                <div className="relative">
                  <select
                    className="bg-white border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onChange={(e) => onTabChange('dashboard', e.target.value)}
                  >
                    <option value="default">General Dashboard</option>
                    {Object.entries(departmentDashboards).map(([key, dept]) => (
                      <option key={key} value={key}>
                        {dept.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* User Profile */}
              <div className="relative group">
                <button className="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
                    <span className="text-white font-medium">
                      {user?.name?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <span className="ml-2 text-gray-700">{user?.name || 'User'}</span>
                </button>
                
                <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <div className="py-1">
                    <a href="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      Profile Settings
                    </a>
                    <a href="/logout" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      Sign Out
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>

      {/* Mobile Navigation (Hidden by default, can be toggled) */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-black bg-opacity-25" onClick={() => setSidebarOpen(false)} />
          <div className="fixed top-0 left-0 w-64 h-full bg-white shadow-lg">
            {/* Mobile navigation content */}
            <div className="p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Navigation</h2>
              {navigationTabs.map((tab) => (
                <div key={tab.id} className="mb-2">
                  <button
                    onClick={() => {
                      onTabChange(tab.id);
                      setSidebarOpen(false);
                    }}
                    className="w-full flex items-center px-2 py-2 text-left text-gray-700 hover:bg-gray-100 rounded-md"
                  >
                    <tab.icon className="h-5 w-5 mr-3" />
                    {tab.name}
                  </button>
                  {tab.subMenus && (
                    <div className="ml-8 mt-1 space-y-1">
                      {tab.subMenus.map((subMenu) => (
                        <a
                          key={subMenu.id}
                          href={subMenu.href}
                          className="block px-2 py-1 text-sm text-gray-600 hover:text-gray-900"
                        >
                          {subMenu.name}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainLayout;