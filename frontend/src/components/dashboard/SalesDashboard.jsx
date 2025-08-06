import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const SalesDashboard = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Sales Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Sales performance metrics and analytics
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Sales Analytics
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Coming soon - Advanced sales analytics and reporting
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SalesDashboard;