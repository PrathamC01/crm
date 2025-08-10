import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import MainLayout from './layouts/MainLayout';
import LoginPage from './pages/Auth/LoginPage';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Dashboard Pages
import DashboardOverview from './pages/Dashboard/DashboardOverview';
import SalesDashboard from './pages/Dashboard/SalesDashboard';
import PresalesDashboard from './pages/Dashboard/PresalesDashboard';
import ProductDashboard from './pages/Dashboard/ProductDashboard';

// Masters Pages
import ProductsPage from './pages/Masters/ProductsPage';
import UOMsPage from './pages/Masters/UOMsPage';
import PriceListsPage from './pages/Masters/PriceListsPage';
import UsersPage from './pages/Masters/UsersPage';
import DepartmentsPage from './pages/Masters/DepartmentsPage';
import RolesPage from './pages/Masters/RolesPage';

// Leads Pages
import LeadsPage from './pages/Leads/LeadsPage';
import MyLeadsPage from './pages/Leads/MyLeadsPage';
import LeadReportsPage from './pages/Leads/LeadReportsPage';

// Opportunities Pages  
import OpportunitiesPage from './pages/Opportunities/OpportunitiesPage';
import MyOpportunitiesPage from './pages/Opportunities/MyOpportunitiesPage';
import QuotationsPage from './pages/Quotations/QuotationsPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Protected Routes */}
            <Route path="/" element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }>
              {/* Dashboard Routes */}
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardOverview />} />
              <Route path="dashboard/sales" element={<SalesDashboard />} />
              <Route path="dashboard/presales" element={<PresalesDashboard />} />
              <Route path="dashboard/product" element={<ProductDashboard />} />
              
              {/* Masters Routes */}
              <Route path="masters">
                <Route index element={<Navigate to="/masters/products" replace />} />
                <Route path="products" element={<ProductsPage />} />
                <Route path="uoms" element={<UOMsPage />} />
                <Route path="pricelists" element={<PriceListsPage />} />
                <Route path="users" element={<UsersPage />} />
                <Route path="departments" element={<DepartmentsPage />} />
                <Route path="roles" element={<RolesPage />} />
              </Route>
              
              {/* Leads Routes */}
              <Route path="leads">
                <Route index element={<LeadsPage />} />
                <Route path="my" element={<MyLeadsPage />} />
                <Route path="reports" element={<LeadReportsPage />} />
              </Route>
              
              {/* Opportunities Routes */}
              <Route path="opportunities">
                <Route index element={<OpportunitiesPage />} />
                <Route path="my" element={<MyOpportunitiesPage />} />
              </Route>
              
              {/* Quotations */}
              <Route path="quotations" element={<QuotationsPage />} />
            </Route>
            
            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;