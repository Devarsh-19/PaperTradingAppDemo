import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Activity } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuthStore();
  
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await register({
        email,
        username,
        full_name: fullName,
        password
      });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to register account');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-layout">
      <div className="auth-left">
        <div style={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 80, height: 80, borderRadius: '24px', background: 'var(--bg-card)', border: '1px solid var(--border-primary)', marginBottom: 'var(--space-lg)' }}>
            <Activity size={40} className="text-blue" />
          </div>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: 'var(--space-md)' }}>Paper Trading</h2>
          <p className="text-secondary" style={{ fontSize: '1.1rem', maxWidth: 400, margin: '0 auto' }}>
            Start practicing your trading strategies with our advanced paper trading platform.
          </p>
        </div>
      </div>
      
      <div className="auth-right">
        <div className="auth-form-container glass-card" style={{ padding: 'var(--space-xl)' }}>
          <h1>Create Account</h1>
          <p className="subtitle">Sign up to get started</p>
          
          <form className="auth-form" onSubmit={handleSubmit}>
            {error && (
              <div style={{ padding: '0.75rem', background: 'var(--accent-red-dim)', border: '1px solid rgba(255,82,82,0.3)', borderRadius: 'var(--radius-md)', color: 'var(--accent-red)', fontSize: '0.875rem', marginBottom: 'var(--space-sm)' }}>
                {error}
              </div>
            )}
            
            <Input
              label="Email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            
            <Input
              label="Username"
              type="text"
              placeholder="johndoe123"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            
            <Input
              label="Full Name (Optional)"
              type="text"
              placeholder="John Doe"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
            
            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
            
            <div style={{ marginTop: 'var(--space-md)' }}>
              <Button type="submit" fullWidth isLoading={isLoading}>
                Sign Up
              </Button>
            </div>
          </form>
          
          <div className="auth-footer">
            Already have an account? <Link to="/login">Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  );
};
