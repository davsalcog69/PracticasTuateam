import React from 'react';

interface FilterSidebarProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
  minPrice: number;
  onMinPriceChange: (price: number) => void;
  maxPrice: number;
  onPriceChange: (price: number) => void;
  minYear: number;
  onYearChange: (year: number) => void;
  maxYear: number;
  onMaxYearChange: (year: number) => void;
  maxMileage: number;
  onMileageChange: (mileage: number) => void;
  minROI: number;
  onROIChange: (roi: number) => void;
  onReset: () => void;
}

export const FilterSidebar: React.FC<FilterSidebarProps> = ({ 
  selectedModel, 
  onModelChange, 
  minPrice,
  onMinPriceChange,
  maxPrice,
  onPriceChange,
  minYear,
  onYearChange,
  maxYear,
  onMaxYearChange,
  maxMileage,
  onMileageChange,
  minROI,
  onROIChange,
  onReset 
}) => {
  return (
    <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-soft h-fit animate-in space-y-8 transition-colors duration-300">
      <div>
        <h2 className="text-xl font-semibold text-slate-900 tracking-tight mb-1">Filtros Inteligentes</h2>
        <p className="text-xs text-slate-400 font-medium">Refina tu búsqueda estratégica</p>
      </div>

      <div className="space-y-6">
        {/* Model Filter */}
        <div className="space-y-3">
          <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Modelo de Vehículo</label>
          <select 
            className="input-field"
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
          >
            <option value="all">Todos los modelos</option>
            <optgroup label="Mercedes-Benz">
              <option value="Vito">Vito</option>
              <option value="Sprinter">Sprinter</option>
              <option value="Citan">Citan</option>
            </optgroup>
            <optgroup label="BMW">
              <option value="Serie 3">Serie 3</option>
            </optgroup>
            <optgroup label="Audi">
              <option value="A4">A4</option>
            </optgroup>
            <optgroup label="Volkswagen">
              <option value="Golf GTI">Golf GTI</option>
              <option value="Golf R">Golf R</option>
            </optgroup>
          </select>
        </div>


        {/* Price Range Filter */}
        <div className="space-y-3">
          <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Rango de Inversión</label>
          <div className="grid grid-cols-2 gap-3">
            <div className="relative">
              <input 
                type="number" 
                value={minPrice}
                onChange={(e) => onMinPriceChange(Number(e.target.value))}
                placeholder="Mín" 
                className="input-field pr-8 text-[10px]" 
              />
              <span className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-[10px] pointer-events-none">€</span>
            </div>
            <div className="relative">
              <input 
                type="number" 
                value={maxPrice}
                onChange={(e) => onPriceChange(Number(e.target.value))}
                placeholder="Máx" 
                className="input-field pr-8 text-[10px]" 
              />
              <span className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-[10px] pointer-events-none">€</span>
            </div>
          </div>
        </div>

        {/* Year Range Filter */}
        <div className="space-y-3">
          <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Rango de Año</label>
          <div className="grid grid-cols-2 gap-3">
            <select 
              className="input-field text-[10px]"
              value={minYear}
              onChange={(e) => onYearChange(Number(e.target.value))}
            >
              {[2019, 2020, 2021, 2022, 2023, 2024, 2025].map(y => <option key={y} value={y}>{y}+</option>)}
            </select>
            <select 
              className="input-field text-[10px]"
              value={maxYear}
              onChange={(e) => onMaxYearChange(Number(e.target.value))}
            >
              {[2020, 2021, 2022, 2023, 2024, 2025, 2026].map(y => <option key={y} value={y}>Hasta {y}</option>)}
            </select>
          </div>
        </div>

        {/* Max Mileage Filter */}
        <div className="space-y-3">
          <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Kilometraje Máx.</label>
          <div className="relative">
            <input 
              type="number" 
              value={maxMileage}
              onChange={(e) => onMileageChange(Number(e.target.value))}
              placeholder="100000" 
              className="input-field pr-12" 
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-[10px] pointer-events-none">KM</span>
          </div>
        </div>

        {/* Min ROI Filter Controls */}
        <div className="space-y-3">
          <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Margen ROI Mínimo</label>
          <div className="flex bg-slate-50 p-1 rounded-xl border border-slate-100 transition-colors">
            {[0, 1000, 3000, 5000].map((roi) => (
              <button 
                key={roi}
                onClick={() => onROIChange(roi)}
                className={`flex-1 py-2 text-[10px] font-bold transition-all rounded-lg ${
                  minROI === roi 
                  ? 'bg-white text-slate-900 shadow-sm border border-slate-100' 
                  : 'text-slate-400 hover:text-slate-600'
                }`}
              >
                {roi === 0 ? 'Mín' : `${roi / 1000}K€`}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="pt-6 border-t border-slate-100">
        <button 
          onClick={onReset}
          className="btn btn-primary w-full py-4 text-[10px] uppercase tracking-[0.2em]"
        >
          Reiniciar Análisis
        </button>
      </div>

      <div className="p-4 bg-primary-50 rounded-2xl border border-primary-100">
        <p className="text-[10px] font-semibold text-primary-700 leading-relaxed">
          <span className="font-bold">Info:</span> Los cálculos de ROI incluyen transporte, ITV y gestión de matriculación estimada en España.
        </p>
      </div>
    </div>
  );
};
