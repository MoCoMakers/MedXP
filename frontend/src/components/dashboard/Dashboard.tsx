import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  IconButton,
  Tooltip,
  Skeleton,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  People as PeopleIcon,
  LocalHospital as HospitalIcon,
  VideoLibrary as VideoIcon,
  Warning as WarningIcon,
  Notifications as NotificationsIcon,
  ArrowForward as ArrowForwardIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useApi } from '../../hooks';
import { LoadingSpinner } from '../common/LoadingSpinner';
import apiClient from '../../services/api';
import type { DashboardStats, Notification, RiskTrend } from '../../types';

const COLORS = ['#4caf50', '#ff9800', '#f44336', '#9c27b0'];

interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: { value: number; positive: boolean };
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, subtitle, icon, trend, color }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography color="text.secondary" variant="body2" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" component="div" sx={{ fontWeight: 600, mb: 1 }}>
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
          {trend && (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
              {trend.positive ? (
                <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main', mr: 0.5 }} />
              ) : (
                <TrendingDownIcon sx={{ fontSize: 16, color: 'error.main', mr: 0.5 }} />
              )}
              <Typography
                variant="body2"
                sx={{ color: trend.positive ? 'success.main' : 'error.main' }}
              >
                {trend.value}% from last week
              </Typography>
            </Box>
          )}
        </Box>
        <Avatar sx={{ bgcolor: `${color}15`, color: color }}>
          {icon}
        </Avatar>
      </Box>
    </CardContent>
  </Card>
);

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [refreshing, setRefreshing] = useState(false);

  const { data: stats, loading: statsLoading, refetch: refetchStats } = useApi<DashboardStats>(
    () => apiClient.getDashboardStats()
  );

  const { data: riskTrends, loading: trendsLoading } = useApi<RiskTrend[]>(
    () => apiClient.getRiskTrends(14)
  );

  const { data: notifications, loading: notificationsLoading } = useApi<Notification[]>(
    () => apiClient.getAlerts()
  );

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetchStats();
    setRefreshing(false);
  };

  const formatRiskData = (trends: RiskTrend[] | null) => {
    if (!trends) return [];
    return trends.map((t) => ({
      date: new Date(t.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      low: t.low,
      medium: t.medium,
      high: t.high,
      critical: t.critical,
    }));
  };

  const getRiskDistribution = (stats: DashboardStats | null) => {
    if (!stats) return [];
    return [
      { name: 'Low', value: 65 },
      { name: 'Medium', value: 25 },
      { name: 'High', value: 8 },
      { name: 'Critical', value: 2 },
    ];
  };

  if (statsLoading || trendsLoading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Dashboard
        </Typography>
        <Tooltip title="Refresh data">
          <IconButton onClick={handleRefresh} disabled={refreshing}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Total Nurses"
            value={stats?.totalNurses || 0}
            subtitle="Active in system"
            icon={<PeopleIcon />}
            trend={{ value: 12, positive: true }}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Total Patients"
            value={stats?.totalPatients || 0}
            subtitle="Enrolled in program"
            icon={<HospitalIcon />}
            trend={{ value: 8, positive: true }}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Active Sessions"
            value={stats?.activeSessions || 0}
            subtitle="Currently recording"
            icon={<VideoIcon />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Avg Risk Score"
            value={`${((stats?.averageRiskScore || 0) * 100).toFixed(1)}%`}
            subtitle="Overall assessment"
            icon={<WarningIcon />}
            trend={{ value: 5, positive: false }}
            color="#d32f2f"
          />
        </Grid>

        {/* Risk Trend Chart */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Risk Trend (Last 14 Days)
            </Typography>
            {trendsLoading ? (
              <Skeleton variant="rectangular" height={300} />
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={formatRiskData(riskTrends)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <RechartsTooltip />
                  <Line type="monotone" dataKey="low" stroke="#4caf50" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="medium" stroke="#ff9800" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="high" stroke="#f44336" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="critical" stroke="#9c27b0" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>

        {/* Risk Distribution Pie Chart */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Risk Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={getRiskDistribution(stats)}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {getRiskDistribution(stats).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
              {getRiskDistribution(stats).map((item, index) => (
                <Box key={item.name} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: COLORS[index] }} />
                  <Typography variant="caption">{item.name}</Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Recent Alerts */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 0 }}>
            <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">Recent Alerts</Typography>
              <IconButton size="small" onClick={() => navigate('/notifications')}>
                <ArrowForwardIcon />
              </IconButton>
            </Box>
            {notificationsLoading ? (
              <Box sx={{ p: 3 }}>
                <Skeleton height={60} />
                <Skeleton height={60} />
                <Skeleton height={60} />
              </Box>
            ) : notifications && notifications.length > 0 ? (
              <List sx={{ p: 0 }}>
                {notifications.slice(0, 5).map((notification) => (
                  <ListItem
                    key={notification.id}
                    divider
                    sx={{ py: 1.5 }}
                    secondaryAction={
                      <Chip
                        label={notification.severity}
                        size="small"
                        color={
                          notification.severity === 'critical'
                            ? 'error'
                            : notification.severity === 'high'
                            ? 'warning'
                            : 'info'
                        }
                      />
                    }
                  >
                    <ListItemIcon>
                      <NotificationsIcon
                        sx={{
                          color:
                            notification.severity === 'critical'
                              ? 'error.main'
                              : notification.severity === 'high'
                              ? 'warning.main'
                              : 'info.main',
                        }}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={notification.title}
                      secondary={new Date(notification.createdAt).toLocaleString()}
                      primaryTypographyProps={{ noWrap: true }}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Typography color="text.secondary">No recent alerts</Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              {[
                { label: 'View All Nurses', icon: <PeopleIcon />, path: '/nurses', color: '#1976d2' },
                { label: 'View All Patients', icon: <HospitalIcon />, path: '/patients', color: '#2e7d32' },
                { label: 'View Sessions', icon: <VideoIcon />, path: '/sessions', color: '#ed6c02' },
                { label: 'Notifications', icon: <NotificationsIcon />, path: '/notifications', color: '#9c27b0' },
              ].map((action) => (
                <Grid item xs={6} key={action.label}>
                  <Card
                    sx={{
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: 3,
                      },
                    }}
                    onClick={() => navigate(action.path)}
                  >
                    <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ bgcolor: `${action.color}15`, color: action.color }}>
                        {action.icon}
                      </Avatar>
                      <Typography variant="body1">{action.label}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
