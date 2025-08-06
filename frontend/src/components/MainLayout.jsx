import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Paper,
  Tabs,
  Tab,
  Menu,
  MenuItem,
  IconButton,
  Avatar,
  Divider,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Business as BusinessIcon,
  Groups as GroupsIcon,
  TrendingUp as TrendingUpIcon,
  Settings as SettingsIcon,
  ExitToApp as LogoutIcon,
  ExpandMore as ExpandMoreIcon,
  Inventory as InventoryIcon,
  Category as CategoryIcon,
  PriceCheck as PriceCheckIcon,
} from '@mui/icons-material';

// Import components (we'll create these)
import DashboardHome from './dashboard/DashboardHome';
import SalesDashboard from './dashboard/SalesDashboard';
import PreSalesDashboard from './dashboard/PreSalesDashboard';
import ProductDashboard from './dashboard/ProductDashboard';
import ProductTypes from './masters/ProductTypes';
import Categories from './masters/Categories';
import Products from './masters/Products';
import LeadManagement from './LeadManagement';
import CompanyManagement from './CompanyManagement';
import ContactManagement from './ContactManagement';
import OpportunityManagement from './OpportunityManagement';
import UserManagement from './UserManagement';

const MainLayout = ({ onLogout }) => {
  const [selectedMainTab, setSelectedMainTab] = useState(0);
  const [dashboardSubTab, setDashboardSubTab] = useState(0);
  const [mastersSubTab, setMastersSubTab] = useState(0);
  const [leadsSubTab, setLeadsSubTab] = useState(0);
  const [opportunitiesSubTab, setOpportunitiesSubTab] = useState(0);
  
  const navigate = useNavigate();
  const location = useLocation();

  // Tab groups configuration
  const tabGroups = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <DashboardIcon />,
      color: '#2196f3',
      subTabs: [
        { id: 'default', label: 'Overview', path: '/dashboard', component: DashboardHome },
        { id: 'sales', label: 'Sales', path: '/dashboard/sales', component: SalesDashboard },
        { id: 'presales', label: 'Pre-Sales', path: '/dashboard/presales', component: PreSalesDashboard },
        { id: 'products', label: 'Products', path: '/dashboard/products', component: ProductDashboard },
      ]
    },
    {
      id: 'masters',
      label: 'Masters',
      icon: <SettingsIcon />,
      color: '#ff9800',
      subTabs: [
        { id: 'product-types', label: 'Product Types', path: '/masters/product-types', component: ProductTypes },
        { id: 'categories', label: 'Categories', path: '/masters/categories', component: Categories },
        { id: 'products', label: 'Products', path: '/masters/products', component: Products },
      ]
    },
    {
      id: 'leads',
      label: 'Leads',
      icon: <TrendingUpIcon />,
      color: '#4caf50',
      subTabs: [
        { id: 'leads', label: 'Leads', path: '/leads', component: LeadManagement },
        { id: 'companies', label: 'Companies', path: '/leads/companies', component: CompanyManagement },
        { id: 'contacts', label: 'Contacts', path: '/leads/contacts', component: ContactManagement },
      ]
    },
    {
      id: 'opportunities',
      label: 'Opportunities',
      icon: <BusinessIcon />,
      color: '#9c27b0',
      subTabs: [
        { id: 'opportunities', label: 'Opportunities', path: '/opportunities', component: OpportunityManagement },
        { id: 'users', label: 'Users', path: '/opportunities/users', component: UserManagement },
      ]
    },
  ];

  // Handle navigation based on current path
  useEffect(() => {
    const currentPath = location.pathname;
    
    tabGroups.forEach((group, groupIndex) => {
      group.subTabs.forEach((subTab, subTabIndex) => {
        if (currentPath === subTab.path || (currentPath === '/' && subTab.path === '/dashboard')) {
          setSelectedMainTab(groupIndex);
          
          // Set appropriate sub tab
          switch (group.id) {
            case 'dashboard':
              setDashboardSubTab(subTabIndex);
              break;
            case 'masters':
              setMastersSubTab(subTabIndex);
              break;
            case 'leads':
              setLeadsSubTab(subTabIndex);
              break;
            case 'opportunities':
              setOpportunitiesSubTab(subTabIndex);
              break;
          }
        }
      });
    });
  }, [location.pathname]);

  const handleMainTabChange = (event, newValue) => {
    setSelectedMainTab(newValue);
    // Navigate to first sub-tab of selected main tab
    const selectedGroup = tabGroups[newValue];
    if (selectedGroup.subTabs.length > 0) {
      navigate(selectedGroup.subTabs[0].path);
    }
  };

  const handleSubTabChange = (groupId, subTabIndex) => {
    const group = tabGroups.find(g => g.id === groupId);
    if (group && group.subTabs[subTabIndex]) {
      navigate(group.subTabs[subTabIndex].path);
      
      // Update the appropriate sub tab state
      switch (groupId) {
        case 'dashboard':
          setDashboardSubTab(subTabIndex);
          break;
        case 'masters':
          setMastersSubTab(subTabIndex);
          break;
        case 'leads':
          setLeadsSubTab(subTabIndex);
          break;
        case 'opportunities':
          setOpportunitiesSubTab(subTabIndex);
          break;
      }
    }
  };

  const getCurrentSubTabIndex = (groupId) => {
    switch (groupId) {
      case 'dashboard':
        return dashboardSubTab;
      case 'masters':
        return mastersSubTab;
      case 'leads':
        return leadsSubTab;
      case 'opportunities':
        return opportunitiesSubTab;
      default:
        return 0;
    }
  };

  const selectedGroup = tabGroups[selectedMainTab];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="sticky" sx={{ zIndex: 1200 }}>
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <BusinessIcon sx={{ mr: 2, fontSize: 28 }} />
            <Typography variant="h5" component="h1" sx={{ fontWeight: 700 }}>
              ERP CRM
            </Typography>
            <Chip 
              label="v2.0" 
              size="small" 
              sx={{ ml: 2, bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }} 
            />
          </Box>
          
          <Button
            color="inherit"
            onClick={onLogout}
            startIcon={<LogoutIcon />}
            sx={{ ml: 2 }}
          >
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      {/* Main Navigation Tabs */}
      <Paper elevation={1} sx={{ borderRadius: 0 }}>
        <Container maxWidth="xl">
          <Tabs
            value={selectedMainTab}
            onChange={handleMainTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                minHeight: 64,
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 600,
              },
            }}
          >
            {tabGroups.map((group, index) => (
              <Tab
                key={group.id}
                icon={group.icon}
                label={group.label}
                iconPosition="start"
                sx={{
                  color: selectedMainTab === index ? group.color : 'text.secondary',
                }}
              />
            ))}
          </Tabs>
        </Container>
      </Paper>

      {/* Sub Navigation */}
      {selectedGroup && selectedGroup.subTabs.length > 1 && (
        <Paper elevation={1} sx={{ borderRadius: 0, bgcolor: 'grey.50' }}>
          <Container maxWidth="xl">
            <Tabs
              value={getCurrentSubTabIndex(selectedGroup.id)}
              onChange={(e, newValue) => handleSubTabChange(selectedGroup.id, newValue)}
              variant="scrollable"
              scrollButtons="auto"
              sx={{
                minHeight: 48,
                '& .MuiTab-root': {
                  minHeight: 48,
                  textTransform: 'none',
                  fontSize: '0.9rem',
                },
              }}
            >
              {selectedGroup.subTabs.map((subTab, index) => (
                <Tab
                  key={subTab.id}
                  label={subTab.label}
                  sx={{
                    color: getCurrentSubTabIndex(selectedGroup.id) === index 
                      ? selectedGroup.color 
                      : 'text.secondary',
                  }}
                />
              ))}
            </Tabs>
          </Container>
        </Paper>
      )}

      {/* Main Content Area */}
      <Box sx={{ flexGrow: 1, bgcolor: 'background.default' }}>
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Routes>
            {tabGroups.map(group =>
              group.subTabs.map(subTab => (
                <Route
                  key={subTab.path}
                  path={subTab.path}
                  element={<subTab.component />}
                />
              ))
            )}
            {/* Default route */}
            <Route path="/" element={<DashboardHome />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
};

export default MainLayout;