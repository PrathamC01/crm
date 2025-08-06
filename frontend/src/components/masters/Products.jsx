import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Products = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Products Master
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Manage products with 5-category classification and auto-generated SKU codes
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Product Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Coming soon - Full product management with inline category creation, SKU auto-generation, 
            and comprehensive product classification system.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Products;