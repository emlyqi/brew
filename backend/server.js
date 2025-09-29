const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// middleware
app.use(cors());
app.use(express.json());

// Python ML service URL - use environment variable for production
const PYTHON_ML_URL = process.env.PYTHON_ML_URL || 'http://127.0.0.1:8000';

// health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'Brew API is running!',
    ml_service_url: PYTHON_ML_URL
  });
});

// search profiles endpoint
app.get('/api/search', async (req, res) => {
  try {
    const { query, num_results = 10 } = req.query;
    
    if (!query) {
      return res.status(400).json({ error: 'query parameter is required' });
    }

    console.log(`searching for: "${query}" (${num_results} results)`);
    console.log(`calling ML service at: ${PYTHON_ML_URL}`);

    // call Python ML service
    const response = await axios.get(`${PYTHON_ML_URL}/search`, {
      params: { query, num_results },
      timeout: 10000
    });

    res.json(response.data);

  } catch (error) {
    console.error('search error:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      res.status(503).json({ 
        error: 'ML service unavailable', 
        message: `cannot connect to ML service at ${PYTHON_ML_URL}` 
      });
    } else {
      res.status(500).json({ 
        error: 'internal server error', 
        message: error.message 
      });
    }
  }
});

// get profile by ID endpoint
app.get('/api/profile/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const response = await axios.get(`${PYTHON_ML_URL}/profile/${id}`);
    res.json(response.data);

  } catch (error) {
    console.error('profile fetch error:', error.message);
    res.status(500).json({ error: 'failed to fetch profile' });
  }
});

// get all profiles endpoint
app.get('/api/profiles', async (req, res) => {
  try {
    const response = await axios.get(`${PYTHON_ML_URL}/profiles`);
    res.json(response.data);

  } catch (error) {
    console.error('profiles fetch error:', error.message);
    res.status(500).json({ error: 'failed to fetch profiles' });
  }
});

// generate message endpoint
app.post('/api/generate-message', async (req, res) => {
  try {
    const { profile, tone, yourContext } = req.body;
    
    if (!profile || !tone || !yourContext) {
      return res.status(400).json({ error: 'profile, tone, and yourContext are required' });
    }

    console.log(`generating ${tone} message for ${profile.name}`);

    // call Python ML service for message generation
    const response = await axios.post(`${PYTHON_ML_URL}/generate-message`, {
      profile,
      tone,
      yourContext
    }, {
      timeout: 15000
    });

    res.json(response.data);

  } catch (error) {
    console.error('message generation error:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      res.status(503).json({ 
        error: 'ML service unavailable', 
        message: `cannot connect to ML service at ${PYTHON_ML_URL}` 
      });
    } else {
      res.status(500).json({ 
        error: 'internal server error', 
        message: error.message 
      });
    }
  }
});

// start server
app.listen(PORT, () => {
  console.log(`Brew API running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`Search endpoint: http://localhost:${PORT}/api/search`);
  console.log(`ML service URL: ${PYTHON_ML_URL}`);
});