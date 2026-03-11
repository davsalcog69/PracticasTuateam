import React, { useState } from 'react';
import type { InspectionRequestInput, ProfitableOpportunity } from '../../types';
interface InspectionFormProps {
  opportunity: ProfitableOpportunity;
  onClose: () => void;
  onSuccess: () => void;
}

const InspectionForm: React.FC<InspectionFormProps> = ({ opportunity, onClose, onSuccess }) => {
  const [formData, setFormData] = useState<Partial<InspectionRequestInput>>({
    car_id: opportunity.url_anuncio, // Using URL as ID for now as per previous logic
    name: '',
    email: '',
    phone: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch('/api/inspection-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        alert('Solicitud enviada correctamente');
        onSuccess();
      } else {
        alert('Error al enviar la solicitud');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error de conexión');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close" onClick={onClose}>&times;</button>
        <h2>Solicitar Inspección</h2>
        <p className="modal-subtitle">Para: {opportunity.brand} {opportunity.model} ({opportunity.year_group})</p>

        <form onSubmit={handleSubmit} className="inspection-form">
          <div className="form-group">
            <label>Nombre Completo</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={e => setFormData({ ...formData, name: e.target.value })}
              placeholder="Ej: Juan Pérez"
            />
          </div>

          <div className="form-group">
            <label>Correo Electrónico</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={e => setFormData({ ...formData, email: e.target.value })}
              placeholder="juan@ejemplo.com"
            />
          </div>

          <div className="form-group">
            <label>Teléfono</label>
            <input
              type="tel"
              required
              value={formData.phone}
              onChange={e => setFormData({ ...formData, phone: e.target.value })}
              placeholder="+34 600 000 000"
            />
          </div>

          <div className="form-group">
            <label>Mensaje (Opcional)</label>
            <textarea
              rows={4}
              value={formData.message}
              onChange={e => setFormData({ ...formData, message: e.target.value })}
              placeholder="Indica cualquier detalle adicional..."
            />
          </div>

          <button type="submit" className="btn btn-primary btn-block" disabled={isSubmitting}>
            {isSubmitting ? 'Enviando...' : 'Enviar Solicitud'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default InspectionForm;
