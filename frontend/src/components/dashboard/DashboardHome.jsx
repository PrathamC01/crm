import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Chip,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  Business,
  People,
  AttachMoney,
  Assessment,
} from '@mui/icons-material';

const DashboardHome = () => {
  const [metrics, setMetrics] = useState({
    leads: { total: 0, new: 0, qualified: 0, conversion_rate: 0 },
    opportunities: { total: 0, open: 0, won: 0, total_value: 0, win_rate: 0 },
    contacts: { total: 0, decision_makers: 0 },
    companies: { total: 0 },
  });

  // Fetch dashboard data
  useEffect(() => {
    // For now using mock data - will integrate with API later
    setMetrics({
      leads: { total: 45, new: 12, qualified: 18, conversion_rate: 40 },
      opportunities: { total: 23, open: 15, won: 8, total_value: 1250000, win_rate: 35 },
      contacts: { total: 127, decision_makers: 38 },
      companies: { total: 89 },
    });
  }, []);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const metricCards = [
    {
      title: 'Total Companies',
      value: metrics.companies.total,
      icon: <Business />,
      color: '#2196f3',
      trend: '+12%',
    },
    {
      title: 'Active Contacts',
      value: metrics.contacts.total,
      icon: <People />,
      color: '#4caf50',
      trend: '+8%',
      subtitle: `${metrics.contacts.decision_makers} Decision Makers`,
    },
    {
      title: 'Active Leads',
      value: metrics.leads.total,
      icon: <TrendingUp />,
      color: '#ff9800',
      trend: '+15%',
      subtitle: `${metrics.leads.qualified} Qualified`,
    },
    {
      title: 'Pipeline Value',
      value: formatCurrency(metrics.opportunities.total_value),
      icon: <AttachMoney />,
      color: '#9c27b0',
      trend: '+22%',
      subtitle: `${metrics.opportunities.total} Opportunities`,
    },
  ];

  return (
    <Box>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, color: 'text.primary' }}>
          Dashboard Overview
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome back! Here's what's happening with your CRM today.
        </Typography>
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} mb={4}>
        {metricCards.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                height: '100%',
                transition: 'all 0.3s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
            >
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Avatar
                    sx={{
                      bgcolor: metric.color,
                      width: 48,
                      height: 48,
                      mr: 2,
                    }}
                  >
                    {metric.icon}
                  </Avatar>
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 600 }}>
                      {typeof metric.value === 'string' ? metric.value : metric.value.toLocaleString()}
                    </Typography>
                    <Chip 
                      label={metric.trend} 
                      size="small" 
                      sx={{ 
                        bgcolor: 'rgba(76, 175, 80, 0.1)', 
                        color: '#4caf50',
                        fontWeight: 600,
                      }} 
                    />
                  </Box>
                </Box>
                <Typography variant="body2" color="text.primary" fontWeight={500}>
                  {metric.title}
                </Typography>
                {metric.subtitle && (
                  <Typography variant="body2" color="text.secondary">
                    {metric.subtitle}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Performance Overview */}
      <Grid container spacing={3}>
        {/* Lead Conversion Funnel */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Lead Conversion Funnel
              </Typography>
              
              <Box mt={3}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">Total Leads</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {metrics.leads.total}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={100}
                  sx={{ height: 8, borderRadius: 4, mb: 2 }}
                />

                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">Qualified Leads</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {metrics.leads.qualified}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={metrics.leads.total > 0 ? (metrics.leads.qualified / metrics.leads.total) * 100 : 0}
                  sx={{ height: 8, borderRadius: 4, mb: 2 }}
                  color="success"
                />

                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">Opportunities</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {metrics.opportunities.total}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={metrics.leads.total > 0 ? (metrics.opportunities.total / metrics.leads.total) * 100 : 0}
                  sx={{ height: 8, borderRadius: 4, mb: 3 }}
                  color="secondary"
                />

                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="body2" color="text.secondary">
                    Conversion Rate:{' '}
                    <Typography component="span" color="success.main" fontWeight={600}>
                      {metrics.leads.total > 0
                        ? ((metrics.opportunities.total / metrics.leads.total) * 100).toFixed(1)
                        : 0}%
                    </Typography>
                  </Typography>
                </Paper>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Pipeline Value */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Opportunity Pipeline
              </Typography>
              
              <Box textAlign="center" mt={3} mb={4}>
                <Typography variant="h3" sx={{ fontWeight: 700, color: 'success.main' }}>
                  {formatCurrency(metrics.opportunities.total_value)}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Total Pipeline Value
                </Typography>
              </Box>

              <Grid container spacing={2} mb={3}>
                <Grid item xs={6}>
                  <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.50' }}>
                    <Typography variant="h6" color="primary.main" fontWeight={600}>
                      {metrics.opportunities.open}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Open
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6}>
                  <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.50' }}>
                    <Typography variant="h6" color="success.main" fontWeight={600}>
                      {metrics.opportunities.won}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Won
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                <Typography variant="body2" color="text.secondary">
                  Average Deal Size:{' '}
                  <Typography component="span" fontWeight={600}>
                    {metrics.opportunities.total > 0
                      ? formatCurrency(metrics.opportunities.total_value / metrics.opportunities.total)
                      : '₹0'}
                  </Typography>
                </Typography>
              </Paper>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardHome;