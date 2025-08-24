import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import { format } from 'date-fns';
import axios from 'axios';

import ScoreGauge from '../components/ScoreGauge';

const CompanyDetail = () => {
  const { id } = useParams();
  const [company, setCompany] = useState(null);
  const [scoreHistory, setScoreHistory] = useState([]);
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCompanyData();
  }, [id]);

  const fetchCompanyData = async () => {
    try {
      setLoading(true);
      
      // Fetch company info, score history, and explanation in parallel
      const [companyResponse, historyResponse, explanationResponse] = await Promise.all([
        axios.get(`/companies/${id}/score`),
        axios.get(`/companies/${id}/scores?days=30`),
        axios.get(`/companies/${id}/explanation`)
      ]);

      setCompany(companyResponse.data);
      setScoreHistory(historyResponse.data);
      setExplanation(explanationResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch company data');
      console.error('Company detail fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatChartData = (data) => {
    return data.map(item => ({
      date: format(new Date(item.time), 'MMM dd'),
      score: parseFloat(item.score),
      confidence: parseFloat(item.confidence || 0)
    })).reverse();
  };

  const formatFeatureData = (features) => {
    return Object.entries(features)
      .sort(([,a], [,b]) => b.importance - a.importance)
      .slice(0, 10)
      .map(([name, data]) => ({
        name: name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        importance: data.importance,
        value: data.shap_value,
        current: data.value
      }));
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

  const chartData = formatChartData(scoreHistory);
  const featureData = explanation ? formatFeatureData(explanation.feature_contributions) : [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Company Analysis
      </Typography>

      <Grid container spacing={3}>
        {/* Company Overview */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="center" mb={2}>
                <ScoreGauge score={explanation?.score || 0} />
              </Box>
              
              <Typography variant="h6" align="center" gutterBottom>
                Current Credit Score
              </Typography>
              
              <Box textAlign="center">
                <Typography variant="body2" color="text.secondary">
                  Confidence: {explanation?.confidence ? `${Math.round(explanation.confidence)}%` : 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Last Updated: {explanation?.timestamp ? format(new Date(explanation.timestamp), 'MMM dd, yyyy HH:mm') : 'N/A'}
                </Typography>
              </Box>

              {explanation?.summary && (
                <Box mt={2}>
                  <Typography variant="body2">
                    {explanation.summary}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Score History Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Score History (30 Days)
              </Typography>
              
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[300, 850]} />
                  <Tooltip 
                    formatter={(value, name) => [
                      name === 'score' ? `${value.toFixed(1)}` : `${value.toFixed(1)}%`,
                      name === 'score' ? 'Credit Score' : 'Confidence'
                    ]}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#1976d2" 
                    strokeWidth={2}
                    dot={{ fill: '#1976d2', strokeWidth: 2, r: 4 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="confidence" 
                    stroke="#ff9800" 
                    strokeWidth={1}
                    strokeDasharray="5 5"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Feature Importance */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Feature Importance
              </Typography>
              
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={featureData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={120} />
                  <Tooltip 
                    formatter={(value) => [value.toFixed(4), 'Importance']}
                  />
                  <Bar dataKey="importance" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Feature Details Table */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Feature Analysis
              </Typography>
              
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Feature</TableCell>
                      <TableCell align="right">Current Value</TableCell>
                      <TableCell align="right">SHAP Value</TableCell>
                      <TableCell align="right">Impact</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {featureData.slice(0, 8).map((feature, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2">
                            {feature.name}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          {feature.current.toFixed(2)}
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={feature.value.toFixed(3)}
                            size="small"
                            color={feature.value > 0 ? 'success' : 'error'}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell align="right">
                          {feature.value > 0 ? 'Positive' : 'Negative'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Events */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Events & News
              </Typography>
              
              {explanation?.recent_events?.length > 0 ? (
                <List>
                  {explanation.recent_events.map((event, index) => (
                    <React.Fragment key={index}>
                      <ListItem alignItems="flex-start">
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="subtitle2">
                                {event.headline}
                              </Typography>
                              <Chip
                                label={event.event_type || 'General'}
                                size="small"
                                variant="outlined"
                              />
                              {event.sentiment && (
                                <Chip
                                  label={`Sentiment: ${event.sentiment.toFixed(1)}`}
                                  size="small"
                                  color={event.sentiment > 60 ? 'success' : event.sentiment < 40 ? 'error' : 'default'}
                                />
                              )}
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                Impact Score: {event.impact?.toFixed(1) || 'N/A'}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {format(new Date(event.timestamp), 'MMM dd, yyyy HH:mm')}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < explanation.recent_events.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">
                  No recent events available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CompanyDetail;