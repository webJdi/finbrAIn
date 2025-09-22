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
  Stepper,
  Step,
  StepLabel,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  ExpandMore,
  PlayArrow,
  Article,
  Psychology,
  Summarize,
} from '@mui/icons-material';
import { useMutation } from '@tanstack/react-query';

const API_BASE_URL = 'http://localhost:8000';

const processingSteps = [
  'Ingest & Validate',
  'Preprocess Text',
  'Classify Content',
  'Extract Insights',
  'Generate Summary'
];

export default function NewsProcessing() {
  const [newsText, setNewsText] = useState('');
  const [results, setResults] = useState(null);

  // Mutation for news processing
  const processingMutation = useMutation({
    mutationFn: async (newsArticles) => {
      const response = await fetch(`${API_BASE_URL}/api/analysis/news/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          news_articles: newsArticles,
          processing_type: 'full_chain'
        }),
      });
      if (!response.ok) throw new Error('Failed to process news');
      return response.json();
    },
    onSuccess: (data) => {
      setResults(data);
    },
  });

  const handleProcess = () => {
    if (!newsText.trim()) return;

    // Parse the input - either multiple articles or single article
    const articles = parseNewsInput(newsText);
    processingMutation.mutate(articles);
  };

  const parseNewsInput = (input) => {
    // Simple parsing - in a real app, this would be more sophisticated
    const lines = input.split('\n').filter(line => line.trim());
    
    if (lines.length === 1) {
      // Single article
      return [{
        title: "User Provided News",
        content: input.trim(),
        date: new Date().toISOString(),
        source: "User Input",
        url: ""
      }];
    } else {
      // Multiple articles - assume each paragraph is an article
      return lines.map((line, index) => ({
        title: `News Article ${index + 1}`,
        content: line.trim(),
        date: new Date().toISOString(),
        source: "User Input",
        url: ""
      }));
    }
  };

  const loadSampleNews = () => {
    const sampleNews = `Apple Inc. reported record third-quarter earnings with revenue of $50 billion, beating analyst expectations. The company's services division showed strong growth, contributing significantly to the overall performance. CEO Tim Cook highlighted the success of the new iPhone lineup and expansion in emerging markets.

Federal Reserve Chair Jerome Powell indicated that the central bank may consider interest rate cuts in the upcoming meetings, citing concerns about economic growth. The announcement led to immediate market reactions, with technology stocks seeing significant gains. Investors are closely watching inflation data for further guidance.

Tesla announced a major expansion of its Supercharger network, planning to double the number of charging stations by end of 2024. The electric vehicle manufacturer also reported strong quarterly deliveries, exceeding market expectations. The stock rallied on the positive news and outlook.`;

    setNewsText(sampleNews);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        News Processing Chain
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Process financial news through the complete LangChain workflow: Ingest → Preprocess → Classify → Extract → Summarize
      </Typography>

      {/* Input Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              News Articles Input
            </Typography>
            <Button 
              variant="outlined" 
              size="small" 
              onClick={loadSampleNews}
              sx={{ mb: 2 }}
            >
              Load Sample News
            </Button>
          </Box>
          
          <TextField
            multiline
            rows={8}
            fullWidth
            variant="outlined"
            placeholder="Paste news articles here... (one article per paragraph for multiple articles)"
            value={newsText}
            onChange={(e) => setNewsText(e.target.value)}
            sx={{ mb: 2 }}
          />
          
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Button
              variant="contained"
              onClick={handleProcess}
              disabled={!newsText.trim() || processingMutation.isPending}
              startIcon={<PlayArrow />}
            >
              Process News
            </Button>
            
            {processingMutation.isPending && (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                <Typography variant="body2">Processing through chain...</Typography>
              </Box>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Processing Steps */}
      {processingMutation.isPending && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Processing Pipeline
            </Typography>
            <Stepper activeStep={2} alternativeLabel>
              {processingSteps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {processingMutation.isError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Processing Error: {processingMutation.error?.message}
        </Alert>
      )}

      {/* Results Display */}
      {results && (
        <Box>
          {results.success ? (
            <Box>
              {/* Final Summary */}
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Summarize sx={{ mr: 1 }} />
                    <Typography variant="h6">Final Investment Summary</Typography>
                    <Chip 
                      label={`${results.processed_articles} articles processed`} 
                      size="small" 
                      sx={{ ml: 2 }} 
                    />
                  </Box>
                  <Paper sx={{ p: 2, bgcolor: 'primary.50' }}>
                    <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
                      {results.final_summary}
                    </Typography>
                  </Paper>
                </CardContent>
              </Card>

              {/* Chain Results Details */}
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Psychology sx={{ mr: 1 }} />
                    <Typography variant="h6">Processing Chain Details</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    {/* Ingested Data */}
                    {results.chain_results?.ingested && (
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle1" gutterBottom>
                          1. Ingestion Results
                        </Typography>
                        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                          <Typography variant="body2">
                            Valid Articles: {results.chain_results.ingested.valid_articles?.length || 0}
                          </Typography>
                          <Typography variant="body2">
                            Rejected Articles: {results.chain_results.ingested.rejected_count || 0}
                          </Typography>
                          {results.chain_results.ingested.rejection_reasons?.length > 0 && (
                            <Typography variant="body2">
                              Rejection Reasons: {results.chain_results.ingested.rejection_reasons.join(', ')}
                            </Typography>
                          )}
                        </Paper>
                      </Box>
                    )}

                    {/* Preprocessed Data */}
                    {results.chain_results?.preprocessed && (
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle1" gutterBottom>
                          2. Preprocessing Results
                        </Typography>
                        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                          {results.chain_results.preprocessed.preprocessed_articles?.map((article, index) => (
                            <Box key={index} sx={{ mb: 2 }}>
                              <Typography variant="body2" fontWeight="bold">
                                Article {index + 1}: {article.title}
                              </Typography>
                              {article.entities && (
                                <Box sx={{ mt: 1 }}>
                                  <Typography variant="caption">
                                    Companies: {article.entities.companies?.join(', ') || 'None'}
                                  </Typography>
                                  <br />
                                  <Typography variant="caption">
                                    Financial Terms: {article.entities.financial_terms?.join(', ') || 'None'}
                                  </Typography>
                                </Box>
                              )}
                            </Box>
                          ))}
                        </Paper>
                      </Box>
                    )}

                    {/* Classification Results */}
                    {results.chain_results?.classified && (
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle1" gutterBottom>
                          3. Classification Results
                        </Typography>
                        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                          {results.chain_results.classified.classified_articles?.map((article, index) => (
                            <Box key={index} sx={{ mb: 2 }}>
                              <Typography variant="body2" fontWeight="bold">
                                {article.title}
                              </Typography>
                              {article.classifications && (
                                <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                  <Chip 
                                    label={`Type: ${article.classifications.news_type}`} 
                                    size="small" 
                                  />
                                  <Chip 
                                    label={`Sentiment: ${article.classifications.sentiment}`} 
                                    size="small"
                                    color={
                                      article.classifications.sentiment === 'positive' ? 'success' :
                                      article.classifications.sentiment === 'negative' ? 'error' : 'default'
                                    }
                                  />
                                  <Chip 
                                    label={`Impact: ${article.classifications.impact_level}`} 
                                    size="small" 
                                  />
                                </Box>
                              )}
                            </Box>
                          ))}
                        </Paper>
                      </Box>
                    )}

                    {/* Extraction Results */}
                    {results.chain_results?.extracted && (
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle1" gutterBottom>
                          4. Information Extraction
                        </Typography>
                        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                          {results.chain_results.extracted.extracted_articles?.map((article, index) => (
                            <Accordion key={index} sx={{ mb: 1 }}>
                              <AccordionSummary expandIcon={<ExpandMore />}>
                                <Typography variant="body2">{article.title}</Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                {article.key_facts && (
                                  <Box sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2">Key Facts:</Typography>
                                    <List dense>
                                      {article.key_facts.financial_figures?.map((fact, i) => (
                                        <ListItem key={i}><ListItemText primary={fact} /></ListItem>
                                      ))}
                                    </List>
                                  </Box>
                                )}
                                {article.investment_implications && (
                                  <Box>
                                    <Typography variant="subtitle2">Investment Implications:</Typography>
                                    <Typography variant="body2">
                                      {article.investment_implications.price_impact}
                                    </Typography>
                                  </Box>
                                )}
                              </AccordionDetails>
                            </Accordion>
                          ))}
                        </Paper>
                      </Box>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            </Box>
          ) : (
            <Alert severity="error">
              Processing failed: {results.error}
            </Alert>
          )}
        </Box>
      )}
    </Box>
  );
}