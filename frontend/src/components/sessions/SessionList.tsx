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
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Tooltip,
  LinearProgress,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Visibility as VisibilityIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { format, parseISO } from 'date-fns';
import { useApi } from '../../hooks';
import { LoadingSpinner } from '../common/LoadingSpinner';
import apiClient from '../../services/api';
import type { Session, PaginationParams } from '../../types';

const getStatusColor = (status: string) => {
  switch (status) {
    case 'recording':
      return 'error';
    case 'transcribing':
      return 'warning';
    case 'analyzing':
      return 'info';
    case 'completed':
      return 'success';
    case 'failed':
      return 'error';
    default:
      return 'default';
  }
};

const getSessionTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    initial_assessment: 'Initial Assessment',
    routine_followup: 'Routine Follow-up',
    emergency: 'Emergency',
    discharge: 'Discharge',
    care_planning: 'Care Planning',
    medication_review: 'Medication Review',
  };
  return labels[type] || type;
};

export const SessionList: React.FC = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [startSessionOpen, setStartSessionOpen] = useState(false);
  const [newSession, setNewSession] = useState({
    nurseId: '',
    patientId: '',
    sessionType: '',
    department: '',
  });

  const params: PaginationParams = {
    page: page + 1,
    limit: rowsPerPage,
  };

  if (statusFilter) {
    params.status = statusFilter;
  }

  if (typeFilter) {
    params.sessionType = typeFilter;
  }

  const { data, loading, refetch } = useApi(() => apiClient.getSessions(params), [
    page,
    rowsPerPage,
    statusFilter,
    typeFilter,
  ]);

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleStartSession = async () => {
    // API call to start session would go here
    setStartSessionOpen(false);
    setNewSession({ nurseId: '', patientId: '', sessionType: '', department: '' });
    refetch();
  };

  const handleStopSession = async (sessionId: string) => {
    await apiClient.stopSession(sessionId);
    refetch();
  };

  if (loading) {
    return <LoadingSpinner message="Loading sessions..." />;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Sessions
        </Typography>
        <Button
          variant="contained"
          startIcon={<PlayIcon />}
          onClick={() => setStartSessionOpen(true)}
        >
          Start Session
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                label="Status"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="recording">Recording</MenuItem>
                <MenuItem value="transcribing">Transcribing</MenuItem>
                <MenuItem value="analyzing">Analyzing</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Session Type</InputLabel>
              <Select
                value={typeFilter}
                label="Session Type"
                onChange={(e) => setTypeFilter(e.target.value)}
              >
                <MenuItem value="">All Types</MenuItem>
                <MenuItem value="initial_assessment">Initial Assessment</MenuItem>
                <MenuItem value="routine_followup">Routine Follow-up</MenuItem>
                <MenuItem value="emergency">Emergency</MenuItem>
                <MenuItem value="discharge">Discharge</MenuItem>
                <MenuItem value="care_planning">Care Planning</MenuItem>
                <MenuItem value="medication_review">Medication Review</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={() => refetch()}
              fullWidth
            >
              Refresh
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Start Time</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.data.map((session) => (
              <TableRow
                key={session.id}
                hover
                sx={{ cursor: 'pointer' }}
                onClick={() => navigate(`/sessions/${session.id}`)}
              >
                <TableCell>
                  {format(parseISO(session.startTime), 'MMM d, yyyy h:mm a')}
                </TableCell>
                <TableCell>
                  {session.duration
                    ? `${Math.floor(session.duration / 60)}m ${session.duration % 60}s`
                    : 'In progress'}
                </TableCell>
                <TableCell>{getSessionTypeLabel(session.sessionType)}</TableCell>
                <TableCell>{session.department}</TableCell>
                <TableCell>
                  <Chip
                    label={session.status}
                    size="small"
                    color={getStatusColor(session.status)}
                  />
                </TableCell>
                <TableCell align="right">
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 0.5 }}>
                    {session.status === 'recording' && (
                      <Tooltip title="Stop Recording">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStopSession(session.id);
                          }}
                        >
                          <StopIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="View Details">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/sessions/${session.id}`);
                        }}
                      >
                        <VisibilityIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
            {data?.data.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">No sessions found</Typography>
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

      <Dialog open={startSessionOpen} onClose={() => setStartSessionOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Start New Session</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nurse ID"
                value={newSession.nurseId}
                onChange={(e) => setNewSession({ ...newSession, nurseId: e.target.value })}
                helperText="Select a nurse for this session"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Patient ID"
                value={newSession.patientId}
                onChange={(e) => setNewSession({ ...newSession, patientId: e.target.value })}
                helperText="Select a patient for this session"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Session Type</InputLabel>
                <Select
                  value={newSession.sessionType}
                  label="Session Type"
                  onChange={(e) => setNewSession({ ...newSession, sessionType: e.target.value })}
                >
                  <MenuItem value="initial_assessment">Initial Assessment</MenuItem>
                  <MenuItem value="routine_followup">Routine Follow-up</MenuItem>
                  <MenuItem value="emergency">Emergency</MenuItem>
                  <MenuItem value="discharge">Discharge</MenuItem>
                  <MenuItem value="care_planning">Care Planning</MenuItem>
                  <MenuItem value="medication_review">Medication Review</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Department</InputLabel>
                <Select
                  value={newSession.department}
                  label="Department"
                  onChange={(e) => setNewSession({ ...newSession, department: e.target.value })}
                >
                  <MenuItem value="emergency">Emergency</MenuItem>
                  <MenuItem value="icu">ICU</MenuItem>
                  <MenuItem value="general">General</MenuItem>
                  <MenuItem value="pediatrics">Pediatrics</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStartSessionOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            startIcon={<PlayIcon />}
            onClick={handleStartSession}
            disabled={!newSession.nurseId || !newSession.patientId}
          >
            Start Recording
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SessionList;
