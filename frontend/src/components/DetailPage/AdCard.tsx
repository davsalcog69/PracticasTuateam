import React from 'react';
import type { ProfitableOpportunity } from '../../types';

interface AdCardProps {
  opportunity: ProfitableOpportunity;
  onInspect: (opportunity: ProfitableOpportunity) => void;
}

const AdCard: React.FC<AdCardProps> = ({ opportunity, onInspect }) => {
  const {
    brand,
    model,
    year_group,
    precio_medio_españa,
    precio_emirates,
    coste_total_importación,
    margen_estimado,
    url_anuncio
  } = opportunity;

  const handleCarfax = () => {
    // Assuming we might have a VIN in a real scenario, but for now we follow the rule
    const carfaxUrl = "https://www.carfax.com/";
    window.open(carfaxUrl, '_blank');
  };

  return (
    <div className="ad-card">
      <div className="ad-image-container">
        <img src="https://via.placeholder.com/400x250?text=Car+Image" alt={`${brand} ${model}`} className="ad-image" />
        <div className="ad-portal-tag">Emirates Auction</div>
      </div>

      <div className="ad-content">
        <div className="ad-header">
          <h3>{brand} {model}</h3>
          <span className="ad-year">{year_group}</span>
        </div>

        <div className="ad-info">
          <p><strong>Kilometraje:</strong> -- km</p>
          <div className="ad-price-grid">
            <div className="price-item">
              <span className="price-label">Precio Origen</span>
              <span className="price-value">{precio_emirates.toLocaleString()} €</span>
            </div>
            <div className="price-item">
              <span className="price-label">Importación</span>
              <span className="price-value">{coste_total_importación.toLocaleString()} €</span>
            </div>
            <div className="price-item highlight">
              <span className="price-label">Venta España (PVP)</span>
              <span className="price-value">{precio_medio_españa.toLocaleString()} €</span>
            </div>
          </div>

          <div className="ad-margin">
            <span className="margin-label">Margen Estimado</span>
            <span className="margin-value">{margen_estimado.toLocaleString()} €</span>
          </div>
        </div>

        <div className="ad-actions">
          <button className="btn btn-secondary" onClick={() => window.open(url_anuncio, '_blank')}>
            Ver Anuncio Original
          </button>
          <button className="btn btn-info" onClick={handleCarfax}>
            Historial CARFAX
          </button>
          <button className="btn btn-primary" onClick={() => onInspect(opportunity)}>
            Solicitar Inspección
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdCard;
