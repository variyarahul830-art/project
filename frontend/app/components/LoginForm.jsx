'use client';

import { useState } from 'react';
import { useAuth } from '@/app/context/AuthContext';
import styles from './AuthForm.module.css';

export default function LoginForm() {
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || data.message || 'Login failed');
        return;
      }

      // Login with JWT token
      login(
        {
          user_id: data.user_id,
          username: data.user?.username || formData.username,
          email: data.user?.email || ''
        },
        data.token
      );

      // Force full page reload to clear old user's data
      window.location.href = '/';
    } catch (err) {
      setError('Network error. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <h2>Login</h2>

      {error && <div className={styles.error}>{error}</div>}

      <div className={styles.formGroup}>
        <label htmlFor="username">Username or Email</label>
        <input
          type="text"
          id="username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          placeholder="Enter username or email"
          required
          disabled={loading}
        />
      </div>

      <div className={styles.formGroup}>
        <label htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Enter password"
          required
          disabled={loading}
        />
      </div>

      <button type="submit" disabled={loading} className={styles.submitBtn}>
        {loading ? 'Logging in...' : 'Login'}
      </button>

      <p className={styles.toggle}>
        Don't have an account?{' '}
        <a href="/signup">Sign up here</a>
      </p>
    </form>
  );
}
