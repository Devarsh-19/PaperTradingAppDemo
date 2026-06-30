import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { CandlestickChart } from '../components/charts/CandlestickChart';
import { OrderForm } from '../components/orders/OrderForm';
import { useAuthStore } from '../stores/authStore';

// Mock candlestick data
const mockData = [
  { time: '2023-10-01', open: 150, high: 155, low: 148, close: 152 },
  { time: '2023-10-02', open: 152, high: 156, low: 151, close: 155 },
  { time: '2023-10-03', open: 155, high: 160, low: 153, close: 158 },
  { time: '2023-10-04', open: 158, high: 159, low: 150, close: 151 },
  { time: '2023-10-05', open: 151, high: 154, low: 149, close: 153 },
  { time: '2023-10-06', open: 153, high: 158, low: 152, close: 157 },
  { time: '2023-10-07', open: 157, high: 162, low: 155, close: 160 },
  { time: '2023-10-08', open: 160, high: 161, low: 158, close: 159 },
  { time: '2023-10-09', open: 159, high: 165, low: 158, close: 164 },
  { time: '2023-10-10', open: 164, high: 168, low: 162, close: 167 },
  { time: '2023-10-11', open: 167, high: 170, low: 165, close: 169 },
  { time: '2023-10-12', open: 169, high: 175, low: 168, close: 174 },
  { time: '2023-10-13', open: 174, high: 176, low: 170, close: 171 },
];

export const TradePage: React.FC = () => {
  const { user } = useAuthStore();
  const [symbol, setSymbol] = useState('AAPL');
  const [currentPrice, setCurrentPrice] = useState(171.50);

  const handleOrderSubmit = (order: any) => {
    console.log("Order submitted:", order);
    // In a real app, dispatch to orderApi
    alert(`Order submitted: ${order.side} ${order.quantity} ${order.symbol} @ ${order.orderType}`);
  };

  return (
    <div className="page-container" style={{ padding: '0 var(--space-xl)' }}>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 'var(--space-md)', height: 'calc(100vh - var(--header-height) - 40px)', paddingTop: 'var(--space-md)' }}>
        
        {/* ── Left Column: Chart ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <Card noPadding style={{ flex: 1, overflow: 'hidden' }}>
            <CandlestickChart data={mockData} symbol={symbol} />
          </Card>
          
          <Card style={{ height: '200px' }} title="Market Depth (Level 2)">
            <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
              [Order Book Placeholder]
            </div>
          </Card>
        </div>

        {/* ── Right Column: Order Entry ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <Card title="Order Entry">
            <OrderForm 
              symbol={symbol}
              currentPrice={currentPrice}
              availableCash={user?.initial_balance || 0}
              onSubmit={handleOrderSubmit}
            />
          </Card>
          
          <Card title="Open Orders" style={{ flex: 1 }}>
            <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
              No open orders
            </div>
          </Card>
        </div>

      </div>
    </div>
  );
};
