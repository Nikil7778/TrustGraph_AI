import React, { useEffect, useState } from 'react';
import { Header } from '../components/layout/Header';
import { Save, Sliders } from 'lucide-react';
import { fetchWeights, saveWeights } from '../services/api';

export const SettingsPage: React.FC = () => {
  const [weights, setWeightsState] = useState<any>({
    organizationWeight: 15.0,
    emailWeight: 15.0,
    phoneWeight: 15.0,
    upiWeight: 20.0,
    websiteWeight: 15.0,
    qrWeight: 10.0,
    logoWeight: 4.0,
    notificationIdWeight: 3.0,
    dateWeight: 3.0
  });

  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    fetchWeights().then(setWeightsState);
  }, []);

  const handleSave = async () => {
    await saveWeights(weights);
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  const fieldLabels: Record<string, string> = {
    upiWeight: 'UPI / VPA Payment Handle Weight',
    phoneWeight: 'Phone Number Weight',
    websiteWeight: 'Website Domain Weight',
    emailWeight: 'Email Address Weight',
    organizationWeight: 'Organization Name Weight',
    qrWeight: 'QR Code Data Payload Weight',
    logoWeight: 'Emblem / Logo Perceptual Hash Weight',
    notificationIdWeight: 'Notification ID Weight',
    dateWeight: 'Publish / Expiry Date Weight'
  };

  return (
    <div className="min-h-screen bg-slate-50/50 pb-12">
      <Header title="Detection Engine Settings" />

      <main className="max-w-4xl mx-auto px-6 pt-8 space-y-6">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900">Fingerprint Matching Weights Configuration</h2>
          <p className="text-sm text-slate-500 font-medium mt-1">
            Adjust field importance multipliers for the 9-characteristic fingerprint matching engine.
          </p>
        </div>

        <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Sliders className="w-5 h-5 text-blue-600" />
              <span>Configurable Characteristic Weights</span>
            </h3>
            <button
              onClick={handleSave}
              className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              <span>{isSaved ? 'Weights Saved!' : 'Save Weights'}</span>
            </button>
          </div>

          <div className="space-y-6">
            {Object.keys(fieldLabels).map(key => (
              <div key={key} className="space-y-2">
                <div className="flex justify-between text-xs font-bold text-slate-800">
                  <span>{fieldLabels[key]}</span>
                  <span className="text-blue-600 font-mono">{weights[key]}%</span>
                </div>
                <input
                  type="range"
                  min={1}
                  max={40}
                  value={weights[key] || 10}
                  onChange={e => setWeightsState({ ...weights, [key]: parseFloat(e.target.value) })}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};
