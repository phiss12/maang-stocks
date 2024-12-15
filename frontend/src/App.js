import React, { useEffect, useState } from 'react';
import axios from 'axios';

const App = () => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await axios.get(`https://${process.env.REACT_APP_FASTAPI_IP}/stocks`, {
          headers: {
            Authorization: process.env.REACT_APP_FASTAPI_TOKEN,
          },
        });

        const db = response.data.stock_data;
        const collections = ["meta", "amazon", "apple", "netflix", "google"];

        const stockData = {};
        for (const name of collections) {
          const collection = db.collection(name);
          const documents = await collection
            .find({}, { projection: { _id: 0, symbol: 1, price: 1, percentageChange: 1 } })
            .toArray();

          if (documents.length > 0) {
            const doc = documents[0];
            stockData[name] = {
              symbol: doc.symbol,
              price: doc.price,
              percentageChange: Math.abs(doc.percentageChange),
              down: doc.percentageChange < 0,
            };
          }
        }

        setStocks(Object.values(stockData));
        await client.close();
      } catch (err) {
        setError("Failed to fetch stock data.");
        console.error(err);
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
