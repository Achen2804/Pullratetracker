module.exports = async (req, res) => {
    // Set CORS headers for all requests
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    // Handle OPTIONS preflight requests
    if (req.method === 'OPTIONS') {
      res.status(200).end();
      return;
    }

    const time = new Date().getDate();
    let targetUrl = ""; 
    if(time <15){
        targetUrl = "https://pullratetracker.onrender.com/api/";
    }else{
        targetUrl = "https://pullratetracker-1.onrender.com/api/"
    }
  

  try {
    const Parameters = req.query;
    const endpoint = Parameters.endpoint;
    let url = "";
    if(endpoint === undefined){
      url = `${targetUrl}data`;
    }else{
      delete Parameters.endpoint;
      const queryString = new URLSearchParams(Parameters).toString();
     url = `${targetUrl}${endpoint}?${queryString}`;
    }
    
    const response = await fetch(url, {
      method: req.method,  
      headers: req.headers, 
      body: req.method === 'POST' || req.method === 'PUT' ? req.body : undefined, 
    });
    if(req.method === 'GET'){
    const data = await response.json(); 
    res.status(response.status).json(data); 
    }else if (req.method === 'HEAD') {
      res.setHeader('Vercel-Server', ''); 
      res.status(response.status).end();
    } else {
      res.status(response.status).end();
    }
    console.log('Request forwarded:', req.method, req.url);
  } catch (error) {
    console.error('Error forwarding request:', error);
    res.status(500).json({ error: 'Failed to forward request' });
  }
};
