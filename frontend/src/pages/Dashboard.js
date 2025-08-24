import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import axios from 'axios';

import ScoreGauge from '../components/ScoreGauge';
import AlertsPanel from '../components/AlertsPanel';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    // Refresh data every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/dashboard');
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 750) return '#4caf50'; // Green
    if (score >= 650) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const getScoreLabel = (score) => {
    if (score >= 750) return 'Excellent';
    if (score >= 650) return 'Good';
    if (score >= 550) return 'Fair';
    return 'Poor';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Credit Intelligence Dashboard
      </Typography>
      
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Real-time credit risk assessment and monitoring
      </Typography>

      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Companies
              </Typography>
              <Typography variant="h4">
                {dashboardData?.total_companies || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Alerts
              </Typography>
              <Typography variant="h4" color="error">
                {dashboardData?.alerts?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Credit Score
              </Typography>
              <Typography variant="h4">
                {dashboardData?.companies?.length > 0
                  ? Math.round(
                      dashboardData.companies.reduce((sum, c) => sum + c.current_score, 0) /
                      dashboardData.companies.length
                    )
                  : 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Last Updated
              </Typography>
              <Typography variant="h6">
                {dashboardData?.last_updated
                  ? format(new Date(dashboardData.last_updated), 'HH:mm:ss')
                  : 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Alerts Panel */}
        {dashboardData?.alerts?.length > 0 && (
          <Grid item xs={12}>
            <AlertsPanel alerts={dashboardData.alerts} />
          </Grid>
        )}

        {/* Companies Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Company Credit Scores
              </Typography>
              
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Company</TableCell>
                      <TableCell>Sector</TableCell>
                      <TableCell align="center">Credit Score</TableCell>
                      <TableCell align="center">Rating</TableCell>
                      <TableCell align="center">Confidence</TableCell>
                      <TableCell align="center">Last Updated</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {dashboardData?.companies?.map((company) => (
                      <TableRow key={company.id} hover>
                        <TableCell>
                          <Box>
                            <Typography variant="subtitle2">
                              {company.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {company.symbol}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={company.sector || 'N/A'}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Box display="flex" justifyContent="center" alignItems="center">
                            <ScoreGauge
                              score={company.current_score}
                              size={60}
                              showLabel={false}
                            />
                            <Typography variant="h6" sx={{ ml: 1 }}>
                              {Math.round(company.current_score)}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={getScoreLabel(company.current_score)}
                            size="small"
                            sx={{
                              backgroundColor: getScoreColor(company.current_score),
                              color: 'white'
                            }}
                          />
                        </TableCell>
                        <TableCell align="center">
                          {company.confidence ? `${Math.round(company.confidence)}%` : 'N/A'}
                        </TableCell>
                        <TableCell align="center">
                          {company.last_updated
                            ? format(new Date(company.last_updated), 'MMM dd, HH:mm')
                            : 'N/A'}
                        </TableCell>
                        <TableCell align="center">
                          <Button
                            component={Link}
                            to={`/company/${company.id}`}
                            variant="outlined"
                            size="small"
                          >
                            Details
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;