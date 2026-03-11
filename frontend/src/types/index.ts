export type CarAd = {
  id: string;
  portal: string;
  brand: string;
  model: string;
  version?: string;
  year: number;
  kilometrage: number;
  fuel: string;
  power?: number;
  price: number;
  currency: string;
  location: string;
  url: string;
  images: string[];
};

export type ProfitableOpportunity = {
  brand: string;
  model: string;
  year_group: number;
  precio_medio_españa: number;
  precio_emirates: number;
  coste_total_importación: number;
  margen_estimado: number;
  url_anuncio: string;
  car_id?: string;
};

export type InspectionRequestInput = {
  car_id: string;
  name: string;
  email: string;
  phone: string;
  message?: string;
};