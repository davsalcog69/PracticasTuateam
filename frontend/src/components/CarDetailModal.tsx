import React, { useState } from 'react';
import type { CarExport } from '../api/cars';
import { recordVisit } from '../api/cars';

interface CarDetailModalProps {
  car: CarExport | null;
  onClose: () => void;
}

export const CarDetailModal: React.FC<CarDetailModalProps> = ({ car, onClose }) => {
  const [activeTab, setActiveTab] = useState<'specs' | 'costs' | 'analysis'>('specs');
  const [activeImage, setActiveImage] = useState(0);

  if (!car) return null;

  // Final fallback as requested
  const images = car.images && car.images.length > 0 
    ? car.images 
    : ['https://via.placeholder.com/400x300?text=No+Image'];

  return (
    <div className="fixed inset-0 z-[1100] flex items-center justify-center p-0 sm:p-4 md:p-8 lg:p-12 overflow-hidden transition-all duration-500">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-slate-950/80 backdrop-blur-xl transition-opacity animate-in duration-500" 
        onClick={onClose} 
      />
      
      {/* Modal Container */}
      <div className="bg-white w-full max-w-7xl h-full md:h-auto md:max-h-[95vh] md:rounded-[2rem] shadow-2xl relative z-10 flex flex-col overflow-hidden border border-slate-200 animate-in transition-colors duration-300">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 z-50 w-10 h-10 flex items-center justify-center rounded-2xl bg-white/80 backdrop-blur-md border border-slate-200 text-slate-500 hover:text-slate-900 hover:bg-white hover:shadow-md transition-all duration-300"
          aria-label="Cerrar"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Main Content Area (Two Columns) */}
        <div className="flex flex-col lg:flex-row flex-1 overflow-y-auto no-scrollbar">
          
          {/* Left: Media Gallery */}
          <div className="w-full lg:w-[60%] bg-slate-50 relative flex flex-col border-b lg:border-b-0 lg:border-r border-slate-200">
            
            {/* Main Image Viewport */}
            <div className="relative flex-1 flex items-center justify-center overflow-hidden min-h-[350px] lg:min-h-[500px] bg-slate-100">
              {/* Blurred Background Layer */}
              <div 
                className="absolute inset-0 scale-110 blur-3xl opacity-30 pointer-events-none"
                style={{ 
                  backgroundImage: `url(${images[activeImage]})`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center'
                }}
              />
              
              {/* Main Image Layer */}
              <img 
                src={images[activeImage]} 
                className="relative z-10 max-w-full max-h-full object-contain transition-all duration-700"
                alt={`${car.brand} ${car.model}`}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x300?text=No+Image';
                }}
              />

              {/* Navigation Arrows */}
              <div className="absolute inset-x-6 top-1/2 -translate-y-1/2 flex justify-between z-20 pointer-events-none">
                <button 
                  onClick={(e) => { e.stopPropagation(); setActiveImage(prev => (prev > 0 ? prev - 1 : images.length - 1))}}
                  className="p-4 bg-white/20 hover:bg-white/40 backdrop-blur-2xl text-white rounded-2xl transition-all border border-white/20 pointer-events-auto shadow-lg"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <button 
                  onClick={(e) => { e.stopPropagation(); setActiveImage(prev => (prev < images.length - 1 ? prev + 1 : 0))}}
                  className="p-4 bg-white/20 hover:bg-white/40 backdrop-blur-2xl text-white rounded-2xl transition-all border border-white/20 pointer-events-auto shadow-lg"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Gallery Navigation Footer */}
            <div className="p-6 bg-white border-t border-slate-100">
              <div className="flex gap-3 overflow-x-auto no-scrollbar py-1">
                {images.map((img, i) => (
                  <button
                    key={i}
                    onClick={() => setActiveImage(i)}
                    className={`relative flex-shrink-0 w-16 h-12 rounded-lg overflow-hidden border-2 transition-all ${
                      activeImage === i ? 'border-primary-500 scale-105 shadow-md' : 'border-transparent opacity-60 hover:opacity-100'
                    }`}
                  >
                    <img src={img} className="w-full h-full object-cover" alt="" />
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Intelligence Panel */}
          <div className="w-full lg:w-[40%] bg-white flex flex-col transition-colors">
            <div className="p-8 lg:p-10 space-y-8 overflow-y-auto no-scrollbar flex-1">
              {/* Header */}
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded-lg bg-slate-100 text-slate-500 text-[9px] font-bold uppercase tracking-widest border border-slate-200">EXP-{(car.id || '').substring(0,6)}</span>
                  <span className={`px-2 py-0.5 rounded-lg text-[9px] font-bold uppercase tracking-widest border font-semibold italic max-w-full truncate ${
                    (car.vehicle_status_check || '').toLowerCase() === 'ok' 
                    ? 'bg-emerald-50 text-emerald-600 border-emerald-100' 
                    : (car.vehicle_status_check || '').toLowerCase() === 'dudoso'
                    ? 'bg-amber-50 text-amber-600 border-amber-100'
                    : 'bg-emerald-50 text-emerald-600 border-emerald-100'
                  }`} title={car.vehicle_status || 'Gebrauchtfahrzeug'}>
                    {car.vehicle_status || 'Gebrauchtfahrzeug'}
                  </span>
                </div>
                <div>
                  <h2 className="text-3xl font-semibold tracking-tight text-slate-900 leading-tight">
                    <span className="text-slate-400 mr-2">{car.brand}</span>
                    {car.model}
                  </h2>
                  <div className="flex items-center gap-2 mt-2 text-slate-500 font-medium text-xs">
                    <svg className="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    </svg>
                    {car.location || car.country}
                  </div>
                </div>
              </div>

              {/* Price & ROI Overview */}
              <div className="grid grid-cols-2 gap-4 bg-slate-50 p-6 rounded-2xl border border-slate-100 transition-colors">
                <div className="space-y-1">
                  <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">Inversión Net</p>
                  <p className="text-2xl font-bold text-slate-900 tracking-tight tabular-nums">{car.price.toLocaleString()}€</p>
                </div>
                <div className="space-y-1 text-right">
                  <p className="text-[10px] font-semibold text-green-600 uppercase tracking-widest">Margen ROI</p>
                  <p className="text-2xl font-bold text-green-600 tracking-tight tabular-nums">+{Math.round(car.estimated_profit).toLocaleString()}€</p>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex bg-slate-50 border border-slate-200 rounded-xl p-1 transition-colors">
                {(['specs', 'costs', 'analysis'] as const).map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`flex-1 py-2.5 rounded-lg text-[10px] font-semibold uppercase tracking-wider transition-all ${
                      activeTab === tab 
                      ? 'bg-white text-slate-900 shadow-sm' 
                      : 'text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    {tab === 'specs' ? 'Técnico' : tab === 'costs' ? 'Costes' : 'ROI'}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="min-h-[250px]">
                {activeTab === 'specs' && (
                  <div className="grid grid-cols-2 gap-3 animate-in">
                    {[
                      { label: 'Kilometraje', value: `${car.mileage.toLocaleString()} km`, icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
                      { label: 'Año', value: car.year, icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
                      { label: 'Motor', value: car.fuel, icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
                      { label: 'Origen', value: car.portal || 'Europa', icon: 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064' },
                    ].map(spec => (
                      <div key={spec.label} className="bg-slate-50 p-4 rounded-xl border border-slate-100 transition-colors">
                        <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
                           <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={spec.icon} />
                           </svg>
                          {spec.label}
                        </p>
                        <p className="text-sm font-semibold text-slate-800">{spec.value}</p>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'costs' && (
                  <div className="space-y-2 animate-in">
                    {[
                      { label: 'Precio Base (Europa)', value: car.price },
                      { label: 'Importación & Hub', value: 2500 },
                      { label: 'Gestión & IVA (ROI)', value: Math.round(car.price * 0.05) },
                    ].map((cost, idx) => (
                      <div key={idx} className="flex justify-between items-center px-4 py-3 bg-slate-50 rounded-xl transition-colors">
                        <span className="text-xs font-medium text-slate-500">{cost.label}</span>
                        <span className="text-xs font-semibold text-slate-800 tabular-nums">{cost.value.toLocaleString()}€</span>
                      </div>
                    ))}
                    <div className="flex justify-between items-center p-5 bg-slate-900 text-white rounded-xl mt-4 border border-slate-800">
                      <span className="text-[10px] font-semibold uppercase tracking-widest">Inversión Final</span>
                      <span className="text-xl font-bold tracking-tight tabular-nums">{(car.price + 2500 + Math.round(car.price * 0.05)).toLocaleString()}€</span>
                    </div>
                  </div>
                )}

                {activeTab === 'analysis' && (
                  <div className="space-y-4 animate-in">
                    <div className="p-6 rounded-2xl bg-green-500 text-white shadow-lg flex items-center justify-between">
                      <div className="flex flex-col gap-1">
                        <p className="text-[10px] font-semibold text-white/80 uppercase tracking-widest">ROI Est.</p>
                        <div className="flex items-baseline gap-3">
                          <p className="text-4xl font-black tracking-tight">+{Math.round(car.estimated_profit).toLocaleString()}€</p>
                        </div>
                      </div>
                      <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-md">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                        </svg>
                      </div>
                    </div>
                    
                    <div className="p-6 rounded-2xl bg-slate-900 text-white space-y-4 border border-slate-800">
                      <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">Benchmark de Mercado</p>
                      <div className="space-y-3">
                        <div className="flex justify-between text-xs font-medium">
                          <span className="text-slate-400">Media España (ITV incl.)</span>
                          <span className="tabular-nums">{(car.price + car.estimated_profit + 2500).toLocaleString()}€</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden flex text-slate-400">
                          <div className="bg-primary-500 h-full" style={{ width: '40%' }}></div>
                          <div className="bg-green-500 h-full" style={{ width: '25%' }}></div>
                          <div className="bg-slate-700 h-full flex-1"></div>
                        </div>
                        <p className="text-[9px] font-medium text-slate-500 leading-relaxed italic">
                          La unidad presenta un diferencial de mercado positivo superior al 15% tras costes de nacionalización.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Global Footer Actions */}
        <div className="bg-white border-t border-slate-100 p-6 flex justify-center items-center gap-6">
          <a 
            href={car.url || '#'} 
            target="_blank" 
            rel="noopener noreferrer"
            onClick={() => recordVisit(car.id, car.model)}
            className="btn btn-primary min-w-[280px] py-4 text-[11px] uppercase tracking-[0.2em] shadow-xl"
          >
            Ver en Origen
          </a>
          <button 
            onClick={onClose}
            className="btn btn-secondary px-10 text-[11px] uppercase tracking-widest font-bold border-2"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};
