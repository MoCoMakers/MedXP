import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  TextField,
  InputAdornment,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Visibility as VisibilityIcon,
  CalendarToday as CalendarIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { format, differenceInYears, parseISO } from 'date-fns';
import { useApi, useDebounce } from '../../hooks';
import { LoadingSpinner } from '../common/LoadingSpinner';
import apiClient from '../../services/api';
import type { Patient, PaginationParams } from '../../types';

type Order = 'asc' | 'desc';

interface HeadCell {
  id: keyof Patient;
  label: string;
  numeric: boolean;
}

const headCells: HeadCell[] = [
  { id: 'mrn', label: 'MRN', numeric: false },
  { id: 'firstName', label: 'First Name', numeric: false },
  { id: 'lastName', label: 'Last Name', numeric: false },
  { id: 'dateOfBirth', label: 'Age', numeric: false },
  { id: 'gender', label: 'Gender', numeric: false },
  { id: 'conditions', label: 'Conditions', numeric: false },
];

export const PatientList: React.FC = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState<keyof Patient>('lastName');
  const [order, setOrder] = useState<Order>('asc');
  const [searchQuery, setSearchQuery] = useState('');
  const [addDialogOpen, setAddDialogOpen] = useState(false);

  const debouncedSearch = useDebounce(searchQuery, 300);

  const params: PaginationParams = {
    page: page + 1,
    limit: rowsPerPage,
  };

  if (orderBy) {
    params.orderBy = orderBy;
    params.order = order;
  }

  if (debouncedSearch) {
    params.search = debouncedSearch;
  }

  const { data, loading, refetch } = useApi(() => apiClient.getPatients(params), [
    page,
    rowsPerPage,
    orderBy,
    order,
    debouncedSearch,
  ]);

  const handleRequestSort = (property: keyof Patient) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const calculateAge = (dob: string) => {
    try {
      return differenceInYears(new Date(), parseISO(dob));
    } catch {
      return 'N/A';
    }
  };

  const handleAddPatient = async () => {
    // API call to add patient would go here
    setAddDialogOpen(false);
    refetch();
  };

  if (loading) {
    return <LoadingSpinner message="Loading patients..." />;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Patients
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setAddDialogOpen(true)}
        >
          Add Patient
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search patients by name or MRN..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              {headCells.map((headCell) => (
                <TableCell
                  key={headCell.id}
                  sortDirection={orderBy === headCell.id ? order : false}
                >
                  <TableSortLabel
                    active={orderBy === headCell.id}
                    direction={orderBy === headCell.id ? order : 'asc'}
                    onClick={() => handleRequestSort(headCell.id)}
                  >
                    {headCell.label}
                  </TableSortLabel>
                </TableCell>
              ))}
              <TableCell align="right" sx={{ width: 80 }}></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.data.map((patient) => (
              <TableRow
                key={patient.id}
                hover
                sx={{ cursor: 'pointer' }}
                onClick={() => navigate(`/patients/${patient.id}`)}
              >
                <TableCell>{patient.mrn}</TableCell>
                <TableCell>{patient.firstName}</TableCell>
                <TableCell>{patient.lastName}</TableCell>
                <TableCell>{calculateAge(patient.dateOfBirth)} years</TableCell>
                <TableCell>{patient.gender}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {patient.conditions.slice(0, 2).map((condition, idx) => (
                      <Chip
                        key={idx}
                        label={condition}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                    {patient.conditions.length > 2 && (
                      <Chip
                        label={`+${patient.conditions.length - 2}`}
                        size="small"
                      />
                    )}
                  </Box>
                </TableCell>
                <TableCell align="right">
                  <Tooltip title="View Details">
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/patients/${patient.id}`);
                      }}
                    >
                      <VisibilityIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
            {data?.data.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">No patients found</Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={data?.total || 0}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
      </TableContainer>

      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Patient</DialogTitle>
        <DialogContent>
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            Patient registration form coming soon...
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleAddPatient}>
            Add Patient
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PatientList;
