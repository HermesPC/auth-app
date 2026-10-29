import { useContext, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { API } from '../api';

const PHONE_REGEX = /^[\d\s\-\(\)\+\.]+$/;
const ZIPCODE_REGEX = /^\d{5}(-\d{4})?$/;
const FIELDS = ['firstName', 'lastName', 'phone', 'addressLine1', 'addressLine2', 'city', 'state', 'zipCode'];

export default function ProfileEditForm({ onSave, onCancel, initial }) {
  const { logout } = useContext(AuthContext);
  const [form, setForm] = useState(() => {
    const s = {};
    FIELDS.forEach((f) => { s[f] = initial?.[f] || ''; });
    return s;
  });
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [serverError, setServerError] = useState('');

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: '' }));
  };

  const validate = () => {
    const errs = {};
    if (form.phone && !PHONE_REGEX.test(form.phone)) {
      errs.phone = 'Phone may only contain digits, spaces, hyphens, parentheses, plus signs, or dots';
    }
    if (form.zipCode && !ZIPCODE_REGEX.test(form.zipCode)) {
      errs.zipCode = 'Zip code must be 5 digits or 5-digit+4 format (e.g., 97477 or 97477-1234)';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setServerError('');
    setSaving(true);
    try {
      const payload = {};
      FIELDS.forEach((f) => { if (form[f]) payload[f] = form[f]; });
      await API.put('/profile', payload);
      onSave();
    } catch (err) {
      setServerError(err.response?.data?.error || 'Failed to save profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-6">
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Edit Profile</h2>

        {serverError && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg mb-4 text-sm" role="alert">
            {serverError}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {FIELDS.map((field) => (
            <div key={field}>
              <label htmlFor={field} className="block text-sm font-medium text-gray-700 mb-1 capitalize">
                {field.replace(/([A-Z])/g, ' $1').trim()}
              </label>
              <input
                id={field}
                type="text"
                value={form[field]}
                onChange={(e) => handleChange(field, e.target.value)}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${errors[field] ? 'border-red-400 bg-red-50' : 'border-gray-300'}`}
                placeholder={field.replace(/([A-Z])/g, ' $1').trim()}
              />
              {errors[field] && (
                <p className="text-red-600 text-xs mt-1">{errors[field]}</p>
              )}
            </div>
          ))}
        </div>

        <div className="flex justify-end gap-3 mt-6 pt-4 border-t">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );
}
