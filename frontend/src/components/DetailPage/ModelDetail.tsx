import React, { useState, useEffect } from 'react';
import InspectionForm from '../InspectionForm/InspectionForm';
import type { ProfitableOpportunity } from '../../types';
import './DetailPage.css';
import AdCard from './AdCard';

interface ModelDetailProps {
  brand: string;
  model: string;
}

const ModelDetail: React.FC<ModelDetailProps> = ({ brand, model }) => {
  const [opportunities, setOpportunities] = useState<ProfitableOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAd, setSelectedAd] = useState<ProfitableOpportunity | null>(null);

  useEffect(() => {
    const fetchOpportunities = async () => {
      try {
        const response = await fetch('/api/profitable-cars');
        const data: ProfitableOpportunity[] = await response.json();
        // Filter by the selected brand and model
        const filtered = data.filter(
          item => item.brand.toLowerCase() === brand.toLowerCase() &&
            item.model.toLowerCase() === model.toLowerCase()
        );
        setOpportunities(filtered);
      } catch (error) {
        console.error("Error fetching opportunities:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchOpportunities();
  }, [brand, model]);

  if (loading) return <div className="loading">Cargando anuncios rentables...</div>;

  return (
    <div className="model-detail-page">
      <header className="detail-header">
        <h1>{brand} {model}</h1>
        <p className="subtitle">Oportunidades rentables detectadas en subastas internacionales</p>
      </header>

      <div className="ad-list">
        {opportunities.length > 0 ? (
          opportunities.map((opp, index) => (
            <AdCard
              key={index}
              opportunity={opp}
              onInspect={(opp) => setSelectedAd(opp)}
            />
          ))
        ) : (
          <div className="no-results">No se han encontrado anuncios rentables para este modelo en este momento.</div>
        )}
      </div>

      {selectedAd && (
        <InspectionForm
          opportunity={selectedAd}
          onClose={() => setSelectedAd(null)}
          onSuccess={() => setSelectedAd(null)}
        />
      )}
    </div>
  );
};

export default ModelDetail;
