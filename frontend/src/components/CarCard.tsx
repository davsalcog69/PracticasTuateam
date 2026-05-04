import React from 'react';
import type { CarExport } from '../api/cars';

interface CarCardProps {
  car: CarExport;
  onClick: (car: CarExport) => void;
  isFavorite?: boolean;
  onToggleFavorite?: (carId: string) => void;
}

export const CarCard: React.FC<CarCardProps> = ({ car, onClick, isFavorite, onToggleFavorite }) => {
// Use first image or placeholder fallback as requested
  const imageUrl = car.images && car.images.length > 0 
    ? car.images[0] 
    : 'https://via.placeholder.com/400x300?text=No+Image';

  const profit = Math.round(car.estimated_profit || 0);
  const isProfitable = profit > 0;
  const status = car.vehicle_status || 'Gebrauchtfahrzeug';
  const statusCheck = car.vehicle_status_check || 'OK';

  const getStatusColor = (s: string) => {
    switch (s.toLowerCase()) {
      case 'ok': return 'bg-emerald-500 text-white shadow-emerald-200';
      case 'dudoso': return 'bg-amber-500 text-white shadow-amber-200';
      case 'descartado': return 'bg-red-500 text-white shadow-red-200';
      default: return 'bg-emerald-500 text-white shadow-emerald-200';
    }
  };

  return (
    <div 
      onClick={() => onClick(car)}
      className={`premium-card group cursor-pointer flex flex-col h-full overflow-hidden animate-reveal ${
        isFavorite 
        ? 'bg-red-50 border-red-200' 
        : 'bg-white'
      }`}
    >
      {/* Image Container */}
      <div className="car-image-container relative">
        <img 
          src={imageUrl} 
          className="car-image group-hover:scale-110" 
          alt={`${car.brand} ${car.model}`}
          onError={(e) => {
            (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x300?text=No+Image';
          }}
        />
        
        {/* Favorite Button Area - Isolated from card click */}
        <div className="absolute top-4 right-4 z-10 pointer-events-auto">
          <button 
            type="button"
            onClick={(e) => {
              e.stopPropagation(); // Prevent opening the modal
              e.preventDefault();  // Prevent any default behavior
              if (onToggleFavorite) {
                onToggleFavorite(car.id);
              }
            }}
            className={`flex items-center justify-center w-11 h-11 rounded-2xl backdrop-blur-xl border transition-all duration-500 active:scale-75 shadow-lg group/fav ${
              isFavorite 
              ? 'bg-red-500 border-red-600 text-white' 
              : 'bg-white/90 border-white/20 text-slate-400 hover:text-red-500 hover:border-red-200'
            }`}
            aria-label={isFavorite ? "Quitar de favoritos" : "Añadir a favoritos"}
          >
            <svg className="w-5 h-5" fill={isFavorite ? "white" : "none"} stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.364-1.364a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
        </div>

        {/* Profit Badge Overlay */}
        <div className="absolute top-4 left-4 z-10">
          <div className="glass px-3.5 py-2 rounded-2xl border border-white/40 flex flex-col items-start gap-0.5">
            <span className="text-[8px] font-bold text-slate-500 uppercase tracking-widest leading-none">Net ROI</span>
            <span className={`text-sm font-bold tabular-nums leading-none ${isProfitable ? 'text-green-600' : 'text-slate-900'}`}>
              {isProfitable ? '+' : ''}{profit.toLocaleString()}€
            </span>
          </div>
        </div>

        {/* Bottom Image Info */}
        <div className="absolute bottom-4 left-4 z-10">
          <div className="badge-premium bg-slate-900/80 text-white backdrop-blur-md">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            </svg>
            {car.location || car.country}
          </div>
        </div>

        {/* Vehicle Status Badge */}
        <div className="absolute bottom-4 right-4 z-10 max-w-[50%]">
          <div className={`px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase tracking-wider shadow-lg backdrop-blur-md truncate ${getStatusColor(statusCheck)}`} title={status}>
            {statusCheck}
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="p-6 flex flex-col flex-1 gap-4">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">{car.brand}</span>
            <div className="w-1 h-1 rounded-full bg-slate-200" />
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">{car.year}</span>
          </div>
          <h3 className="text-xl font-semibold tracking-tight text-slate-900 group-hover:text-accent-600 transition-colors duration-300">
            {car.model}
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-3 py-4 border-y border-slate-50">
          <div className="flex flex-col gap-0.5">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Kilometraje</span>
            <span className="text-sm font-semibold text-slate-700">{car.mileage.toLocaleString()} km</span>
          </div>
          <div className="flex flex-col gap-0.5 text-right">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Combustible</span>
            <span className="text-sm font-semibold text-slate-700">{car.fuel}</span>
          </div>
        </div>

        <div className="mt-auto flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Inversión</span>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-bold text-slate-900 tracking-tighter">
                {car.price.toLocaleString()}
              </span>
              <span className="text-xs font-bold text-slate-400">€</span>
            </div>
          </div>
          <button className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-slate-900 group-hover:text-white group-hover:border-slate-900 transition-all duration-500 shadow-sm">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};
