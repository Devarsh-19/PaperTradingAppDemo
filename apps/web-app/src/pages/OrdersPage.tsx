import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';

export const OrdersPage: React.FC = () => {
  const [loading, setLoading] = useState(true);

  // Mock data
  const mockOrders = [
    { id: '1', symbol: 'AAPL', type: 'MARKET', side: 'BUY', qty: 10, status: 'FILLED', date: '2023-10-15 10:30', price: 171.50 },
    { id: '2', symbol: 'TSLA', type: 'LIMIT', side: 'SELL', qty: 5, status: 'OPEN', date: '2023-10-15 11:45', limit: 250.00 },
    { id: '3', symbol: 'MSFT', type: 'MARKET', side: 'BUY', qty: 20, status: 'FILLED', date: '2023-10-14 15:20', price: 330.00 },
    { id: '4', symbol: 'GOOGL', type: 'LIMIT', side: 'BUY', qty: 15, status: 'CANCELLED', date: '2023-10-13 09:15', limit: 125.00 },
  ];

  useEffect(() => {
    setTimeout(() => setLoading(false), 300);
  }, []);

  if (loading) {
    return <div className="page-container"><div className="skeleton" style={{ height: '400px' }} /></div>;
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'FILLED': return <Badge variant="success">Filled</Badge>;
      case 'OPEN': return <Badge variant="warning">Open</Badge>;
      case 'CANCELLED': return <Badge variant="default">Cancelled</Badge>;
      default: return <Badge>{status}</Badge>;
    }
  };

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <div>
          <h1 className="page-title" style={{ marginBottom: 'var(--space-xs)' }}>Orders</h1>
          <p className="text-secondary">View and manage your open and historical orders.</p>
        </div>
      </div>

      <Card noPadding>
        <table className="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Symbol</th>
              <th>Type</th>
              <th>Side</th>
              <th className="text-right">Qty</th>
              <th className="text-right">Price/Limit</th>
              <th className="text-right">Status</th>
              <th className="text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {mockOrders.map((order) => (
              <tr key={order.id}>
                <td className="text-muted text-sm">{order.date}</td>
                <td style={{ fontWeight: 600 }}>{order.symbol}</td>
                <td>{order.type}</td>
                <td className={order.side === 'BUY' ? 'text-green' : 'text-red'}>{order.side}</td>
                <td className="text-right font-mono">{order.qty}</td>
                <td className="text-right font-mono">
                  ${(order.price || order.limit)?.toFixed(2)}
                </td>
                <td className="text-right">{getStatusBadge(order.status)}</td>
                <td className="text-right">
                  {order.status === 'OPEN' && (
                    <button className="text-red" style={{ background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '0.8rem' }}>
                      Cancel
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
};
