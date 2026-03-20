import { useEffect, useRef, useState, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import { motion, AnimatePresence } from 'framer-motion';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapLoadingIndicator } from './LoadingSpinner';
import type { FloodRiskLevel, LocationData } from '@/types';

// Fix Leaflet default icon issue
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

// Custom marker icons based on risk level
const createRiskIcon = (risk: FloodRiskLevel | null, isLoading: boolean) => {
  if (isLoading) {
    return L.divIcon({
      className: 'custom-marker',
      html: `
        <div class="relative w-10 h-10 flex items-center justify-center">
          <div class="absolute inset-0 rounded-full border-2 border-transparent border-t-sky-400 animate-spin"></div>
          <div class="absolute inset-2 rounded-full bg-sky-400/40 animate-pulse"></div>
        </div>
      `,
      iconSize: [40, 40],
      iconAnchor: [20, 20],
    });
  }

  const colors = {
    Low: '#10b981',
    Medium: '#f59e0b',
    High: '#e11d48',
  };

  const color = risk ? colors[risk] : '#38bdf8';

  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div class="relative w-10 h-10">
        <div class="marker-pulse ${risk?.toLowerCase() || ''}" style="background: ${color}40"></div>
        <div class="marker-pin" style="background: ${color}; box-shadow: 0 0 20px ${color}80">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
            <circle cx="12" cy="9" r="2.5"/>
          </svg>
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 40],
  });
};

// Ripple effect component
interface Ripple {
  id: number;
  x: number;
  y: number;
}

interface MapClickHandlerProps {
  onMapClick: (lat: number, lng: number) => void;
  onRipple: (ripple: Ripple) => void;
}

function MapClickHandler({ onMapClick, onRipple }: MapClickHandlerProps) {
  const map = useMap();
  
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      
      // Create ripple effect at click position
      const point = map.latLngToContainerPoint(e.latlng);
      onRipple({
        id: Date.now(),
        x: point.x,
        y: point.y,
      });
      
      onMapClick(lat, lng);
    },
  });
  
  return null;
}

// Map controller for programmatic map updates
interface MapControllerProps {
  center: [number, number];
  zoom: number;
}

function MapController({ center, zoom }: MapControllerProps) {
  const map = useMap();
  
  useEffect(() => {
    map.setView(center, zoom, {
      animate: true,
      duration: 1,
    });
  }, [center, zoom, map]);
  
  return null;
}

interface MapComponentProps {
  selectedLocation: LocationData | null;
  riskLevel: FloodRiskLevel | null;
  isLoading: boolean;
  onLocationSelect: (location: LocationData) => void;
  defaultCenter?: [number, number];
  defaultZoom?: number;
}

export function MapComponent({
  selectedLocation,
  riskLevel,
  isLoading,
  onLocationSelect,
  defaultCenter = [10.8505, 76.2711], // Center of India
  defaultZoom = 7,
}: MapComponentProps) {
  const [ripples, setRipples] = useState<Ripple[]>([]);
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  // Add these bounds for Kerala/Southern India
  const keralaBounds: L.LatLngBoundsExpression = [
    [8.0, 74.5], // Southwest coordinates
    [13.0, 77.5] // Northeast coordinates
  ];
  const handleMapClick = useCallback((lat: number, lng: number) => {
    onLocationSelect({ latitude: lat, longitude: lng });
  }, [onLocationSelect]);

  const handleRipple = useCallback((ripple: Ripple) => {
    setRipples((prev) => [...prev, ripple]);
    
    // Remove ripple after animation
    setTimeout(() => {
      setRipples((prev) => prev.filter((r) => r.id !== ripple.id));
    }, 600);
  }, []);

  const markerPosition: [number, number] | null = selectedLocation
    ? [selectedLocation.latitude, selectedLocation.longitude]
    : null;

  return (
    <div ref={containerRef} className="relative w-full h-full overflow-hidden rounded-2xl">
      {/* Flow Lines Background Effect */}
      <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-px h-full bg-gradient-to-b from-transparent via-sky-400/20 to-transparent"
            style={{
              left: `${20 + i * 15}%`,
            }}
            animate={{
              y: ['-100%', '100%'],
            }}
            transition={{
              duration: 8 + i * 2,
              repeat: Infinity,
              ease: 'linear',
              delay: i * 1.5,
            }}
          />
        ))}
      </div>

      {/* Map Container */}
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        className="w-full h-full z-10"
        ref={mapRef}
        zoomControl={false}
        attributionControl={true}
        maxBounds={keralaBounds}     // Prevents panning outside Kerala
        maxBoundsViscosity={1.0}     // Makes the bounds feel solid
        minZoom={6}
      >
        {/* Dark themed map tiles - CartoDB Dark Matter */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          subdomains="abcd"
          maxZoom={20}
        />

        {/* Map Controller for view updates */}
        <MapController 
          center={markerPosition || defaultCenter} 
          zoom={selectedLocation ? 12 : defaultZoom} 
        />

        {/* Click Handler */}
        <MapClickHandler onMapClick={handleMapClick} onRipple={handleRipple} />

        {/* Location Marker */}
        <AnimatePresence>
          {markerPosition && (
            <Marker
              position={markerPosition}
              icon={createRiskIcon(riskLevel, isLoading)}
              eventHandlers={{
                add: (e) => {
                  // Animate marker drop
                  const marker = e.target.getElement();
                  if (marker) {
                    marker.style.transformOrigin = 'bottom center';
                    marker.animate([
                      { transform: 'translateY(-50px) scale(0.5)', opacity: 0 },
                      { transform: 'translateY(10px) scale(1.1)', opacity: 1, offset: 0.6 },
                      { transform: 'translateY(0) scale(1)', opacity: 1 },
                    ], {
                      duration: 600,
                      easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
                    });
                  }
                },
              }}
            />
          )}
        </AnimatePresence>

        {/* Custom Zoom Control */}
        <div className="absolute bottom-6 right-6 z-[400] flex flex-col gap-2">
          <motion.button
            className="w-10 h-10 rounded-lg glass flex items-center justify-center text-slate-300 hover:text-white hover:bg-slate-700/50 transition-colors"
            onClick={() => mapRef.current?.zoomIn()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
          </motion.button>
          <motion.button
            className="w-10 h-10 rounded-lg glass flex items-center justify-center text-slate-300 hover:text-white hover:bg-slate-700/50 transition-colors"
            onClick={() => mapRef.current?.zoomOut()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14"/>
            </svg>
          </motion.button>
        </div>
      </MapContainer>

      {/* Ripple Effects Overlay */}
      <div className="absolute inset-0 pointer-events-none z-20 overflow-hidden rounded-2xl">
        <AnimatePresence>
          {ripples.map((ripple) => (
            <motion.div
              key={ripple.id}
              className="absolute rounded-full border-2 border-sky-400/60"
              style={{
                left: ripple.x,
                top: ripple.y,
                transform: 'translate(-50%, -50%)',
              }}
              initial={{ width: 0, height: 0, opacity: 1 }}
              animate={{ width: 100, height: 100, opacity: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* Click Instruction Overlay */}
      {!selectedLocation && (
        <motion.div
          className="absolute inset-0 z-30 flex items-center justify-center pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <div className="glass-strong px-6 py-4 rounded-2xl text-center">
            <motion.div
              className="w-12 h-12 mx-auto mb-3 rounded-full bg-sky-500/20 flex items-center justify-center"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                <circle cx="12" cy="9" r="2.5"/>
              </svg>
            </motion.div>
            <p className="text-slate-200 font-medium">Click anywhere on the map</p>
            <p className="text-slate-400 text-sm mt-1">to assess flood risk</p>
          </div>
        </motion.div>
      )}

      {/* Loading Overlay */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            className="absolute inset-0 z-40 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="glass-strong px-8 py-6 rounded-2xl flex flex-col items-center gap-4">
              <MapLoadingIndicator />
              <p className="text-slate-300 font-medium">Analyzing location...</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default MapComponent;
