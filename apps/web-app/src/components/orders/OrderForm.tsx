import React, { useState } from 'react';
import { Button } from '../ui/Button';
import './OrderForm.css';

interface OrderFormProps {
  symbol: string;
  currentPrice: number;
  availableCash: number;
  onSubmit: (order: any) => void;
}

export const OrderForm: React.FC<OrderFormProps> = ({ symbol, currentPrice, availableCash, onSubmit }) => {
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT'>('MARKET');
  const [quantity, setQuantity] = useState<string>('1');
  const [limitPrice, setLimitPrice] = useState<string>(currentPrice.toString());

  const numQuantity = parseInt(quantity) || 0;
  const numLimitPrice = parseFloat(limitPrice) || 0;
  
  const estimatedCost = side === 'BUY' 
    ? numQuantity * (orderType === 'MARKET' ? currentPrice : numLimitPrice)
    : 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (numQuantity <= 0) return;
    
    onSubmit({
      symbol,
      side,
      orderType,
      quantity: numQuantity,
      limitPrice: orderType === 'LIMIT' ? numLimitPrice : undefined,
    });
  };

  return (
    <form className="order-form" onSubmit={handleSubmit}>
      <div className="order-side-toggle">
        <button 
          type="button" 
          className={`side-btn buy ${side === 'BUY' ? 'active' : ''}`}
          onClick={() => setSide('BUY')}
        >
          BUY
        </button>
        <button 
          type="button" 
          className={`side-btn sell ${side === 'SELL' ? 'active' : ''}`}
          onClick={() => setSide('SELL')}
        >
          SELL
        </button>
      </div>

      <div className="form-group">
        <label>Order Type</label>
        <select 
          value={orderType} 
          onChange={(e) => setOrderType(e.target.value as 'MARKET' | 'LIMIT')}
          className="form-input"
        >
          <option value="MARKET">Market</option>
          <option value="LIMIT">Limit</option>
        </select>
      </div>

      <div className="form-group">
        <label>Quantity (Shares)</label>
        <input 
          type="number" 
          min="1" 
          step="1" 
          className="form-input" 
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          required
        />
      </div>

      {orderType === 'LIMIT' && (
        <div className="form-group">
          <label>Limit Price ($)</label>
          <input 
            type="number" 
            min="0.01" 
            step="0.01" 
            className="form-input" 
            value={limitPrice}
            onChange={(e) => setLimitPrice(e.target.value)}
            required
          />
        </div>
      )}

      <div className="order-summary">
        <div className="summary-row">
          <span className="text-secondary">Current Price</span>
          <span className="font-mono">${currentPrice.toFixed(2)}</span>
        </div>
        {side === 'BUY' && (
          <>
            <div className="summary-row">
              <span className="text-secondary">Est. Cost</span>
              <span className="font-mono text-blue">${estimatedCost.toFixed(2)}</span>
            </div>
            <div className="summary-row">
              <span className="text-secondary">Available Cash</span>
              <span className="font-mono">${availableCash.toFixed(2)}</span>
            </div>
          </>
        )}
      </div>

      <Button 
        type="submit" 
        variant={side === 'BUY' ? 'success' : 'danger'} 
        fullWidth 
        size="lg"
        style={{ marginTop: 'var(--space-md)' }}
      >
        {side} {symbol}
      </Button>
    </form>
  );
};
