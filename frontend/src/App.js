import React, { useEffect, useState } from 'react';
import axios from 'axios';

const App = () => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await axios.get(`http://${process.env.REACT_APP_FASTAPI_IP}:${process.env.REACT_APP_FASTAPI_PORT}/stocks`, {
          headers: {
            Authorization: process.env.REACT_APP_FASTAPI_TOKEN,
          },
        });

        const stockData = response.data.stock_data;
        const processedStocks = Object.values(stockData).map(stock => ({
          symbol: stock.symbol,
          latest_price: stock.price,
          percentage_change: stock.percentageChange,
          status: stock.down ? 'down' : 'up',
        }));
        setStocks(processedStocks);
      } catch (err) {
        setError('Failed to fetch stock data.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStocks();
  }, []);

  if (loading) return <h1>Loading...</h1>;
  if (error) return <h1 style={{ color: 'red' }}>{error}</h1>;

  return (
    <div className="container">
    <div className="stocks">
      {stocks.map((stock, index) => (
        <div
          key={index}
          className={`stock-card ${stock.status === "down" ? "down" : "up"}`}
        >
          <p className="symbol">{stock.symbol}</p>
          <p className="status">
            {stock.status === "down" ? "Down" : "Up"} by {stock.percentage_change}%
          </p>
          <p className="price">${stock.latest_price.toFixed(2)}</p>
        </div>
      ))}
    </div>
  </div>
);
};

export default App;
