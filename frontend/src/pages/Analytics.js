import React, { useState, useEffect } from "react";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import axios from "axios";

const Analytics = () => {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      const [companiesResponse, analyticsResponse] = await Promise.all([
        axios.get("/companies"),
        axios.get("/analytics"),
      ]);

      setCompanies(companiesResponse.data);
      console.log("Analytics data:", analyticsResponse.data);
      setError(null);
    } catch (err) {
      setError(`Failed to fetch analytics data: ${err.message}`);
      console.error("Analytics fetch error:", err);
      
      // Set sample data as fallback
      setCompanies([
        { id: 1, name: "Apple Inc.", symbol: "AAPL" },
        { id: 2, name: "Microsoft Corporation", symbol: "MSFT" }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Mock data for demonstration
  const sectorDistribution = [
    { name: "Technology", value: 40, color: "#1976d2" },
    { name: "Financial Services", value: 25, color: "#dc004e" },
    { name: "Healthcare", value: 15, color: "#4caf50" },
    { name: "Consumer Cyclical", value: 12, color: "#ff9800" },
    { name: "Energy", value: 8, color: "#9c27b0" },
  ];

  const revenueTrends = [
    { month: "Jan", revenue: 400 },
    { month: "Feb", revenue: 600 },
    { month: "Mar", revenue: 800 },
    { month: "Apr", revenue: 700 },
    { month: "May", revenue: 1000 },
  ];

  const riskScores = [
    { company: "A", risk: 70 },
    { company: "B", risk: 50 },
    { company: "C", risk: 90 },
    { company: "D", risk: 40 },
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Analytics Dashboard
      </Typography>

      {/* Dropdown for company filter */}
      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>Company</InputLabel>
        <Select
          value={selectedCompany}
          label="Company"
          onChange={(e) => setSelectedCompany(e.target.value)}
        >
          <MenuItem value="all">All</MenuItem>
          {companies.map((c) => (
            <MenuItem key={c.id} value={c.name}>
              {c.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <Grid container spacing={3}>
          {/* Pie Chart: Sector Distribution */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6">Sector Distribution</Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={sectorDistribution}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label
                    >
                      {sectorDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Line Chart: Revenue Trends */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6">Revenue Trends</Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={revenueTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="revenue"
                      stroke="#1976d2"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Bar Chart: Risk Scores */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6">Risk Scores</Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={riskScores}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="company" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="risk" fill="#dc004e" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default Analytics;
