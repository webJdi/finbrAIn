'use client';

import { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Tab,
  Tabs,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  Analytics,
  Assessment,
  SmartToy,
} from '@mui/icons-material';

// Import our custom components
import StockAnalysis from './components/StockAnalysis';
import NewsProcessing from './components/NewsProcessing';
import AgentDashboard from './components/AgentDashboard';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function FinbrainDashboard() {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          FinbrAIn
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Multi-Agent Financial Advisory System
        </Typography>
        <Typography variant="body1" color="text.secondary">
          AI-powered financial research using LangChain, LangGraph, and advanced agent workflows
        </Typography>
      </Box>

      {/* Feature Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUp color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Stock Research</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Autonomous investment research with self-reflection and learning
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Analytics color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">News Processing</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                News → Preprocess → Classify → Extract → Summarize pipeline
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Assessment color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Content Routing</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Intelligent routing to specialist agents based on content
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SmartToy color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Quality Optimization</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Evaluate analysis quality and optimize using feedback loops
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange} 
            aria-label="FinbrAIn features"
            variant="fullWidth"
          >
            <Tab label="Stock Analysis" />
            <Tab label="News Processing" />
            <Tab label="Agent Dashboard" />
            <Tab label="System Status" />
          </Tabs>
        </Box>

        <TabPanel value={activeTab} index={0}>
          <StockAnalysis />
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <NewsProcessing />
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <AgentDashboard />
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <SystemStatus />
        </TabPanel>
      </Paper>
    </Container>
  );
}

// System Status Component
function SystemStatus() {
  const [backendStatus, setBackendStatus] = useState('checking...');
  const [loading, setLoading] = useState(true);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setBackendStatus('online');
      } else {
        setBackendStatus('error');
      }
    } catch (error) {
      setBackendStatus('offline');
    } finally {
      setLoading(false);
    }
  };

  useState(() => {
    checkBackendStatus();
  }, []);

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        System Status
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Backend API
              </Typography>
              {loading ? (
                <CircularProgress size={20} />
              ) : (
                <Alert 
                  severity={backendStatus === 'online' ? 'success' : 'error'}
                  sx={{ mt: 1 }}
                >
                  Status: {backendStatus}
                  {backendStatus === 'online' && ' - All services operational'}
                  {backendStatus === 'offline' && ' - Backend not running on localhost:8000'}
                </Alert>
              )}
            </CardContent>
            <CardActions>
              <Button size="small" onClick={checkBackendStatus}>
                Refresh Status
              </Button>
              {backendStatus === 'online' && (
                <Button size="small" href="http://localhost:8000/docs" target="_blank">
                  View API Docs
                </Button>
              )}
            </CardActions>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Frontend Application
              </Typography>
              <Alert severity="success" sx={{ mt: 1 }}>
                Status: Running - Next.js with MUI components loaded
              </Alert>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Quick Start Instructions
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          1. Make sure your backend is running: <code>cd backend && python app/main.py</code>
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          2. Configure your API keys in the backend <code>.env</code> file
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          3. Use the Stock Analysis tab to research any stock symbol
        </Typography>
        <Typography variant="body2" color="text.secondary">
          4. Try the News Processing to analyze financial news articles
        </Typography>
      </Box>
    </Box>
  );
}
