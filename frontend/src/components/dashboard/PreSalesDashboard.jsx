import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const PreSalesDashboard = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Pre-Sales Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Lead generation and qualification metrics
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Pre-Sales Analytics
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Coming soon - Lead generation and qualification metrics
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default PreSalesDashboard;