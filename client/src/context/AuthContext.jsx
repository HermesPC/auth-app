import { createContext, useState, useEffect, useCallback } from 'react';
import { API } from '../api';
import { useNavigate } from 'react-router-dom';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchProfile = useCallback(async (token) => {
    try {
      const res = await API.get('/profile', { headers: { Authorization: `Bearer ${token}` } });
      setUser({ email: res.data.email, ...res.data.contact });
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchProfile(token).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [fetchProfile]);

  const login = async (email, password) => {
    const res = await API.post('/auth/login', { email, password });
    localStorage.setItem('token', res.data.token);
    await fetchProfile(res.data.token);
    navigate('/dashboard');
    return res.data;
  };

  const signup = async (email, password) => {
    const res = await API.post('/auth/signup', { email, password });
    localStorage.setItem('token', res.data.token);
    await fetchProfile(res.data.token);
    navigate('/dashboard');
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    navigate('/');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
