import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MapPin, 
  Home, 
  HardHat, 
  Ban, 
  Info, 
  AlertTriangle, 
  CheckCircle, 
  Droplets, 
  Mountain, 
  Route,
  X
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { PredictionResponse, ConstructionVerdict } from '@/types';

interface RiskDashboardProps {
  data: PredictionResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

export function RiskDashboard({ data, isOpen, onClose }: RiskDashboardProps) {
  const [placeName, setPlaceName] = useState<string>("Locating...");

  // 1. Reverse Geocoding (Nominatim OSM)
  useEffect(() => {
    if (data?.location) {
      const { latitude, longitude } = data.location;
      fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`)
        .then(res => res.json())
        .then(geoData => {
          const village = geoData.address.village || geoData.address.town || geoData.address.city || geoData.address.suburb || "Unknown Area";
          const district = geoData.address.state_district || geoData.address.county || "";
          setPlaceName(`${village}${district ? `, ${district}` : ''}`);
        })
        .catch(() => setPlaceName("Kerala, India"));
    }
  }, [data]);

  // If panel is closed or data is missing, render nothing (AnimatePresence handles exit)
  if (!data) return null;

  // 2. Data Mapping & Calculations
  const { flood_risk, confidence, environmental_data, historical_floods, location } = data;

  const verdictMap: Record<string, { label: ConstructionVerdict, color: string, bg: string, icon: React.ElementType, title: string }> = {
    Low: { label: 'Suitable', color: 'text-emerald-500', bg: 'bg-emerald-500', icon: Home, title: "This land is safe to build your home on" },
    Medium: { label: 'Conditional', color: 'text-amber-500', bg: 'bg-amber-500', icon: HardHat, title: "Building here is possible, but needs care" },
    High: { label: 'Avoid', color: 'text-rose-500', bg: 'bg-rose-500', icon: Ban, title: "We advise against building your home here" }
  };

  const currentVerdict = verdictMap[flood_risk] || verdictMap.Medium;
  const VerdictIcon = currentVerdict.icon;

  // Calculate Suitability Score (0-100)
  const calcScore = (): number => {
    const safeProb = (100 - (confidence?.High || 0)); 
    const elevationScore = Math.min(environmental_data.elevation / 20 * 100, 100); 
    const riverScore = Math.min(environmental_data.river_distance / 3 * 100, 100); 
    
    const rawScore = (safeProb * 0.5) + (elevationScore * 0.25) + (riverScore * 0.25);
    return Math.round(Math.max(0, Math.min(100, rawScore)));
  };
  
  const score = calcScore();

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ x: '100%', opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: '100%', opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="absolute top-0 right-0 w-full md:w-[450px] h-full max-h-screen bg-slate-900/95 backdrop-blur-xl border-l border-slate-800 shadow-2xl flex flex-col z-50"
        >
          {/* SECTION 1: Verdict Banner */}
          <div className={`p-6 border-b border-slate-800 relative overflow-hidden shrink-0`}>
            <div className={`absolute inset-0 opacity-10 ${currentVerdict.bg}`} />
            
            {/* Header / Close Button */}
            <div className="relative z-20 flex justify-end mb-2">
              <motion.button
                onClick={onClose}
                className="w-8 h-8 rounded-lg bg-slate-800/50 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors border border-slate-700"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <X className="w-4 h-4" />
              </motion.button>
            </div>

            <div className="relative z-10 flex justify-between items-start mb-4">
              <div>
                <div className="flex items-baseline gap-2">
                  <h2 className={`text-4xl font-bold ${currentVerdict.color}`}>{flood_risk}</h2>
                  <span className={`text-lg font-medium tracking-wide ${currentVerdict.color}`}>
                    ({currentVerdict.label})
                  </span>
                </div>
                <p className="text-slate-200 font-medium mt-2 text-lg leading-tight">
                  {currentVerdict.title}
                </p>
              </div>
              <VerdictIcon className={`w-12 h-12 ${currentVerdict.color} opacity-80`} />
            </div>

            <div className="flex items-start gap-2 mt-4 text-slate-400 bg-slate-950/50 p-3 rounded-lg border border-slate-800/50">
              <MapPin className="w-5 h-5 shrink-0 text-sky-400 mt-0.5" />
              <div>
                <p className="font-medium text-slate-200">{placeName}</p>
                <p className="text-xs font-mono mt-1 text-slate-500">
                  {location.latitude.toFixed(4)}°N, {location.longitude.toFixed(4)}°E
                </p>
              </div>
            </div>
          </div>

          {/* Scrollable Content */}
          <ScrollArea className="flex-1 min-h-0 overflow-hidden">
            <div className="p-6 space-y-8 pb-8">
              
              {/* SECTION 2: Construction Suitability Score */}
              <section>
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Construction Suitability</h3>
                <div className="bg-slate-950/50 rounded-xl p-5 border border-slate-800/50">
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-slate-300 font-medium">Score</span>
                    <div className="text-right">
                      <span className={`text-3xl font-bold ${score >= 70 ? 'text-emerald-400' : score >= 40 ? 'text-amber-400' : 'text-rose-400'}`}>
                        {score}
                      </span>
                      <span className="text-slate-500 font-medium">/100</span>
                    </div>
                  </div>
                  <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden relative">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${score}%` }}
                      transition={{ duration: 1.5, ease: "easeOut" }}
                      className={`absolute top-0 left-0 h-full rounded-full ${score >= 70 ? 'bg-emerald-500' : score >= 40 ? 'bg-amber-500' : 'bg-rose-500'}`}
                    />
                  </div>
                </div>
              </section>

              {/* SECTION 3: Site Risk Factors */}
              <section>
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Site Risk Factors</h3>
                <div className="grid grid-cols-2 gap-3">
                  <FactorCard icon={Droplets} label="Annual Rainfall" value={`${environmental_data.rainfall} mm`} sub="High = drainage needed" />
                  <FactorCard icon={Mountain} label="Site Elevation" value={`${environmental_data.elevation} m`} sub="Low = flood-prone" />
                  <FactorCard icon={Route} label="Nearest River" value={`${environmental_data.river_distance} km`} sub="Riparian rules may apply" />
                  <FactorCard icon={AlertTriangle} label="Drainage Density" value={`${environmental_data.soil_moisture}%`} sub="High = weak soil" />
                </div>
              </section>

              {/* SECTION 4: Flood History Timeline */}
              <section>
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Historical Flood Events</h3>
                <div className="bg-slate-950/50 rounded-xl p-5 border border-slate-800/50">
                  <div className="flex justify-between gap-2 mb-4">
                    <TimelineYear year="2018" flooded={historical_floods?.["2018"] || false} />
                    <TimelineYear year="2019" flooded={historical_floods?.["2019"] || false} />
                    <TimelineYear year="2021" flooded={historical_floods?.["2021"] || false} />
                  </div>
                  <p className="text-sm text-slate-400 text-center">
                    Total observed major flood events: <strong className="text-slate-200">{historical_floods?.total_count || 0} of 3</strong> years
                  </p>
                </div>
              </section>

              {/* SECTION 5: Construction Guidelines */}
              <section>
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Construction Guidelines</h3>
                <div className="bg-slate-950/50 rounded-xl p-5 border border-slate-800/50 space-y-4">
                  {flood_risk === 'Low' && (
                    <>
                      <GuidelineItem icon={CheckCircle} color="text-emerald-400" text="This plot looks safe — it stayed dry through Kerala's major flood years." />
                      <GuidelineItem icon={CheckCircle} color="text-emerald-400" text="You can proceed with standard home construction. No special flood-proofing required." />
                      <GuidelineItem icon={Info} color="text-sky-400" text="Visit your local panchayat to confirm standard building permit processes." />
                    </>
                  )}
                  {flood_risk === 'Medium' && (
                    <>
                      <GuidelineItem icon={AlertTriangle} color="text-amber-400" text="Build your plinth at least 0.6m above the road level (NBC 2016 guideline)." />
                      <GuidelineItem icon={AlertTriangle} color="text-amber-400" text="Make sure your plot has proper drainage around the house and get a soil test done." />
                      <GuidelineItem icon={Info} color="text-sky-400" text="Check if your area needs a KSDMA clearance before construction." />
                    </>
                  )}
                  {flood_risk === 'High' && (
                    <>
                      <GuidelineItem icon={Ban} color="text-rose-400" text="We strongly advise against building your home here." />
                      <GuidelineItem icon={Ban} color="text-rose-400" text="This land has flooded multiple times; your home and belongings would be at serious risk." />
                      <GuidelineItem icon={Info} color="text-sky-400" text="You may face legal restrictions. Speak with local authorities and DTCP before deciding." />
                    </>
                  )}
                </div>
              </section>

            </div>
          </ScrollArea>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// --- Helper Components ---

function FactorCard({ icon: Icon, label, value, sub }: { icon: any, label: string, value: string | number, sub: string }) {
  return (
    <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800/50">
      <div className="flex items-center gap-2 mb-1 text-slate-400">
        <Icon className="w-4 h-4" />
        <span className="text-xs font-medium uppercase tracking-wider">{label}</span>
      </div>
      <div className="text-lg font-bold text-slate-200 mb-1">{value}</div>
      <div className="text-[10px] text-slate-500 leading-tight">{sub}</div>
    </div>
  );
}

function TimelineYear({ year, flooded }: { year: string, flooded: boolean }) {
  return (
    <div className="flex-1 flex flex-col items-center gap-2">
      <span className="text-xs font-bold text-slate-500">{year}</span>
      <div className={`w-full h-8 rounded flex items-center justify-center border ${
        flooded ? 'bg-rose-500/20 border-rose-500/50 text-rose-400' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-500'
      }`}>
        <span className="text-[10px] font-bold uppercase tracking-wider">
          {flooded ? 'Flooded' : 'Clear'}
        </span>
      </div>
    </div>
  );
}

function GuidelineItem({ icon: Icon, text, color }: { icon: any, text: string, color: string }) {
  return (
    <div className="flex items-start gap-3">
      <Icon className={`w-5 h-5 shrink-0 mt-0.5 ${color}`} />
      <p className="text-sm text-slate-300 leading-relaxed">{text}</p>
    </div>
  );
}

export default RiskDashboard;