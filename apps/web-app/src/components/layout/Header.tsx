import React from 'react';
import { useAuthStore } from '../../stores/authStore';
import { Bell, Search, User } from 'lucide-react';
import './Header.css';

export const Header: React.FC = () => {
  const { user, logout } = useAuthStore();

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
