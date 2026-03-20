import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Droplets, 
  Shield, 
  Map as MapIcon, 
  Info,
  Github,
  Twitter,
  Menu,
  X
} from 'lucide-react';
import { MapComponent } from '@/components/MapComponent';
import { RiskDashboard } from '@/components/RiskDashboard';
import type { LocationData, PredictionResponse, FloodRiskLevel } from '@/types';
import { toast } from 'sonner';

// API Configuration
const API_BASE_URL = 'http://127.0.0.1:5000';

function App() {
  const [selectedLocation, setSelectedLocation] = useState<LocationData | null>(null);
  const [predictionData, setPredictionData] = useState<PredictionResponse | null>(null);
  const [riskLevel, setRiskLevel] = useState<FloodRiskLevel | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDashboardOpen, setIsDashboardOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Handle location selection from map
  const handleLocationSelect = useCallback(async (location: LocationData) => {
    setSelectedLocation(location);
    setIsLoading(true);
    setIsDashboardOpen(false);

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          latitude: location.latitude,
          longitude: location.longitude,
        }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data: PredictionResponse = await response.json();
      setPredictionData(data);
      setRiskLevel(data.flood_risk);
      setIsDashboardOpen(true);
      
      toast.success('Risk assessment complete!', {
        description: `Flood risk level: ${data.flood_risk}`,
      });
    } catch (error) {
      console.error('Error fetching prediction:', error);
      
      // Remove the mock data generation and show an actual error to the user
      toast.error('Analysis Failed', {
        description: 'Could not connect to the SafeLand prediction server. Please try again later.',
      });
      
      // Ensure the dashboard doesn't open with empty/fake data
      setPredictionData(null);
      setRiskLevel(null);
      setIsDashboardOpen(false);
      
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Close dashboard
  const handleCloseDashboard = useCallback(() => {
    setIsDashboardOpen(false);
  }, []);

  // Navigation items
  const navItems = [
    { label: 'Map', icon: MapIcon, href: '#map' },
    { label: 'About', icon: Info, href: '#about' },
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 overflow-x-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 pointer-events-none z-0">
        {/* Gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800/50 to-slate-900" />
        
        {/* Animated flow lines */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute h-full w-px"
              style={{
                left: `${10 + i * 12}%`,
                background: `linear-gradient(to bottom, transparent, ${
                  i % 2 === 0 ? 'rgba(56, 189, 248, 0.1)' : 'rgba(129, 140, 248, 0.1)'
                }, transparent)`,
              }}
              animate={{
                y: ['-100%', '100%'],
              }}
              transition={{
                duration: 10 + i * 2,
                repeat: Infinity,
                ease: 'linear',
                delay: i * 1.2,
              }}
            />
          ))}
        </div>

        {/* Floating particles */}
        <div className="absolute inset-0">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={`particle-${i}`}
              className="absolute w-1 h-1 rounded-full bg-sky-400/30"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                y: [0, -30, 0],
                opacity: [0.2, 0.6, 0.2],
              }}
              transition={{
                duration: 4 + Math.random() * 4,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: Math.random() * 4,
              }}
            />
          ))}
        </div>
      </div>

      {/* Navigation */}
      <motion.nav
        className="fixed top-0 left-0 right-0 z-50 glass border-b border-slate-700/30"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <motion.div 
              className="flex items-center gap-3"
              whileHover={{ scale: 1.02 }}
            >
              <div className="relative w-10 h-10">
                <motion.div
                  className="absolute inset-0 rounded-xl bg-gradient-to-br from-sky-400 to-indigo-500"
                  animate={{
                    rotate: [0, 360],
                  }}
                  transition={{
                    duration: 20,
                    repeat: Infinity,
                    ease: 'linear',
                  }}
                  style={{ borderRadius: '12px' }}
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Droplets className="w-5 h-5 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">
                  SafeLand
                </h1>
                <p className="text-xs text-slate-400 -mt-1">Flood Risk Assessment</p>
              </div>
            </motion.div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-6">
              {navItems.map((item) => (
                <motion.a
                  key={item.label}
                  href={item.href}
                  className="flex items-center gap-2 text-slate-400 hover:text-slate-100 transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <item.icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{item.label}</span>
                </motion.a>
              ))}
              
              <motion.a
                href="https://github.com/niyabraham/SafeLand"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 rounded-lg bg-slate-800/50 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Github className="w-4 h-4" />
              </motion.a>
            </div>

            {/* Mobile Menu Button */}
            <motion.button
              className="md:hidden w-10 h-10 rounded-lg bg-slate-800/50 flex items-center justify-center"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              whileTap={{ scale: 0.95 }}
            >
              {isMobileMenuOpen ? (
                <X className="w-5 h-5 text-slate-300" />
              ) : (
                <Menu className="w-5 h-5 text-slate-300" />
              )}
            </motion.button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              className="md:hidden glass-strong border-t border-slate-700/30"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <div className="px-4 py-4 space-y-2">
                {navItems.map((item) => (
                  <a
                    key={item.label}
                    href={item.href}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-800/50 transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </a>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.nav>

      {/* Main Content */}
      <main className="relative z-10 pt-16">
        {/* Hero Section */}
        <section className="min-h-[40vh] flex items-center justify-center px-4 py-16">
          <div className="text-center max-w-3xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
            >
              {/* Badge */}
              <motion.div
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
              >
                <Shield className="w-4 h-4 text-sky-400" />
                <span className="text-sm text-slate-300">AI-Powered Risk Assessment</span>
              </motion.div>

              {/* Title */}
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
                <span className="text-slate-100">Protect Your</span>{' '}
                <span className="bg-gradient-to-r from-sky-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
                  Community
                </span>
              </h1>

              {/* Description */}
              <p className="text-lg text-slate-400 mb-8 max-w-2xl mx-auto leading-relaxed">
                SafeLand uses advanced machine learning to analyze environmental data 
                and predict flood risks. Click anywhere on the map to get instant 
                risk assessments for any location.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <motion.a
                  href="#map"
                  className="flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 text-white font-semibold shadow-lg shadow-sky-500/25"
                  whileHover={{ scale: 1.05, boxShadow: '0 0 40px rgba(56, 189, 248, 0.4)' }}
                  whileTap={{ scale: 0.95 }}
                >
                  <MapIcon className="w-5 h-5" />
                  Explore the Map
                </motion.a>
                
                <motion.a
                  href="#about"
                  className="flex items-center gap-2 px-8 py-4 rounded-xl glass text-slate-300 font-semibold hover:text-white transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Info className="w-5 h-5" />
                  Learn More
                </motion.a>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Map Section */}
        <section id="map" className="px-4 py-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              className="relative h-[600px] lg:h-[700px] rounded-3xl overflow-hidden shadow-2xl"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
            >
              {/* Map Container */}
              <MapComponent
                selectedLocation={selectedLocation}
                riskLevel={riskLevel}
                isLoading={isLoading}
                onLocationSelect={handleLocationSelect}
              />

              {/* Risk Dashboard Overlay */}
              <RiskDashboard
                data={predictionData}
                isOpen={isDashboardOpen}
                onClose={handleCloseDashboard}
              />
            </motion.div>

            {/* Map Instructions */}
            <motion.div
              className="mt-6 flex flex-wrap items-center justify-center gap-4 text-sm text-slate-400"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-500" />
                <span>Low Risk</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-amber-500" />
                <span>Medium Risk</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-rose-600" />
                <span>High Risk</span>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section id="about" className="px-4 py-24">
          <div className="max-w-7xl mx-auto">
            <motion.div
              className="text-center mb-16"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl sm:text-4xl font-bold text-slate-100 mb-4">
                How SafeLand Works
              </h2>
              <p className="text-slate-400 max-w-2xl mx-auto">
                Our AI-powered platform analyzes multiple environmental factors 
                to provide accurate flood risk assessments in real-time.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: MapIcon,
                  title: 'Select Location',
                  description: 'Click anywhere on the interactive map to select a location for risk assessment.',
                  color: 'from-sky-400 to-blue-500',
                },
                {
                  icon: Droplets,
                  title: 'Analyze Data',
                  description: 'Our system analyzes rainfall, elevation, soil moisture, and water levels.',
                  color: 'from-indigo-400 to-purple-500',
                },
                {
                  icon: Shield,
                  title: 'Get Results',
                  description: 'Receive instant flood risk ratings with personalized safety recommendations.',
                  color: 'from-emerald-400 to-teal-500',
                },
              ].map((feature, index) => (
                <motion.div
                  key={feature.title}
                  className="glass rounded-2xl p-8 text-center group hover:scale-105 transition-transform duration-300"
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className={`w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-100 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-slate-400 leading-relaxed">
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="px-4 py-16">
          <div className="max-w-7xl mx-auto">
            <div className="glass rounded-3xl p-8 lg:p-12">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
                {[
                  { value: '99%', label: 'Accuracy Rate' },
                  { value: '50K+', label: 'Locations Analyzed' },
                  { value: '24/7', label: 'Real-time Monitoring' },
                  { value: '<2s', label: 'Response Time' },
                ].map((stat, index) => (
                  <motion.div
                    key={stat.label}
                    className="text-center"
                    initial={{ opacity: 0, scale: 0.9 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <p className="text-3xl lg:text-4xl font-bold bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">
                      {stat.value}
                    </p>
                    <p className="text-slate-400 text-sm mt-1">{stat.label}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800/50 mt-16">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sky-400 to-indigo-500 flex items-center justify-center">
                <Droplets className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-slate-100">SafeLand</span>
            </div>

            {/* Links */}
            <div className="flex items-center gap-6 text-sm text-slate-400">
              <a href="#" className="hover:text-slate-200 transition-colors">Privacy</a>
              <a href="#" className="hover:text-slate-200 transition-colors">Terms</a>
              <a href="#" className="hover:text-slate-200 transition-colors">Contact</a>
            </div>

            {/* Social */}
            <div className="flex items-center gap-3">
              <motion.a
                href="https://github.com/niyabraham/SafeLand" // Updated to your repo
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 rounded-lg bg-slate-800/50 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Github className="w-4 h-4" />
              </motion.a>
              {/* You can remove the Twitter button here if you don't have a project Twitter account, or update its href */}
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-slate-800/50 text-center text-sm text-slate-500">
            {/* Updated the year dynamically */}
            <p>© {new Date().getFullYear()} SafeLand. All rights reserved. Built with React, Tailwind CSS & Framer Motion.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
