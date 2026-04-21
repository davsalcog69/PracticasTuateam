import React from 'react';

interface FilterSidebarProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
  maxPrice: number;
  onPriceChange: (price: number) => void;
  minYear: number;
  onYearChange: (year: number) => void;
  maxMileage: number;
  onMileageChange: (mileage: number) => void;
  minROI: number;
  onROIChange: (roi: number) => void;
  onReset: () => void;
}

export const FilterSidebar: React.FC<FilterSidebarProps> = ({ 
  selectedModel, 
  onModelChange, 
  maxPrice,
  onPriceChange,
  minYear,
  onYearChange,
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
            <option value="Vito">Mercedes-Benz Vito</option>
            <option value="Sprinter">Mercedes-Benz Sprinter</option>
            <option value="Citan">Mercedes-Benz Citan</option>
          </select>
        </div>

        {/* Max Price Filter */}
        <div className="space-y-3">
          <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Inversión Máxima</label>
          <div className="relative">
            <input 
              type="number" 
              value={maxPrice}
              onChange={(e) => onPriceChange(Number(e.target.value))}
              placeholder="50000" 
              className="input-field pr-10" 
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-xs pointer-events-none">€</span>
          </div>
        </div>

        {/* Min Year Filter - Restricted to 2023-2026 */}
        <div className="space-y-3">
          <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Año Mínimo</label>
          <select 
            className="input-field"
            value={minYear}
            onChange={(e) => onYearChange(Number(e.target.value))}
          >
            <option value="2023">2023+</option>
            <option value="2024">2024+</option>
            <option value="2025">2025+</option>
            <option value="2026">2026+</option>
          </select>
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
