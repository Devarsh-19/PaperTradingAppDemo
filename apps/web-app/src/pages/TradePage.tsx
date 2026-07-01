import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { CandlestickChart } from '../components/charts/CandlestickChart';
import { OrderForm } from '../components/orders/OrderForm';
import { useAuthStore } from '../stores/authStore';
import { marketApi } from '../api/market';
import { ordersApi } from '../api/orders';
import { Order } from '../types/api';
import { Badge } from '../components/ui/Badge';
import { useWebSocket } from '../hooks/useWebSocket';

export const TradePage: React.FC = () => {
  const { user } = useAuthStore();
  const [symbol, setSymbol] = useState('AAPL');
  const [currentPrice, setCurrentPrice] = useState(171.50);
  const [chartData, setChartData] = useState<any[]>([]);
  const [openOrders, setOpenOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  
  const { isConnected, subscribe, subscribeToSymbols, unsubscribeFromSymbols } = useWebSocket();

  const fetchChartData = async (sym: string) => {
    try {
      const data = await marketApi.getHistory(sym, '1mo', '1d');
      if (data && data.history) {
        setChartData(data.history);
      }
    } catch (e) {
      console.error("Failed to fetch chart", e);
    }
  };

  const fetchOpenOrders = async () => {
    try {
      const data = await ordersApi.getAll(1, 50, 'OPEN');
      setOpenOrders(data.items || data);
    } catch (e) {
      console.error("Failed to fetch open orders", e);
    }
  };

  const fetchPrice = async (sym: string) => {
    try {
      const quote = await marketApi.getQuote(sym);
      setCurrentPrice(quote.price);
    } catch (e) {
      console.error("Failed to fetch price", e);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchChartData(symbol);
    fetchOpenOrders();
    fetchPrice(symbol);
    setLoading(false);
  }, [symbol]);

  useEffect(() => {
    if (isConnected) {
      subscribeToSymbols([symbol]);
    }
    return () => {
      if (isConnected) {
        unsubscribeFromSymbols([symbol]);
      }
    };
  }, [symbol, isConnected, subscribeToSymbols, unsubscribeFromSymbols]);

  useEffect(() => {
    const unsubscribePrice = subscribe('price_update', (data) => {
      if (data && data[symbol]) {
        setCurrentPrice(data[symbol].price);
      }
    });

    const unsubscribeOrder = subscribe('order_update', (data) => {
      // Refresh orders when an order update happens
      fetchOpenOrders();
    });

    return () => {
      unsubscribePrice();
      unsubscribeOrder();
    };
  }, [symbol, subscribe]);

  const handleOrderSubmit = async (orderData: any) => {
    try {
      await ordersApi.create({
        symbol: orderData.symbol,
        order_type: orderData.orderType,
        side: orderData.side,
        quantity: orderData.quantity,
        limit_price: orderData.limitPrice,
        stop_price: orderData.stopPrice
      });
      alert(`Order submitted successfully`);
      fetchOpenOrders();
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Order submission failed');
    }
  };

  return (
    <div className="page-container" style={{ padding: '0 var(--space-xl)' }}>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 'var(--space-md)', height: 'calc(100vh - var(--header-height) - 40px)', paddingTop: 'var(--space-md)' }}>
        
        {/* ── Left Column: Chart ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <Card noPadding style={{ flex: 1, overflow: 'hidden' }}>
            <div style={{ padding: 'var(--space-md)', display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-primary)' }}>
              <input 
                type="text" 
                value={symbol} 
                onChange={e => setSymbol(e.target.value.toUpperCase())}
                className="input-field" 
                style={{ width: '120px', padding: '0.5rem' }} 
                placeholder="Symbol"
              />
              <div style={{ padding: '0.5rem', fontWeight: 700, fontSize: '1.2rem', color: 'var(--accent-blue)' }}>
                ${currentPrice.toFixed(2)}
              </div>
            </div>
            {chartData.length > 0 ? (
              <CandlestickChart data={chartData} symbol={symbol} />
            ) : (
              <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                {loading ? 'Loading chart...' : 'No chart data available'}
              </div>
            )}
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
          
          <Card title="Open Orders" style={{ flex: 1, overflowY: 'auto' }}>
            {openOrders.length === 0 ? (
              <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                No open orders
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {openOrders.map(order => (
                  <div key={order.id} style={{ padding: '8px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', fontSize: '0.875rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 600 }}>{order.symbol}</span>
                      <span className={order.side === 'BUY' ? 'text-green' : 'text-red'}>{order.side}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                      <span>{order.quantity} @ {order.order_type === 'MARKET' ? 'MKT' : `$${order.limit_price || order.stop_price}`}</span>
                      <Badge variant="warning">OPEN</Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

      </div>
    </div>
  );
};
