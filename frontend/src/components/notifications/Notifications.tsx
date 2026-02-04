import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Button,
  Tabs,
  Tab,
  Badge,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Error as ErrorIcon,
  CheckCircle as CheckIcon,
  Delete as DeleteIcon,
  DoneAll as DoneAllIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { format, parseISO, isToday, isYesterday } from 'date-fns';
import { useApi, useDebounce } from '../../hooks';
import { LoadingSpinner } from '../common/LoadingSpinner';
import apiClient from '../../services/api';
import { useAppStore } from '../../store';
import type { Notification, NotificationSeverity, NotificationType, PaginationParams } from '../../types';

const getSeverityColor = (severity: NotificationSeverity) => {
  switch (severity) {
    case 'critical':
      return 'error';
    case 'high':
      return 'warning';
    case 'medium':
      return 'info';
    case 'low':
      return 'success';
    default:
      return 'default';
  }
};

const getSeverityIcon = (severity: NotificationSeverity) => {
  switch (severity) {
    case 'critical':
      return <ErrorIcon color="error" />;
    case 'high':
      return <WarningIcon color="warning" />;
    case 'medium':
      return <InfoIcon color="info" />;
    case 'low':
      return <CheckIcon color="success" />;
    default:
      return <NotificationsIcon />;
  }
};

const getTypeLabel = (type: NotificationType) => {
  const labels: Record<NotificationType, string> = {
    alert: 'Alert',
    warning: 'Warning',
    info: 'Info',
    action_required: 'Action Required',
    risk_assessment: 'Risk Assessment',
  };
  return labels[type] || type;
};

const formatDate = (dateString: string) => {
  const date = parseISO(dateString);
  if (isToday(date)) {
    return `Today at ${format(date, 'h:mm a')}`;
  }
  if (isYesterday(date)) {
    return `Yesterday at ${format(date, 'h:mm a')}`;
  }
  return format(date, 'MMM d, yyyy h:mm a');
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index} style={{ height: '100%' }}>
    {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
  </div>
);

export const Notifications: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedSearch = useDebounce(searchQuery, 300);
  const { notifications, markNotificationRead, markAllNotificationsRead, removeNotification } = useAppStore();

  const params: PaginationParams = {
    page: page + 1,
    limit: rowsPerPage,
  };

  if (severityFilter) {
    params.severity = severityFilter;
  }

  if (typeFilter) {
    params.type = typeFilter;
  }

  const { data, loading, refetch } = useApi(() => apiClient.getNotifications(params), [
    page,
    rowsPerPage,
    severityFilter,
    typeFilter,
  ]);

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  const handleMarkAllRead = async () => {
    await apiClient.markAllNotificationsRead();
    markAllNotificationsRead();
    refetch();
  };

  const handleMarkRead = async (id: string) => {
    await apiClient.markNotificationRead(id);
    markNotificationRead(id);
  };

  const handleDelete = async (id: string) => {
    removeNotification(id);
  };

  const filteredNotifications = data?.data || [];
  const criticalAlerts = filteredNotifications.filter((n) => n.severity === 'critical');
  const actionRequired = filteredNotifications.filter((n) => n.type === 'action_required');

  if (loading) {
    return <LoadingSpinner message="Loading notifications..." />;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Notifications
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {unreadCount > 0 && (
            <Button
              variant="outlined"
              startIcon={<DoneAllIcon />}
              onClick={handleMarkAllRead}
            >
              Mark All Read
            </Button>
          )}
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            <Badge badgeContent={criticalAlerts.length} color="error">
              <ErrorIcon sx={{ fontSize: 40, color: 'error.main' }} />
            </Badge>
            <Box>
              <Typography variant="h6">{criticalAlerts.length}</Typography>
              <Typography variant="body2" color="text.secondary">
                Critical Alerts
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            <Badge badgeContent={actionRequired.length} color="warning">
              <WarningIcon sx={{ fontSize: 40, color: 'warning.main' }} />
            </Badge>
            <Box>
              <Typography variant="h6">{actionRequired.length}</Typography>
              <Typography variant="body2" color="text.secondary">
                Action Required
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            <Badge badgeContent={unreadCount} color="info">
              <NotificationsIcon sx={{ fontSize: 40, color: 'info.main' }} />
            </Badge>
            <Box>
              <Typography variant="h6">{unreadCount}</Typography>
              <Typography variant="body2" color="text.secondary">
                Unread
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search notifications..."
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
              <InputLabel>Severity</InputLabel>
              <Select
                value={severityFilter}
                label="Severity"
                onChange={(e) => setSeverityFilter(e.target.value)}
              >
                <MenuItem value="">All Severities</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Type</InputLabel>
              <Select
                value={typeFilter}
                label="Type"
                onChange={(e) => setTypeFilter(e.target.value)}
              >
                <MenuItem value="">All Types</MenuItem>
                <MenuItem value="alert">Alert</MenuItem>
                <MenuItem value="warning">Warning</MenuItem>
                <MenuItem value="info">Info</MenuItem>
                <MenuItem value="action_required">Action Required</MenuItem>
                <MenuItem value="risk_assessment">Risk Assessment</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs */}
      <Paper>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
        >
          <Tab label={`All (${filteredNotifications.length})`} />
          <Tab
            label={
              <Badge badgeContent={criticalAlerts.length} color="error">
                Critical
              </Badge>
            }
          />
          <Tab
            label={
              <Badge badgeContent={actionRequired.length} color="warning">
                Action Required
              </Badge>
            }
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <NotificationList
            notifications={filteredNotifications}
            onMarkRead={handleMarkRead}
            onDelete={handleDelete}
          />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <NotificationList
            notifications={criticalAlerts}
            onMarkRead={handleMarkRead}
            onDelete={handleDelete}
          />
        </TabPanel>
        <TabPanel value={tabValue} index={2}>
          <NotificationList
            notifications={actionRequired}
            onMarkRead={handleMarkRead}
            onDelete={handleDelete}
          />
        </TabPanel>
      </Paper>
    </Box>
  );
};

interface NotificationListProps {
  notifications: Notification[];
  onMarkRead: (id: string) => void;
  onDelete: (id: string) => void;
}

const NotificationList: React.FC<NotificationListProps> = ({ notifications, onMarkRead, onDelete }) => {
  if (notifications.length === 0) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography color="text.secondary">No notifications found</Typography>
      </Box>
    );
  }

  return (
    <List sx={{ p: 0 }}>
      {notifications.map((notification, index) => (
        <React.Fragment key={notification.id}>
          <ListItem
            sx={{
              py: 2,
              px: 3,
              bgcolor: notification.isRead ? 'transparent' : 'action.hover',
              '&:hover': {
                bgcolor: 'action.selected',
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 48 }}>
              {getSeverityIcon(notification.severity)}
            </ListItemIcon>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Typography variant="subtitle1" fontWeight={notification.isRead ? 400 : 600}>
                    {notification.title}
                  </Typography>
                  <Chip
                    label={notification.severity}
                    size="small"
                    color={getSeverityColor(notification.severity)}
                  />
                  <Chip
                    label={getTypeLabel(notification.type)}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              }
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    {notification.message}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatDate(notification.createdAt)}
                  </Typography>
                </Box>
              }
            />
            <ListItemSecondaryAction>
              {!notification.isRead && (
                <IconButton
                  edge="end"
                  size="small"
                  onClick={() => onMarkRead(notification.id)}
                  sx={{ mr: 1 }}
                >
                  <CheckIcon fontSize="small" />
                </IconButton>
              )}
              <IconButton
                edge="end"
                size="small"
                onClick={() => onDelete(notification.id)}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
          {index < notifications.length - 1 && <Divider />}
        </React.Fragment>
      ))}
    </List>
  );
};

export default Notifications;
