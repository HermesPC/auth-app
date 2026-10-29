import { useContext, useState, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { API } from '../api';
import ProfileEditForm from './ProfileEditForm';
import { useNavigate } from 'react-router-dom';

const FIELDS = [
  'firstName', 'lastName', 'phone', 'addressLine1', 'addressLine2',
  'city', 'state', 'zipCode'
];

const FIELD_LABELS = {
  firstName: 'First Name',
  lastName: 'Last Name',
  phone: 'Phone',
  addressLine1: 'Address Line 1',
  addressLine2: 'Address Line 2',
  city: 'City',
  state: 'State',
  zipCode: 'Zip Code'
};

export default function DashboardView() {
  const { user, logout } = useContext(AuthContext);
  const [profile, setProfile] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await API.get('/profile');
        setProfile(res.data);
      } catch {
        setProfile(null);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleSave = () => {
    setEditMode(false);
    API.get('/profile').then((res) => setProfile(res.data));
  };

  const handleCancel = () => {
    setEditMode(false);
  };

  if (loading) return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  if (!profile) return <div className="flex items-center justify-center min-h-screen text-gray-500">No profile found.</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-indigo-700">Dashboard</h1>
        <div className="flex items-center gap-4">
          <span className="text-gray-600 text-sm">{user?.email}</span>
          <button
            onClick={() => { logout(); navigate('/'); }}
            className="px-4 py-1.5 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition text-sm font-medium"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="p-6">
        {editMode ? (
          <ProfileEditForm
            initial={profile.contact || profile}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        ) : (
          <div className="max-w-2xl mx-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-800">My Profile</h2>
              <button
                onClick={() => setEditMode(true)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-semibold"
              >
                Edit Profile
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {FIELDS.map((field) => {
                  const value = profile.contact?.[field] ?? profile[field] ?? '';
                  return (
                    <div key={field}>
                      <dt className="text-sm font-medium text-gray-500">{FIELD_LABELS[field]}</dt>
                      <dd className="mt-1 text-lg text-gray-800">{value || <span className="text-gray-300 italic">Not set</span>}</dd>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
