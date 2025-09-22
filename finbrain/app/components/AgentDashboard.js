'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
} from '@mui/material';
import {
  SmartToy,
  Psychology,
  TrendingUp,
  Assessment,
  Timeline,
  ExpandMore,
  Refresh,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = 'http://localhost:8000';

export default function AgentDashboard() {
  const [systemStats, setSystemStats] = useState({
    totalAnalyses: 0,
    successfulAnalyses: 0,
    averageQualityScore: 0,
    agentUptime: '00:00:00'
  });

  // Query for agent health status
  const { data: agentHealth, isLoading: healthLoading, refetch: refetchHealth } = useQuery({
    queryKey: ['agentHealth'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/agents/health`);
      if (!response.ok) throw new Error('Failed to fetch agent health');
      return response.json();
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Query for workflow status
  const { data: workflowStatus, isLoading: workflowLoading, refetch: refetchWorkflows } = useQuery({
    queryKey: ['workflowStatus'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/analysis/workflows/status`);
      if (!response.ok) throw new Error('Failed to fetch workflow status');
      return response.json();
    },
    refetchInterval: 30000,
  });

  // Simulate uptime counter
  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const hours = Math.floor(elapsed / 3600000);
      const minutes = Math.floor((elapsed % 3600000) / 60000);
      const seconds = Math.floor((elapsed % 60000) / 1000);
      setSystemStats(prev => ({
        ...prev,
        agentUptime: `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'available':
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'unavailable':
        return 'error';
      default:
        return 'default';
    }
  };

  const getHealthStatusIcon = (status) => {
    switch (status) {
      case 'available':
      case 'healthy':
        return <CheckCircle color="success" />;
      case 'degraded':
        return <Error color="warning" />;
      case 'unavailable':
        return <Error color="error" />;
      default:
        return <CircularProgress size={20} />;
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Agent Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Monitor the status and performance of all financial analysis agents and workflows.
      </Typography>

      {/* System Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SmartToy color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Agent Uptime</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {systemStats.agentUptime}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Assessment color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Analyses</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {systemStats.totalAnalyses}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {systemStats.successfulAnalyses} successful
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Avg Quality</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {systemStats.averageQualityScore.toFixed(1)}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={systemStats.averageQualityScore * 10} 
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Timeline color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">System Status</Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                Online
              </Typography>
              <Chip label="All Systems Operational" size="small" color="success" />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Agent Services Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Agent Services</Typography>
            <Button 
              startIcon={<Refresh />} 
              onClick={() => refetchHealth()}
              disabled={healthLoading}
            >
              Refresh
            </Button>
          </Box>
          
          {healthLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
              <CircularProgress />
            </Box>
          ) : agentHealth ? (
            <List>
              {Object.entries(agentHealth.services || {}).map(([service, status]) => (
                <ListItem key={service}>
                  <ListItemIcon>
                    {getHealthStatusIcon(status)}
                  </ListItemIcon>
                  <ListItemText 
                    primary={service.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    secondary={`Status: ${status}`}
                  />
                  <Chip 
                    label={status} 
                    size="small" 
                    color={getHealthStatusColor(status)}
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Alert severity="warning">
              Unable to fetch agent health status
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Workflow Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Workflow Status</Typography>
            <Button 
              startIcon={<Refresh />} 
              onClick={() => refetchWorkflows()}
              disabled={workflowLoading}
            >
              Refresh
            </Button>
          </Box>
          
          {workflowLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
              <CircularProgress />
            </Box>
          ) : workflowStatus ? (
            <Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Available Workflows: {workflowStatus.available_workflows} / {workflowStatus.total_workflows}
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={(workflowStatus.available_workflows / workflowStatus.total_workflows) * 100}
                  sx={{ mt: 1 }}
                />
              </Box>
              
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="subtitle1">Workflow Details</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List>
                    {Object.entries(workflowStatus.workflows || {}).map(([workflow, info]) => (
                      <ListItem key={workflow}>
                        <ListItemIcon>
                          {getHealthStatusIcon(info.available ? 'available' : 'unavailable')}
                        </ListItemIcon>
                        <ListItemText 
                          primary={workflow.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          secondary={`${info.description} | Endpoint: ${info.endpoint}`}
                        />
                        <Chip 
                          label={info.available ? 'Available' : 'Unavailable'} 
                          size="small" 
                          color={info.available ? 'success' : 'error'}
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            </Box>
          ) : (
            <Alert severity="warning">
              Unable to fetch workflow status
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Agent Memory & Learning */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Agent Memory & Learning
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Memory System
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • SQLite storage for structured learning sessions
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Vector store for semantic memory search
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Persistent learning across agent runs
                </Typography>
                <Chip label="Active" size="small" color="success" sx={{ mt: 1 }} />
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Learning Progress
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Self-reflection on analysis quality
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Improvement suggestions storage
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Performance tracking over time
                </Typography>
                <Chip label="Improving" size="small" color="info" sx={{ mt: 1 }} />
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
}