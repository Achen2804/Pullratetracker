module.exports = async (req, res) => {
    const time = new Date().getDate();
    let targetUrl = ""; 
    if(time <15){
        targetUrl = "https://pullratetracker.onrender.com/api/data";
    }else{
        targetUrl = "https://pullratetracker-1.onrender.com/api/data"
    }
  

  try {
    const response = await fetch(targetUrl, {
      method: req.method,  
      headers: req.headers, 
      body: req.method === 'POST' || req.method === 'PUT' ? req.body : undefined, 
    });
    res.setHeader('Access-Control-Allow-Origin', '*');
    if(req.method === 'GET'){
    const data = await response.json(); 
    res.status(response.status).json(data); 
    }else if (req.method === 'HEAD') {
      res.status(response.status).set(response.headers).end();
    } else {
      res.status(response.status).end();
    }
  } catch (error) {
    console.error('Error forwarding request:', error);
    res.status(500).json({ error: 'Failed to forward request' });
  }
};
