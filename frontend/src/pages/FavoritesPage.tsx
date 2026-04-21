import React, { useState, useEffect } from 'react';
import { CarCard } from '../components/CarCard';
import { CarDetailModal } from '../components/CarDetailModal';
import { CardSkeleton } from '../components/ui/Skeleton';
import { fetchFavorites, type CarExport, deleteFavorite } from '../api/cars';
import { Heart } from 'lucide-react';

export const FavoritesPage: React.FC = () => {
  const [cars, setCars] = useState<CarExport[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCar, setSelectedCar] = useState<CarExport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadFavorites = async () => {
    try {
      setLoading(true);
      const data = await fetchFavorites();
      setCars(data);
    } catch (err) {
      setError('Error al cargar tus favoritos.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFavorites();
  }, []);

  const handleToggleFavorite = async (carId: string) => {
    try {
      await deleteFavorite(carId);
      // Immediately remove from UI in the favorites page
      setCars(prev => prev.filter(c => c.id !== carId));
    } catch (err) {
      console.error('Failed to remove favorite', err);
    }
  };

  return (
    <main className="max-w-[1600px] mx-auto px-8 py-10">
      <header className="mb-10 bg-white p-8 rounded-[2rem] border border-slate-100 shadow-soft">
        <div className="flex items-center gap-4 mb-2">
            <div className="p-2 bg-accent-50 text-accent-600 rounded-lg">
                <Heart className="w-5 h-5 fill-current" />
            </div>
            <h1 className="text-4xl font-semibold tracking-tight text-slate-900">
                Mis Favoritos
            </h1>
        </div>
        <p className="text-slate-500 text-sm font-medium">
            Gestiona los vehículos que has guardado para analizar más tarde.
        </p>
      </header>

      {error && (
        <div className="bg-accent-50 border-l-4 border-accent-600 p-6 rounded-2xl mb-8">
            <p className="text-sm text-accent-700">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
          {Array.from({ length: 3 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : cars.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
          {cars.map((car) => (
            <CarCard 
              key={car.id} 
              car={car} 
              isFavorite={true}
              onToggleFavorite={handleToggleFavorite}
              onClick={setSelectedCar} 
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-32 bg-white rounded-[3rem] border border-dashed border-slate-200">
          <div className="bg-slate-50 w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-6">
            <Heart className="w-10 h-10 text-slate-200" />
          </div>
          <h3 className="text-xl font-semibold text-slate-900">Aún no tienes favoritos</h3>
          <p className="text-slate-400 mt-2">Explora el marketplace y guarda los coches que te interesen.</p>
        </div>
      )}

      <CarDetailModal 
        car={selectedCar} 
        onClose={() => setSelectedCar(null)} 
      />
    </main>
  );
};
