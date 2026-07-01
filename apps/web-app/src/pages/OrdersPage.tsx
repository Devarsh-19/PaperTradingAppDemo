import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { ordersApi } from '../api/orders';
import { Order } from '../types/api';

export const OrdersPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const data = await ordersApi.getAll();
      setOrders(data.items || data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleCancelOrder = async (orderId: string) => {
    try {
      await ordersApi.cancel(orderId);
      // Refresh list
      fetchOrders();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel order');
    }
  };

  if (loading && orders.length === 0) {
    return <div className="page-container"><div className="skeleton" style={{ height: '400px' }} /></div>;
  }

  if (error) {
    return <div className="page-container text-red">{error}</div>;
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
            {orders.length === 0 ? (
              <tr>
                <td colSpan={8} className="text-center text-muted" style={{ padding: 'var(--space-lg)' }}>
                  No orders found
                </td>
              </tr>
            ) : (
              orders.map((order) => (
                <tr key={order.id}>
                  <td className="text-muted text-sm">{new Date(order.created_at).toLocaleString()}</td>
                  <td style={{ fontWeight: 600 }}>{order.symbol}</td>
                  <td>{order.order_type}</td>
                  <td className={order.side === 'BUY' ? 'text-green' : 'text-red'}>{order.side}</td>
                  <td className="text-right font-mono">{order.quantity}</td>
                  <td className="text-right font-mono">
                    ${(order.average_fill_price || order.limit_price || order.stop_price || 0)?.toFixed(2)}
                  </td>
                  <td className="text-right">{getStatusBadge(order.status)}</td>
                  <td className="text-right">
                    {order.status === 'OPEN' && (
                      <button 
                        className="text-red" 
                        style={{ background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '0.8rem' }}
                        onClick={() => handleCancelOrder(order.id)}
                      >
                        Cancel
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </Card>
    </div>
  );
};
