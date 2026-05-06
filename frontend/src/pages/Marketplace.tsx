import React, { useState, useEffect, useMemo } from 'react';
import { CarCard } from '../components/CarCard';
import { CarDetailModal } from '../components/CarDetailModal';
import { fetchCars, type CarExport, fetchFavorites, toggleFavorite, deleteFavorite } from '../api/cars';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../config';

type SortOption = 'profit' | 'recent' | 'mileage';

export const Marketplace: React.FC = () => {
  const { token } = useAuth();
  const [cars, setCars] = useState<CarExport[]>([]);
  const [favoriteIds, setFavoriteIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [selectedCar, setSelectedCar] = useState<CarExport | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Filter & Sort States
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [sortBy, setBySort] = useState<SortOption>('profit');
  const [minPrice, setMinPrice] = useState<number>(0);
  const [maxPrice, setMaxPrice] = useState<number>(100000);
  const [minYear, setMinYear] = useState<number>(2019);
  const [maxYear, setMaxYear] = useState<number>(2026);
  const [minROI, setMinROI] = useState<number>(0);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [carsData, favoritesData] = await Promise.all([
          fetchCars(),
          fetchFavorites()
        ]);
        setCars(carsData.cars);
        setFavoriteIds(new Set(favoritesData.map(car => car.id)));
      } catch (err) {
        setError('Error al conectar con la central de inteligencia. Verifique la conexión con el servidor.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const handleToggleFavorite = async (carId: string) => {
    const isFav = favoriteIds.has(carId);
    setFavoriteIds(prev => {
      const next = new Set(prev);
      if (isFav) next.delete(carId);
      else next.add(carId);
      return next;
    });

    try {
      if (isFav) await deleteFavorite(carId);
      else await toggleFavorite(carId);
    } catch (err) {
      setFavoriteIds(prev => {
        const next = new Set(prev);
        if (isFav) next.add(carId);
        else next.delete(carId);
        return next;
      });
    }
  };

  const filteredAndSortedCars = useMemo(() => {
    let result = [...cars];
    result = result.filter(car => {
      const matchModel = selectedModels.length === 0 || selectedModels.some(m => car.model.toLowerCase().includes(m.toLowerCase()));
      const matchPrice = car.price >= minPrice && car.price <= maxPrice;
      const matchYear = car.year >= minYear && car.year <= maxYear;
      const matchROI = car.estimated_profit >= minROI;
      return matchModel && matchPrice && matchYear && matchROI;
    });

    result.sort((a, b) => {
      if (sortBy === 'profit') return b.estimated_profit - a.estimated_profit;
      if (sortBy === 'mileage') return a.mileage - b.mileage;
      return b.year - a.year || b.estimated_profit - a.estimated_profit;
    });
    return result;
  }, [cars, favoriteIds, selectedModels, sortBy, minPrice, maxPrice, minYear, maxYear, minROI]);

  const handleReset = () => {
    setSelectedModels([]);
    setBySort('profit');
    setMinPrice(0);
    setMaxPrice(100000);
    setMinYear(2019);
    setMaxYear(2026);
    setMinROI(0);
  };

  const handleCarClick = async (car: CarExport) => {
    setSelectedCar(car);
    if (token) {
        try {
            await fetch(`${API_BASE_URL}/user/record-visit/${encodeURIComponent(car.id)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ model_name: car.model })
            });
        } catch (err) {
            console.error('Failed to record visit', err);
        }
    }
  };

  return (
    <main className="max-w-[1600px] mx-auto px-8 py-10 min-h-screen">
      {/* Balanced Header Section */}
      <header className="mb-12 animate-reveal">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-8">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-0.5 rounded-full bg-accent-600" />
              <span className="text-xs font-bold text-accent-600 uppercase tracking-[0.3em]">Live Feed</span>
            </div>
            <h1 className="text-4xl font-bold tracking-tighter text-slate-900 leading-none">
              Explorar <span className="text-slate-400">Oportunidades</span>
            </h1>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="flex flex-col items-end">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">Unidades</span>
              <span className="text-xl font-bold text-slate-900 leading-none">{cars.length}</span>
            </div>
            <div className="h-8 w-px bg-slate-100" />
            <div className="badge-premium bg-green-50 text-green-600 border border-green-100 py-2 px-3 text-xs font-bold uppercase tracking-tight">
              Intelligence Active
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-col lg:flex-row gap-12">
        {/* Optimized Filter Sidebar */}
        <aside className="w-full lg:w-80 shrink-0 animate-reveal" style={{ animationDelay: '0.1s' }}>
          <div className="bg-white rounded-[2.5rem] border border-slate-100/50 p-8 shadow-premium sticky top-28">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-xl font-bold tracking-tight">Filtros</h2>
              <button 
                onClick={handleReset}
                className="text-xs font-bold text-accent-600 uppercase tracking-widest hover:text-accent-700 transition-colors"
              >
                Limpiar
              </button>
            </div>

            <div className="space-y-8">
              {/* Sort Logic - MOVED TO TOP */}
              <div className="space-y-4">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Ordenar por</label>
                <div className="flex bg-slate-50 p-1 rounded-2xl border border-slate-100">
                  <button 
                    onClick={() => setBySort('profit')}
                    className={`flex-1 py-2.5 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-all ${
                      sortBy === 'profit' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    ROI
                  </button>
                  <button 
                    onClick={() => setBySort('recent')}
                    className={`flex-1 py-2.5 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-all ${
                      sortBy === 'recent' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    Año
                  </button>
                  <button 
                    onClick={() => setBySort('mileage')}
                    className={`flex-1 py-2.5 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-all ${
                      sortBy === 'mileage' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    KM
                  </button>
                </div>
              </div>

              {/* Model Selection - Grouped Dropdown */}
              <div className="space-y-4">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Modelo</label>
                <select
                  value={selectedModels[0] || 'all'}
                  onChange={(e) => {
                    const val = e.target.value;
                    setSelectedModels(val === 'all' ? [] : [val]);
                  }}
                  className="w-full px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl text-xs font-bold text-slate-700 focus:bg-white focus:border-accent-200 focus:ring-4 focus:ring-accent-500/5 transition-all outline-none appearance-none cursor-pointer"
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


              {/* Price Range */}
              <div className="space-y-4">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Inversión</label>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-tight ml-1">Mínimo</span>
                    <div className="relative">
                      <input 
                        type="number" 
                        value={minPrice}
                        onChange={(e) => setMinPrice(Number(e.target.value))}
                        className="w-full pl-4 pr-8 py-3 bg-slate-50 border border-slate-100 rounded-xl text-xs font-bold text-slate-700 focus:bg-white focus:border-accent-200 transition-all outline-none"
                      />
                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-[10px]">€</span>
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-tight ml-1">Máximo</span>
                    <div className="relative">
                      <input 
                        type="number" 
                        value={maxPrice}
                        onChange={(e) => setMaxPrice(Number(e.target.value))}
                        className="w-full pl-4 pr-8 py-3 bg-slate-50 border border-slate-100 rounded-xl text-xs font-bold text-slate-700 focus:bg-white focus:border-accent-200 transition-all outline-none"
                      />
                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-[10px]">€</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Year Range */}
              <div className="space-y-4">
                <div className="flex justify-between items-end ml-1">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-widest">Año</label>
                  <span className="text-sm font-bold text-slate-900">{minYear} - {maxYear}</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-tight">Desde</span>
                    <select 
                      value={minYear}
                      onChange={(e) => setMinYear(parseInt(e.target.value))}
                      className="w-full px-3 py-2 bg-slate-50 border border-slate-100 rounded-xl text-xs font-bold"
                    >
                      {[2019, 2020, 2021, 2022, 2023, 2024, 2025].map(y => <option key={y} value={y}>{y}</option>)}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-tight">Hasta</span>
                    <select 
                      value={maxYear}
                      onChange={(e) => setMaxYear(parseInt(e.target.value))}
                      className="w-full px-3 py-2 bg-slate-50 border border-slate-100 rounded-xl text-xs font-bold"
                    >
                      {[2020, 2021, 2022, 2023, 2024, 2025, 2026].map(y => <option key={y} value={y}>{y}</option>)}
                    </select>
                  </div>
                </div>
              </div>

              {/* ROI Filter */}
              <div className="space-y-4">
                <div className="flex justify-between items-end ml-1">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-widest">ROI Mínimo</label>
                  <span className="text-sm font-bold text-green-600">+{minROI.toLocaleString()}€</span>
                </div>
                <input 
                  type="range" min="0" max="20000" step="500" value={minROI}
                  onChange={(e) => setMinROI(parseInt(e.target.value))}
                  className="w-full accent-green-500 h-1.5 bg-slate-100 rounded-full appearance-none cursor-pointer"
                />
              </div>
            </div>
          </div>
        </aside>

        {/* Car Grid Container */}
        <div className="flex-1 space-y-10 animate-reveal" style={{ animationDelay: '0.2s' }}>
          {error && (
            <div className="bg-red-50 border border-red-100 p-8 rounded-[2.5rem] flex items-center gap-5 text-red-600 shadow-sm">
              <div className="p-3 bg-white rounded-2xl shadow-sm text-red-500">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <p className="font-bold text-red-900">Interrupción de Datos</p>
                <p className="text-sm opacity-80">{error}</p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-10">
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="bg-white rounded-[2.5rem] h-[520px] border border-slate-100/50 shadow-premium animate-pulse" />
              ))
            ) : filteredAndSortedCars.length === 0 ? (
              <div className="col-span-full py-40 text-center bg-white rounded-[4rem] border border-dashed border-slate-200">
                <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-8">
                  <svg className="w-12 h-12 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-slate-900">Sin coincidencias</h3>
                <p className="text-slate-400 mt-3 max-w-sm mx-auto font-medium">Ajuste los parámetros de búsqueda para identificar nuevas oportunidades de arbitraje.</p>
              </div>
            ) : (
              filteredAndSortedCars.map((car) => (
                <CarCard 
                  key={car.id} 
                  car={car} 
                  onClick={handleCarClick} 
                  isFavorite={favoriteIds.has(car.id)}
                  onToggleFavorite={handleToggleFavorite}
                />
              ))
            )}
          </div>
        </div>
      </div>

      <CarDetailModal car={selectedCar} onClose={() => setSelectedCar(null)} />
    </main>
  );
};
