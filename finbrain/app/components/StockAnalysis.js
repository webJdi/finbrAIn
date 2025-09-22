'use client';

import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  ExpandMore,
  Search,
  TrendingUp,
  Assessment,
  Timeline,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = 'http://localhost:8000';

export default function StockAnalysis() {
  const [symbol, setSymbol] = useState('');
  const [analysisSymbol, setAnalysisSymbol] = useState('');
  const [showResults, setShowResults] = useState(false);

  // Query for stock research
  const { data: researchData, isLoading: researchLoading, error: researchError } = useQuery({
    queryKey: ['stockResearch', analysisSymbol],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/agents/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: analysisSymbol }),
      });
      if (!response.ok) throw new Error('Failed to fetch research data');
      return response.json();
    },
    enabled: !!analysisSymbol,
  });

  // Query for basic stock data
  const { data: stockData, isLoading: stockLoading } = useQuery({
    queryKey: ['stockData', analysisSymbol],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/agents/data/${analysisSymbol}`);
      if (!response.ok) throw new Error('Failed to fetch stock data');
      return response.json();
    },
    enabled: !!analysisSymbol,
  });

  // Query for stock news
  const { data: newsData, isLoading: newsLoading } = useQuery({
    queryKey: ['stockNews', analysisSymbol],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/agents/news/${analysisSymbol}`);
      if (!response.ok) throw new Error('Failed to fetch news data');
      return response.json();
    },
    enabled: !!analysisSymbol,
  });

  const handleAnalyze = () => {
    if (symbol.trim()) {
      setAnalysisSymbol(symbol.trim().toUpperCase());
      setShowResults(true);
    }
  };

  const isLoading = researchLoading || stockLoading || newsLoading;

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Investment Research Agent
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Autonomous stock research using LangGraph workflows with planning, data collection, analysis, and self-reflection.
      </Typography>

      {/* Input Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              label="Stock Symbol"
              variant="outlined"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="e.g., AAPL, MSFT, TSLA"
              sx={{ flexGrow: 1 }}
              onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
            />
            <Button
              variant="contained"
              onClick={handleAnalyze}
              disabled={!symbol.trim() || isLoading}
              startIcon={<Search />}
            >
              Analyze
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Results Section */}
      {showResults && (
        <Box>
          {isLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
              <Typography sx={{ ml: 2 }}>
                Running comprehensive analysis for {analysisSymbol}...
              </Typography>
            </Box>
          )}

          {researchError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Research Error: {researchError.message}
            </Alert>
          )}

          {/* Research Results */}
          {researchData && (
            <Box sx={{ mb: 3 }}>
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Assessment sx={{ mr: 1 }} />
                    <Typography variant="h6">
                      Investment Research Report
                    </Typography>
                    {researchData.success && (
                      <Chip 
                        label={`${researchData.iterations || 1} iterations`} 
                        size="small" 
                        sx={{ ml: 2 }} 
                      />
                    )}
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {researchData.success ? (
                    <Box>
                      {/* Research Plan */}
                      {researchData.research_plan && researchData.research_plan.length > 0 && (
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle1" gutterBottom>
                            Research Plan:
                          </Typography>
                          <List dense>
                            {researchData.research_plan.map((step, index) => (
                              <ListItem key={index}>
                                <ListItemText primary={`${index + 1}. ${step}`} />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}

                      {/* Final Report */}
                      {researchData.analysis?.final_report && (
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle1" gutterBottom>
                            Analysis Report:
                          </Typography>
                          <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                            <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                              {researchData.analysis.final_report}
                            </Typography>
                          </Paper>
                        </Box>
                      )}

                      {/* Quality Assessment */}
                      {researchData.quality_assessment && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle1" gutterBottom>
                            Quality Assessment:
                          </Typography>
                          <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                            <Typography variant="body2">
                              {researchData.quality_assessment.assessment_text || 'Quality assessment completed'}
                            </Typography>
                          </Paper>
                        </Box>
                      )}
                    </Box>
                  ) : (
                    <Alert severity="warning">
                      Research failed: {researchData.error || 'Unknown error'}
                    </Alert>
                  )}
                </AccordionDetails>
              </Accordion>
            </Box>
          )}

          {/* Stock Data */}
          {stockData && (
            <Box sx={{ mb: 3 }}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <TrendingUp sx={{ mr: 1 }} />
                    <Typography variant="h6">Financial Data</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {stockData.success ? (
                    <Grid container spacing={2}>
                      {stockData.data?.yahoo_finance?.company_info && (
                        <Grid item xs={12} md={6}>
                          <Paper sx={{ p: 2 }}>
                            <Typography variant="subtitle1" gutterBottom>
                              Company Information
                            </Typography>
                            <Typography variant="body2">
                              <strong>Name:</strong> {stockData.data.yahoo_finance.company_info.name}
                            </Typography>
                            <Typography variant="body2">
                              <strong>Sector:</strong> {stockData.data.yahoo_finance.company_info.sector}
                            </Typography>
                            <Typography variant="body2">
                              <strong>Market Cap:</strong> ${(stockData.data.yahoo_finance.company_info.market_cap / 1e9).toFixed(2)}B
                            </Typography>
                            <Typography variant="body2">
                              <strong>P/E Ratio:</strong> {stockData.data.yahoo_finance.company_info.pe_ratio?.toFixed(2) || 'N/A'}
                            </Typography>
                          </Paper>
                        </Grid>
                      )}
                      
                      {stockData.data?.yahoo_finance?.price_data && (
                        <Grid item xs={12} md={6}>
                          <Paper sx={{ p: 2 }}>
                            <Typography variant="subtitle1" gutterBottom>
                              Price Information
                            </Typography>
                            <Typography variant="body2">
                              <strong>Current Price:</strong> ${stockData.data.yahoo_finance.price_data.current_price?.toFixed(2)}
                            </Typography>
                            <Typography variant="body2">
                              <strong>Day High:</strong> ${stockData.data.yahoo_finance.price_data.day_high?.toFixed(2)}
                            </Typography>
                            <Typography variant="body2">
                              <strong>Day Low:</strong> ${stockData.data.yahoo_finance.price_data.day_low?.toFixed(2)}
                            </Typography>
                            <Typography variant="body2">
                              <strong>52W High:</strong> ${stockData.data.yahoo_finance.price_data['52_week_high']?.toFixed(2)}
                            </Typography>
                          </Paper>
                        </Grid>
                      )}
                    </Grid>
                  ) : (
                    <Alert severity="info">
                      {stockData.message || 'Financial data not available'}
                    </Alert>
                  )}
                </AccordionDetails>
              </Accordion>
            </Box>
          )}

          {/* News Data */}
          {newsData && (
            <Box sx={{ mb: 3 }}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Timeline sx={{ mr: 1 }} />
                    <Typography variant="h6">Latest News</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {newsData.success && newsData.news?.articles?.length > 0 ? (
                    <List>
                      {newsData.news.articles.slice(0, 5).map((article, index) => (
                        <Box key={index}>
                          <ListItem alignItems="flex-start">
                            <ListItemText
                              primary={article.title}
                              secondary={
                                <Box>
                                  <Typography variant="body2" color="text.secondary">
                                    {article.description}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    Source: {article.source} | {new Date(article.published_at).toLocaleDateString()}
                                  </Typography>
                                </Box>
                              }
                            />
                          </ListItem>
                          {index < 4 && <Divider />}
                        </Box>
                      ))}
                    </List>
                  ) : (
                    <Alert severity="info">
                      No recent news available for {analysisSymbol}
                    </Alert>
                  )}
                </AccordionDetails>
              </Accordion>
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
}