import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const ProductDashboard = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Product Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Product performance and inventory analytics
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Product Analytics
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Coming soon - Product-wise revenue and performance metrics
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ProductDashboard;