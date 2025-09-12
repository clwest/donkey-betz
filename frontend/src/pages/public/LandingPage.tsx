import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { 
  Sparkles, 
  TrendingUp, 
  Brain, 
  Users, 
  FileText, 
  Trophy,
  ArrowRight,
  CheckCircle,
  Zap,
  Shield,
  Globe,
  BarChart3
} from 'lucide-react';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Content',
      description: 'Generate high-quality content with advanced AI models including GPT-5',
      color: 'text-purple-500'
    },
    {
      icon: TrendingUp,
      title: 'Sports Analytics',
      description: 'Real-time odds analysis and intelligent betting recommendations',
      color: 'text-green-500'
    },
    {
      icon: Users,
      title: 'Agent Orchestra',
      description: '100+ specialized AI agents working together for complex tasks',
      color: 'text-blue-500'
    },
    {
      icon: FileText,
      title: 'Smart Research',
      description: 'Automated research with web search, academic papers, and news',
      color: 'text-orange-500'
    },
    {
      icon: Trophy,
      title: 'Betting Intelligence',
      description: 'Kelly Criterion calculations and arbitrage opportunity detection',
      color: 'text-yellow-500'
    },
    {
      icon: Shield,
      title: 'Secure Platform',
      description: 'Enterprise-grade security with encrypted data and secure APIs',
      color: 'text-red-500'
    }
  ];

  const stats = [
    { value: '100+', label: 'AI Agents' },
    { value: '50K+', label: 'Articles Generated' },
    { value: '95%', label: 'Accuracy Rate' },
    { value: '24/7', label: 'Availability' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 backdrop-blur-lg bg-gray-900/70 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-8 w-8 text-purple-500" />
              <span className="text-xl font-bold text-white">Unified Donkey Betz</span>
            </div>
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/blogs')}
                className="text-gray-300 hover:text-white"
              >
                Blog
              </Button>
              <Button 
                variant="ghost" 
                onClick={() => navigate('/api-docs')}
                className="text-gray-300 hover:text-white"
              >
                API Docs
              </Button>
              <Button 
                variant="ghost" 
                onClick={() => navigate('/login')}
                className="text-gray-300 hover:text-white"
              >
                Login
              </Button>
              <Button 
                onClick={() => navigate('/signup')}
                className="bg-purple-600 hover:bg-purple-700"
              >
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 mb-6">
            <Zap className="h-4 w-4 text-purple-400 mr-2" />
            <span className="text-sm text-purple-300">Powered by GPT-5 & Claude</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
            AI-Powered Content & Sports Intelligence
          </h1>
          
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Harness the power of 100+ specialized AI agents for content creation, sports analytics, 
            and intelligent betting strategies. Your all-in-one platform for AI-driven insights.
          </p>
          
          <div className="flex justify-center space-x-4">
            <Button 
              size="lg" 
              onClick={() => navigate('/signup')}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            >
              Start Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              onClick={() => navigate('/demo')}
              className="border-gray-600 text-gray-300 hover:bg-gray-800"
            >
              Watch Demo
            </Button>
          </div>
        </div>

        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 border-y border-gray-800">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">{stat.value}</div>
                <div className="text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Everything You Need in One Platform
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              From content generation to sports analytics, our platform provides comprehensive AI solutions
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card 
                key={index}
                className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-all hover:scale-105 cursor-pointer"
                onClick={() => navigate('/features')}
              >
                <div className="p-6">
                  <feature.icon className={`h-12 w-12 ${feature.color} mb-4`} />
                  <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-400">{feature.description}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-20 px-4 bg-gray-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                Built for Professionals
              </h2>
              <div className="space-y-4">
                {[
                  'Content creators and marketers',
                  'Sports analysts and bettors',
                  'Research teams and academics',
                  'Business intelligence professionals',
                  'Developers and API integrators'
                ].map((item, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                    <span className="text-gray-300">{item}</span>
                  </div>
                ))}
              </div>
              <Button 
                className="mt-8 bg-purple-600 hover:bg-purple-700"
                onClick={() => navigate('/use-cases')}
              >
                Explore Use Cases
              </Button>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <Card className="bg-gradient-to-br from-purple-900/50 to-purple-800/30 border-purple-700">
                <div className="p-6">
                  <Globe className="h-8 w-8 text-purple-400 mb-3" />
                  <h4 className="font-semibold text-white mb-2">Global Reach</h4>
                  <p className="text-sm text-gray-300">Access data from worldwide sources</p>
                </div>
              </Card>
              <Card className="bg-gradient-to-br from-blue-900/50 to-blue-800/30 border-blue-700">
                <div className="p-6">
                  <BarChart3 className="h-8 w-8 text-blue-400 mb-3" />
                  <h4 className="font-semibold text-white mb-2">Real-time Analytics</h4>
                  <p className="text-sm text-gray-300">Live data and instant insights</p>
                </div>
              </Card>
              <Card className="bg-gradient-to-br from-green-900/50 to-green-800/30 border-green-700">
                <div className="p-6">
                  <Shield className="h-8 w-8 text-green-400 mb-3" />
                  <h4 className="font-semibold text-white mb-2">Enterprise Security</h4>
                  <p className="text-sm text-gray-300">Bank-level encryption</p>
                </div>
              </Card>
              <Card className="bg-gradient-to-br from-orange-900/50 to-orange-800/30 border-orange-700">
                <div className="p-6">
                  <Zap className="h-8 w-8 text-orange-400 mb-3" />
                  <h4 className="font-semibold text-white mb-2">Lightning Fast</h4>
                  <p className="text-sm text-gray-300">Optimized for speed</p>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Workflow?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of professionals using AI to accelerate their success
          </p>
          <div className="flex justify-center space-x-4">
            <Button 
              size="lg"
              onClick={() => navigate('/signup')}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            >
              Get Started Free
            </Button>
            <Button 
              size="lg"
              variant="outline"
              onClick={() => navigate('/contact')}
              className="border-gray-600 text-gray-300 hover:bg-gray-800"
            >
              Contact Sales
            </Button>
          </div>
          <p className="mt-4 text-sm text-gray-400">
            No credit card required • 14-day free trial • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Sparkles className="h-6 w-6 text-purple-500" />
                <span className="font-semibold text-white">Unified Donkey Betz</span>
              </div>
              <p className="text-sm text-gray-400">
                AI-powered platform for content creation and sports intelligence
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="/features" className="hover:text-white">Features</a></li>
                <li><a href="/pricing" className="hover:text-white">Pricing</a></li>
                <li><a href="/api-docs" className="hover:text-white">API</a></li>
                <li><a href="/integrations" className="hover:text-white">Integrations</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="/about" className="hover:text-white">About</a></li>
                <li><a href="/blogs" className="hover:text-white">Blog</a></li>
                <li><a href="/careers" className="hover:text-white">Careers</a></li>
                <li><a href="/contact" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="/privacy" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="/terms" className="hover:text-white">Terms of Service</a></li>
                <li><a href="/security" className="hover:text-white">Security</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-gray-800 text-center text-sm text-gray-400">
            © 2025 Unified Donkey Betz. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;