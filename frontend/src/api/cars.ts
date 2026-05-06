export interface CarExport {
  id: string;
  portal: string;
  brand: string;
  model: string;
  vehicle_status: string;
  vehicle_status_check?: string;
  year: number;
  mileage: number;
  fuel: string;
  power?: number;
  price: number;
  currency: string;
  price_eur: number;
  price_spain_avg: number;
  country: string;
  location: string;
  url: string;
  transport_cost: number;
  import_tax: number;
  itv_cost: number;
  registration_cost: number;
  gestor_cost: number;
  total_import_cost: number;
  final_price: number;
  estimated_profit: number;
  roi_percentage?: number;
  created_at?: string;
  images?: string[];
}

export interface ExportResponse {
  total: number;
  cars: CarExport[];
}

import { API_BASE_URL } from '../config';

export async function fetchCars(skip = 0, limit = 100): Promise<ExportResponse> {
  const token = sessionStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/cars/export?skip=${skip}&limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  if (!response.ok) {
    if (response.status === 401) {
      sessionStorage.removeItem('token');
      window.location.href = '/login';
    }
    throw new Error('Failed to fetch cars');
  }
  return response.json();
}

export async function toggleFavorite(carId: string): Promise<void> {
  const token = sessionStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/favorites`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ car_id: carId })
  });
  if (!response.ok) throw new Error('Failed to toggle favorite');
}

export async function deleteFavorite(carId: string): Promise<void> {
  const token = sessionStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/favorites?car_id=${encodeURIComponent(carId)}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  if (!response.ok) throw new Error('Failed to delete favorite');
}

export async function fetchFavorites(): Promise<CarExport[]> {
  const token = sessionStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/favorites`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  if (!response.ok) throw new Error('Failed to fetch favorites');
  const data = await response.json();
  // We return the car objects from the favorite records
  return data.map((fav: any) => fav.car).filter((car: any) => car !== null);
}

export async function recordVisit(carId: string, modelName: string): Promise<void> {
  const token = sessionStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/user/record-visit?car_id=${encodeURIComponent(carId)}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ model_name: modelName })
  });
  if (!response.ok) console.error('Failed to record visit');
}
