import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Box
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { format } from 'date-fns';

const AlertsPanel = ({ alerts }) => {
  const getAlertIcon = (severity) => {
    switch (severity) {
      case 'high':
        return <ErrorIcon color="error" />;
      case 'medium':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getAlertColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      default:
        return 'info';
    }
  };

  const formatScoreChange = (change) => {
    const sign = change > 0 ? '+' : '';
    return `${sign}${change.toFixed(1)}`;
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Alerts
        </Typography>
        
        {alerts.length === 0 ? (
          <Typography color="text.secondary">
            No recent alerts
          </Typography>
        ) : (
          <List>
            {alerts.map((alert, index) => (
              <ListItem key={index} divider={index < alerts.length - 1}>
                <ListItemIcon>
                  {getAlertIcon(alert.severity)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle2">
                        {alert.company_name} ({alert.company_symbol})
                      </Typography>
                      <Chip
                        label={`${formatScoreChange(alert.score_change)} points`}
                        size="small"
                        color={alert.score_change > 0 ? 'success' : 'error'}
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Credit score changed by {formatScoreChange(alert.score_change)} points
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {format(new Date(alert.timestamp), 'MMM dd, yyyy HH:mm')}
                      </Typography>
                    </Box>
                  }
                />
                <Chip
                  label={alert.severity.toUpperCase()}
                  size="small"
                  color={getAlertColor(alert.severity)}
                />
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
};

export default AlertsPanel;