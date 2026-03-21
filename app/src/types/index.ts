// SafeLand Type Definitions

export interface LocationData {
  latitude: number;
  longitude: number;
  address?: string;
}

export interface EnvironmentalData {
  rainfall: number;
  elevation: number;
  soil_moisture: number;
  water_level: number;
  river_distance: number;
}

// Keep the existing risk level since the backend still sends it
export type FloodRiskLevel = 'Low' | 'Medium' | 'High';

// NEW: Three-Tier Verdict System mapped to construction suitability
export type ConstructionVerdict = 'Suitable' | 'Conditional' | 'Avoid';

// NEW: Suitability Score interface for the dashboard calculation
export interface SuitabilityScore {
  score: number;       // 0 to 100
  verdict: ConstructionVerdict;
}

export interface PredictionResponse {
  location: {
    latitude: number;
    longitude: number;
  };
  environmental_data: EnvironmentalData;
  // NEW: Added historical floods data
  historical_floods: {
    "2018": boolean;
    "2019": boolean;
    "2021": boolean;
    total_count: number;
  };
  flood_risk: FloodRiskLevel;
  // NEW: Added confidence scores
  confidence: Record<FloodRiskLevel, number>;
}

export interface MapClickEvent {
  latlng: {
    lat: number;
    lng: number;
  };
}

export interface RiskConfig {
  color: string;
  bgColor: string;
  glowColor: string;
  icon: string;
  description: string;
}