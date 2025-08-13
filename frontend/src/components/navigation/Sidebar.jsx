import React from 'react';
import { Link } from 'react-router-dom';
import { 
  HomeIcon, 
  UserGroupIcon, 
  BriefcaseIcon, 
  CogIcon,
  ChartBarIcon,
  DocumentTextIcon,
  BuildingOfficeIcon,
  UserIcon
} from '@heroicons/react/24/outline';

const Sidebar = ({ isOpen, onToggle, currentPath }) => {
  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: HomeIcon,
      children: [
        { name: 'Overview', href: '/dashboard' },
        { name: 'Sales Dashboard', href: '/dashboard/sales' },
        { name: 'Presales Dashboard', href: '/dashboard/presales' },
        { name: 'Product Dashboard', href: '/dashboard/product' }
      ]
    },
    {
      name: 'Companies',
      href: '/companies',
      icon: BuildingOfficeIcon,
      children: []
    },
    {
      name: 'Leads',
      href: '/leads',
      icon: UserGroupIcon,
      children: [
        { name: 'All Leads', href: '/leads' },
        { name: 'My Leads', href: '/leads/my' },
        { name: 'Lead Reports', href: '/leads/reports' }
      ]
    },
    {
      name: 'Opportunities',
      href: '/opportunities',
      icon: BriefcaseIcon,
      children: [
        { name: 'All Opportunities', href: '/opportunities' },
        { name: 'My Opportunities', href: '/opportunities/my' },
        { name: 'Quotations', href: '/quotations' }
      ]
    },
    {
      name: 'Masters',
      href: '/masters',
      icon: CogIcon,
      children: [
        { name: 'Products', href: '/masters/products' },
        { name: 'Price Lists', href: '/masters/pricelists' },
        { name: 'UOMs', href: '/masters/uoms' },
        { name: 'Users', href: '/masters/users' },
        { name: 'Departments', href: '/masters/departments' },
        { name: 'Roles', href: '/masters/roles' }
      ]
    }
  ];

  const isActive = (path) => {
    return currentPath.startsWith(path);
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-20 lg:hidden"
          onClick={onToggle}
        />
      )}
      
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-30 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-48'
      } lg:translate-x-0`}>
        
        {/* Logo */}
        <div className="flex items-center justify-center h-16 px-4 bg-blue-600">
          <h1 className="text-xl font-bold text-white">Enterprise CRM</h1>
        </div>

        {/* Navigation */}
        <nav className="mt-8 px-4">
          <ul className="space-y-2">
            {navigation.map((item) => (
              <li key={item.name}>
                <Link
                  to={item.href}
                  className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive(item.href)
                      ? 'bg-blue-100 text-blue-700 border-r-4 border-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {isOpen && (
                    <>
                      {item.name}
                      {isActive(item.href) && (
                        <ChartBarIcon className="ml-auto h-4 w-4" />
                      )}
                    </>
                  )}
                </Link>
                
                {/* Sub-navigation */}
                {isOpen && isActive(item.href) && item.children && (
                  <ul className="mt-2 ml-8 space-y-1">
                    {item.children.map((child) => (
                      <li key={child.name}>
                        <Link
                          to={child.href}
                          className={`block px-3 py-2 text-sm rounded-md transition-colors ${
                            currentPath === child.href
                              ? 'bg-blue-50 text-blue-600 font-medium'
                              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                          }`}
                        >
                          {child.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 w-full p-4 border-t">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <UserIcon className="h-8 w-8 text-gray-400" />
            </div>
            {isOpen && (
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">User Panel</p>
                <p className="text-xs text-gray-500">Enterprise CRM v1.0</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;