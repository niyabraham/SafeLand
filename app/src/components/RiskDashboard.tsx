import { motion, AnimatePresence } from 'framer-motion';
import { 
  CloudRain, 
  Mountain, 
  Droplets, 
  Waves, 
  MapPin, 
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  X,
  Navigation
} from 'lucide-react';
import type { PredictionResponse, FloodRiskLevel } from '@/types';

interface RiskDashboardProps {
  data: PredictionResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

const riskConfig: Record<FloodRiskLevel, {
  color: string;
  bgColor: string;
  glowColor: string;
  borderColor: string;
  icon: React.ReactNode;
  description: string;
  gradient: string;
}> = {
  Low: {
    color: '#10b981',
    bgColor: 'rgba(16, 185, 129, 0.15)',
    glowColor: 'rgba(16, 185, 129, 0.4)',
    borderColor: 'rgba(16, 185, 129, 0.3)',
    icon: <CheckCircle2 className="w-8 h-8" />,
    description: 'Minimal flood risk detected. Area is relatively safe.',
    gradient: 'from-emerald-400 to-emerald-600',
  },
  Medium: {
    color: '#f59e0b',
    bgColor: 'rgba(245, 158, 11, 0.15)',
    glowColor: 'rgba(245, 158, 11, 0.4)',
    borderColor: 'rgba(245, 158, 11, 0.3)',
    icon: <AlertCircle className="w-8 h-8" />,
    description: 'Moderate flood risk. Stay cautious and monitor conditions.',
    gradient: 'from-amber-400 to-amber-600',
  },
  High: {
    color: '#e11d48',
    bgColor: 'rgba(225, 29, 72, 0.15)',
    glowColor: 'rgba(225, 29, 72, 0.4)',
    borderColor: 'rgba(225, 29, 72, 0.3)',
    icon: <AlertTriangle className="w-8 h-8" />,
    description: 'High flood risk! Take immediate precautions.',
    gradient: 'from-rose-400 to-rose-600',
  },
};

interface DataCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  unit: string;
  color: string;
  delay: number;
}

function DataCard({ icon, label, value, unit, color, delay }: DataCardProps) {
  return (
    <motion.div
      className="data-card glass rounded-xl p-4 relative overflow-hidden group"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
      whileHover={{ scale: 1.02 }}
    >
      {/* Glow effect on hover */}
      <div 
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{ 
          background: `radial-gradient(circle at center, ${color}10 0%, transparent 70%)` 
        }}
      />
      
      <div className="relative flex items-center gap-4">
        <div 
          className="w-12 h-12 rounded-xl flex items-center justify-center transition-transform duration-300 group-hover:scale-110"
          style={{ background: `${color}20`, color }}
        >
          {icon}
        </div>
        
        <div className="flex-1">
          <p className="text-slate-400 text-sm font-medium">{label}</p>
          <div className="flex items-baseline gap-1">
            <motion.span
              className="text-2xl font-bold text-slate-100"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: delay + 0.2 }}
            >
              <AnimatedNumber value={value} />
            </motion.span>
            <span className="text-slate-500 text-sm">{unit}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Animated number counter
function AnimatedNumber({ value }: { value: number }) {
  return (
    <motion.span
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {(value || 0).toFixed(1)}
    </motion.span>
  );
}

// Risk Badge Component
function RiskBadge({ level }: { level: FloodRiskLevel }) {
  const config = riskConfig[level];
  
  return (
    <motion.div
      className="relative"
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      {/* Glow effect */}
      <motion.div
        className="absolute inset-0 rounded-2xl blur-xl"
        style={{ background: config.glowColor }}
        animate={{ 
          opacity: [0.5, 0.8, 0.5],
          scale: [1, 1.05, 1],
        }}
        transition={{ 
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      
      {/* Main badge */}
      <div
        className="relative px-8 py-4 rounded-2xl border-2 flex items-center gap-4"
        style={{ 
          background: config.bgColor,
          borderColor: config.borderColor,
          boxShadow: `0 0 30px ${config.glowColor}`,
        }}
      >
        <motion.div
          style={{ color: config.color }}
          animate={{ 
            rotate: level === 'High' ? [0, -10, 10, -10, 10, 0] : 0,
          }}
          transition={{ 
            duration: 0.5,
            repeat: level === 'High' ? Infinity : 0,
            repeatDelay: 2,
          }}
        >
          {config.icon}
        </motion.div>
        
        <div>
          <p className="text-slate-400 text-sm font-medium">Flood Risk Level</p>
          <motion.p
            className={`text-3xl font-bold bg-gradient-to-r ${config.gradient} bg-clip-text text-transparent`}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            {level}
          </motion.p>
        </div>
      </div>
    </motion.div>
  );
}

// Location Info Component
function LocationInfo({ latitude, longitude }: { latitude: number; longitude: number }) {
  return (
    <motion.div
      className="flex items-center gap-3 glass rounded-xl px-4 py-3"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.1 }}
    >
      <div className="w-10 h-10 rounded-lg bg-sky-500/20 flex items-center justify-center">
        <Navigation className="w-5 h-5 text-sky-400" />
      </div>
      <div>
        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider">Coordinates</p>
        <p className="text-slate-200 text-sm font-mono">
          {latitude.toFixed(4)}°, {longitude.toFixed(4)}°
        </p>
      </div>
    </motion.div>
  );
}

export function RiskDashboard({ data, isOpen, onClose }: RiskDashboardProps) {
  if (!data) return null;

  const { location, environmental_data, flood_risk } = data;
  const riskSettings = riskConfig[flood_risk];

  const environmentalCards = [
    {
      icon: <CloudRain className="w-6 h-6" />,
      label: 'Rainfall',
      value: environmental_data.rainfall,
      unit: 'mm',
      color: '#38bdf8',
    },
    {
      icon: <Mountain className="w-6 h-6" />,
      label: 'Elevation',
      value: environmental_data.elevation,
      unit: 'm',
      color: '#a78bfa',
    },
    {
      icon: <Droplets className="w-6 h-6" />,
      label: 'Soil Moisture',
      value: environmental_data.soil_moisture,
      unit: '%',
      color: '#22d3ee',
    },
    {
      icon: <Waves className="w-6 h-6" />,
      label: 'Water Level',
      value: environmental_data.water_level,
      unit: 'm',
      color: '#60a5fa',
    },
    {
      icon: <MapPin className="w-6 h-6" />,
      label: 'River Distance',
      value: environmental_data.river_distance,
      unit: 'km',
      color: '#34d399',
    },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="absolute right-0 top-0 h-full w-full md:w-[420px] z-50"
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          <div className="h-full glass-strong border-l border-slate-700/50 flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-700/50">
              <div>
                <h2 className="text-xl font-bold text-slate-100">Risk Assessment</h2>
                <p className="text-slate-400 text-sm">Environmental analysis results</p>
              </div>
              <motion.button
                onClick={onClose}
                className="w-10 h-10 rounded-lg bg-slate-800/50 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <X className="w-5 h-5" />
              </motion.button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Risk Badge */}
              <RiskBadge level={flood_risk} />

              {/* Risk Description */}
              <motion.p
                className="text-slate-300 text-center px-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                {riskSettings.description}
              </motion.p>

              {/* Location Info */}
              <LocationInfo 
                latitude={location.lat || 0} 
                longitude={location.lon || 0} 
              />

              {/* Environmental Data Grid */}
              <div>
                <motion.h3
                  className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  Environmental Data
                </motion.h3>
                
                <div className="grid grid-cols-1 gap-3">
                  {environmentalCards.map((card, index) => (
                    <DataCard
                      key={card.label}
                      {...card}
                      delay={0.3 + index * 0.1}
                    />
                  ))}
                </div>
              </div>

              {/* Safety Tips */}
              <motion.div
                className="glass rounded-xl p-4 border border-slate-700/50"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
              >
                <h4 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  Safety Recommendations
                </h4>
                <ul className="space-y-2">
                  {flood_risk === 'Low' && (
                    <>
                      <li className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-emerald-400 mt-0.5">•</span>
                        Monitor weather forecasts regularly
                      </li>
                      <li className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-emerald-400 mt-0.5">•</span>
                        Keep emergency contacts updated
                      </li>
                    </>
                  )}
                  {flood_risk === 'Medium' && (
                    <>
                      <li className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-amber-400 mt-0.5">•</span>
                        Prepare emergency kit and evacuation plan
                      </li>
                      <li className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-amber-400 mt-0.5">•</span>
                        Avoid low-lying areas during heavy rain
                      </li>
                      <li className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-amber-400 mt-0.5">•</span>
                        Stay tuned to local weather alerts
                      </li>
                    </>
                  )}
                  {flood_risk === 'High' && (
                    <>
                      <li className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-rose-400 mt-0.5">•</span>
                        <span className="font-medium text-rose-300">Evacuate to higher ground immediately</span>
                      </li>
                      <li className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-rose-400 mt-0.5">•</span>
                        Follow official evacuation orders
                      </li>
                      <li className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-rose-400 mt-0.5">•</span>
                        Do not attempt to cross flooded roads
                      </li>
                      <li className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-rose-400 mt-0.5">•</span>
                        Keep emergency supplies ready
                      </li>
                    </>
                  )}
                </ul>
              </motion.div>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-slate-700/50 text-center">
              <p className="text-slate-500 text-xs">
                Data provided by SafeLand AI Risk Assessment
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default RiskDashboard;
