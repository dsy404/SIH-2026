"use client";

import React, { useState } from 'react';
import { FieldHabitation } from './HabitationList';

interface VerificationFormProps {
  habitation: FieldHabitation;
  onBack: () => void;
  onSubmit: (id: string, verifiedData: any) => void;
}

export default function VerificationForm({ habitation, onBack, onSubmit }: VerificationFormProps) {
  const [formData, setFormData] = useState({
    elevation: habitation.systemData.elevation,
    slope: habitation.systemData.slope,
    population: habitation.systemData.population,
    households: habitation.systemData.households,
    immediateDanger: false,
    notes: '',
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate network delay
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitted(true);
      
      // Call parent after brief delay to show success state
      setTimeout(() => {
        onSubmit(habitation.id, formData);
      }, 1500);
    }, 1000);
  };

  if (submitted) {
    return (
      <div className="flex flex-col items-center justify-center p-8 h-64 max-w-md mx-auto">
        <div className="w-16 h-16 bg-green-100 text-green-500 rounded-full flex items-center justify-center mb-4 text-3xl">
          ✓
        </div>
        <h2 className="text-xl font-bold text-gray-800">Verification Submitted!</h2>
        <p className="text-gray-500 text-center mt-2">The ground truth data has been synced to the master DSS.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col p-4 pb-24 max-w-md mx-auto w-full">
      <div className="flex items-center mb-6">
        <button 
          onClick={onBack}
          className="mr-3 p-2 rounded-full hover:bg-gray-100 transition-colors"
          aria-label="Go back"
        >
          ←
        </button>
        <div>
          <h2 className="text-xl font-bold text-gray-800">{habitation.name}</h2>
          <p className="text-xs text-gray-500">ID: {habitation.id}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* Data Comparison Section */}
        <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
          <h3 className="text-sm font-bold text-blue-800 uppercase tracking-wide mb-3">Field Validation</h3>
          
          <div className="grid grid-cols-2 gap-4">
            {/* Elevation */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Elevation (m)</label>
              <div className="flex flex-col">
                <span className="text-[10px] text-gray-400 mb-1">System: {habitation.systemData.elevation}</span>
                <input 
                  type="number" 
                  name="elevation"
                  value={formData.elevation}
                  onChange={handleChange}
                  className="w-full p-2 border border-gray-300 rounded text-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Slope */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Slope (°)</label>
              <div className="flex flex-col">
                <span className="text-[10px] text-gray-400 mb-1">System: {habitation.systemData.slope}</span>
                <input 
                  type="number" 
                  name="slope"
                  value={formData.slope}
                  onChange={handleChange}
                  className="w-full p-2 border border-gray-300 rounded text-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Population */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Population</label>
              <div className="flex flex-col">
                <span className="text-[10px] text-gray-400 mb-1">System: {habitation.systemData.population}</span>
                <input 
                  type="number" 
                  name="population"
                  value={formData.population}
                  onChange={handleChange}
                  className="w-full p-2 border border-gray-300 rounded text-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Households */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Households</label>
              <div className="flex flex-col">
                <span className="text-[10px] text-gray-400 mb-1">System: {habitation.systemData.households}</span>
                <input 
                  type="number" 
                  name="households"
                  value={formData.households}
                  onChange={handleChange}
                  className="w-full p-2 border border-gray-300 rounded text-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Status Toggle */}
        <div className="bg-red-50 p-4 rounded-xl border border-red-100 flex items-center justify-between">
          <div>
            <h3 className="font-medium text-red-800">Immediate Danger?</h3>
            <p className="text-xs text-red-600">Flag for emergency evacuation</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="immediateDanger"
              checked={formData.immediateDanger}
              onChange={handleChange}
              className="sr-only peer" 
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
          </label>
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Field Notes / Remarks</label>
          <textarea 
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows={3}
            className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500"
            placeholder="Add observations about infrastructure, access roads..."
          ></textarea>
        </div>

        {/* Photo Upload Mockup */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Evidence (Photos)</label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center justify-center text-gray-500 hover:bg-gray-50 transition-colors cursor-pointer">
            <span className="text-2xl mb-2">📷</span>
            <span className="text-sm font-medium">Tap to take photo</span>
          </div>
        </div>

        {/* Submit Button */}
        <button 
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-blue-600 text-white font-bold py-4 rounded-xl shadow-lg hover:bg-blue-700 transition-colors active:scale-95 disabled:bg-blue-400 flex justify-center items-center"
        >
          {isSubmitting ? (
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
          ) : (
            "Submit Verification"
          )}
        </button>

      </form>
    </div>
  );
}
