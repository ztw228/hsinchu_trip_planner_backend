const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hsinchu Trip Planner API is running!');
});

const port = process.env.PORT || 8080;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});