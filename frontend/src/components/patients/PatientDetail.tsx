import React from 'react';
import { Box, Typography } from '@mui/material';

export const PatientDetail: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4">Patient Detail</Typography>
      <Typography color="text.secondary" sx={{ mt: 2 }}>
        Patient detail page coming soon...
      </Typography>
    </Box>
  );
};

export default PatientDetail;
