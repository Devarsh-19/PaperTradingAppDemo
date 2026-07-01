import React from 'react';
import { useAuthStore } from '../../stores/authStore';
import { useWebSocket } from '../../hooks/useWebSocket';
import { Bell, Search, User, Wifi, WifiOff } from 'lucide-react';
import './Header.css';

export const Header: React.FC = () => {
  const { user, logout } = useAuthStore();
  const { isConnected } = useWebSocket();

  return (
    <header className="header">
      <div className="header-search">
        <Search size={18} className="text-secondary" />
        <input type="text" placeholder="Search symbols (e.g. AAPL, TSLA)..." />
      </div>

      <div className="header-actions">
        <div className="portfolio-mini">
          <span className="text-secondary text-sm mr-2">Virtual Cash:</span>
          <span className="font-mono font-bold text-green">
            ${user?.initial_balance?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </span>
        </div>

        <div title={isConnected ? 'Connected to real-time feed' : 'Disconnected'} style={{ display: 'flex', alignItems: 'center' }}>
          {isConnected ? <Wifi size={16} className="text-green" /> : <WifiOff size={16} className="text-red" />}
        </div>

        <button className="icon-btn">
          <Bell size={20} />
        </button>

        <div className="user-menu">
          <div className="avatar">
            <User size={18} />
          </div>
          <span className="username">{user?.username || 'Guest'}</span>
          <button className="logout-btn" onClick={logout}>Logout</button>
        </div>
      </div>
    </header>
  );
};
