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
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  Delete as DeleteIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useApi, useDebounce } from '../../hooks';
import { LoadingSpinner } from '../common/LoadingSpinner';
import apiClient from '../../services/api';
import type { Nurse, PaginationParams } from '../../types';

type Order = 'asc' | 'desc';

interface HeadCell {
  id: keyof Nurse;
  label: string;
  numeric: boolean;
}

const headCells: HeadCell[] = [
  { id: 'name', label: 'Name', numeric: false },
  { id: 'email', label: 'Email', numeric: false },
  { id: 'department', label: 'Department', numeric: false },
  { id: 'shiftPattern', label: 'Shift', numeric: false },
  { id: 'status', label: 'Status', numeric: false },
  { id: 'hireDate', label: 'Hire Date', numeric: false },
];

export const NurseList: React.FC = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState<keyof Nurse>('name');
  const [order, setOrder] = useState<Order>('asc');
  const [searchQuery, setSearchQuery] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedNurse, setSelectedNurse] = useState<Nurse | null>(null);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [newNurse, setNewNurse] = useState({
    name: '',
    email: '',
    department: '',
    shiftPattern: '',
    employeeId: '',
  });

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

  if (departmentFilter) {
    params.department = departmentFilter;
  }

  if (statusFilter) {
    params.status = statusFilter;
  }

  const { data, loading, refetch } = useApi(() => apiClient.getNurses(params), [
    page,
    rowsPerPage,
    orderBy,
    order,
    debouncedSearch,
    departmentFilter,
    statusFilter,
  ]);

  const handleRequestSort = (property: keyof Nurse) => {
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

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, nurse: Nurse) => {
    setAnchorEl(event.currentTarget);
    setSelectedNurse(nurse);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedNurse(null);
  };

  const handleViewNurse = () => {
    if (selectedNurse) {
      navigate(`/nurses/${selectedNurse.id}`);
    }
    handleMenuClose();
  };

  const handleAddNurse = async () => {
    // API call to add nurse would go here
    setAddDialogOpen(false);
    setNewNurse({ name: '', email: '', department: '', shiftPattern: '', employeeId: '' });
    refetch();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'inactive':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading nurses..." />;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Nurses
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setAddDialogOpen(true)}
        >
          Add Nurse
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search nurses..."
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
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Department</InputLabel>
              <Select
                value={departmentFilter}
                label="Department"
                onChange={(e) => setDepartmentFilter(e.target.value)}
              >
                <MenuItem value="">All Departments</MenuItem>
                <MenuItem value="emergency">Emergency</MenuItem>
                <MenuItem value="icu">ICU</MenuItem>
                <MenuItem value="general">General</MenuItem>
                <MenuItem value="pediatrics">Pediatrics</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                label="Status"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ width: 50 }}></TableCell>
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
              <TableCell align="right" sx={{ width: 50 }}></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.data.map((nurse) => (
              <TableRow
                key={nurse.id}
                hover
                sx={{ cursor: 'pointer' }}
                onClick={() => navigate(`/nurses/${nurse.id}`)}
              >
                <TableCell>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    {nurse.name.charAt(0)}
                  </Avatar>
                </TableCell>
                <TableCell>{nurse.name}</TableCell>
                <TableCell>{nurse.email}</TableCell>
                <TableCell>{nurse.department}</TableCell>
                <TableCell>{nurse.shiftPattern}</TableCell>
                <TableCell>
                  <Chip
                    label={nurse.status}
                    size="small"
                    color={getStatusColor(nurse.status)}
                  />
                </TableCell>
                <TableCell>
                  {new Date(nurse.hireDate).toLocaleDateString()}
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleMenuOpen(e, nurse);
                    }}
                  >
                    <MoreVertIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
            {data?.data.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">No nurses found</Typography>
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

      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={handleViewNurse}>
          <ListItemIcon>
            <VisibilityIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleMenuClose} sx={{ color: 'error.main' }}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Deactivate</ListItemText>
        </MenuItem>
      </Menu>

      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Nurse</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Full Name"
                value={newNurse.name}
                onChange={(e) => setNewNurse({ ...newNurse, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={newNurse.email}
                onChange={(e) => setNewNurse({ ...newNurse, email: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Department</InputLabel>
                <Select
                  value={newNurse.department}
                  label="Department"
                  onChange={(e) => setNewNurse({ ...newNurse, department: e.target.value })}
                >
                  <MenuItem value="emergency">Emergency</MenuItem>
                  <MenuItem value="icu">ICU</MenuItem>
                  <MenuItem value="general">General</MenuItem>
                  <MenuItem value="pediatrics">Pediatrics</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Shift Pattern</InputLabel>
                <Select
                  value={newNurse.shiftPattern}
                  label="Shift Pattern"
                  onChange={(e) => setNewNurse({ ...newNurse, shiftPattern: e.target.value })}
                >
                  <MenuItem value="day">Day Shift</MenuItem>
                  <MenuItem value="night">Night Shift</MenuItem>
                  <MenuItem value="rotating">Rotating</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Employee ID"
                value={newNurse.employeeId}
                onChange={(e) => setNewNurse({ ...newNurse, employeeId: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleAddNurse}>
            Add Nurse
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default NurseList;
