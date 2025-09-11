import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '../../../components/common/Card';
import { Button } from '../../../components/common/Button';
import { Badge } from '../../../components/common/Badge';
import { GameCard } from './GameCard';
import { GamingGameCard } from './GamingGameCard';
import { Gamepad2, Palette, ArrowRight } from 'lucide-react';
import type { GameData, ToolbarParams } from '../types';

// Demo data for showcasing the themes
const demoGame: GameData = {
  id: 'demo-game-1',
  league: 'NFL',
  away_team: 'Kansas City Chiefs',
  home_team: 'Buffalo Bills', 
  game_date: new Date().toISOString(),
  status: 'live',
  venue: 'Highmark Stadium',
  moneylines: [
    {
      id: 'ml-1',
      team: 'Kansas City Chiefs',
      side: 'away',
      odds_american: 130,
      implied_probability: 0.435,
      kelly_percentage: 0.08,
      recommended_stake: 320,
      edge: 0.045,
    },
    {
      id: 'ml-2', 
      team: 'Buffalo Bills',
      side: 'home',
      odds_american: -150,
      implied_probability: 0.600,
      kelly_percentage: 0.12,
      recommended_stake: 480,
      edge: 0.072,
    }
  ]
};

const demoParams: ToolbarParams = {
  bankroll: 4000,
  winPercentage: 58,
  fractionalKelly: 0.5,
  selectedLeague: 'NFL',
  selectedDate: new Date().toISOString().split('T')[0],
};

export function ThemeDemo() {
  const [selectedTheme, setSelectedTheme] = useState<'classic' | 'gaming'>('classic');

  return (
    <Card className="border-t-4 border-t-primary-500">
      <div className="p-6 border-b border-dark-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Palette className="w-6 h-6 text-primary-400" />
            <span className="text-xl text-white">Theme Comparison</span>
            <Badge variant="secondary" className="ml-2">
              Live Demo
            </Badge>
          </div>
          
          {/* Theme Selector */}
          <div className="flex items-center space-x-2">
            <Button
              onClick={() => setSelectedTheme('classic')}
              variant={selectedTheme === 'classic' ? 'primary' : 'secondary'}
              size="sm"
            >
              <Palette className="w-4 h-4 mr-2" />
              Classic
            </Button>
            <Button
              onClick={() => setSelectedTheme('gaming')}
              variant={selectedTheme === 'gaming' ? 'primary' : 'secondary'}
              size="sm"
              className={selectedTheme === 'gaming' ? 'gaming-btn-active' : ''}
            >
              <Gamepad2 className="w-4 h-4 mr-2" />
              Gaming
            </Button>
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="space-y-6">
          {/* Theme Description */}
          <div className="text-center space-y-2">
            <h3 className="text-lg font-semibold text-white">
              {selectedTheme === 'gaming' ? '🎮 Gaming/Esports Theme' : '🎨 Classic Theme'}
            </h3>
            <p className="text-gray-400 max-w-2xl mx-auto">
              {selectedTheme === 'gaming' 
                ? 'Experience the thrill with neon accents, cyberpunk aesthetics, pulsing animations, and gaming-inspired design elements that bring excitement to every bet.'
                : 'Clean, professional interface with subtle shadows, perfect typography hierarchy, and minimal distractions for focused betting decisions.'
              }
            </p>
          </div>

          {/* Live Demo Card */}
          <div className="max-w-md mx-auto">
            <motion.div
              key={selectedTheme}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              {selectedTheme === 'gaming' ? (
                <GamingGameCard 
                  game={demoGame}
                  params={demoParams}
                  className="w-full"
                />
              ) : (
                <GameCard 
                  game={demoGame}
                  params={demoParams} 
                  className="w-full"
                />
              )}
            </motion.div>
          </div>

          {/* Theme Features */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <Card className="p-4">
              <h4 className="font-semibold text-white mb-3">
                {selectedTheme === 'gaming' ? '🎮 Gaming Features' : '🎨 Classic Features'}
              </h4>
              <ul className="space-y-2 text-sm text-gray-300">
                {selectedTheme === 'gaming' ? (
                  <>
                    <li>• Neon glow effects and cyberpunk colors</li>
                    <li>• Pulsing animations for live games</li>
                    <li>• Gaming-inspired typography</li>
                    <li>• Electric border animations</li>
                    <li>• Matrix-style progress bars</li>
                  </>
                ) : (
                  <>
                    <li>• Clean, minimal design language</li>
                    <li>• Professional color palette</li>
                    <li>• Subtle hover interactions</li>
                    <li>• Focus on data clarity</li>
                    <li>• Consistent spacing system</li>
                  </>
                )}
              </ul>
            </Card>

            <Card className="p-4">
              <h4 className="font-semibold text-white mb-3">Best For</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                {selectedTheme === 'gaming' ? (
                  <>
                    <li>• Esports and gaming audiences</li>
                    <li>• Users who want excitement</li>
                    <li>• Modern, bold brand identity</li>
                    <li>• Social betting experiences</li>
                    <li>• Younger demographics</li>
                  </>
                ) : (
                  <>
                    <li>• Professional bettors</li>
                    <li>• Data-focused analysis</li>
                    <li>• Corporate environments</li>
                    <li>• Minimal distraction needs</li>
                    <li>• Traditional audiences</li>
                  </>
                )}
              </ul>
            </Card>
          </div>

          {/* Call to Action */}
          <div className="text-center">
            <div className="inline-flex items-center space-x-3 bg-primary-500/10 px-6 py-3 rounded-lg">
              <span className="text-white font-medium">
                Switch between themes using the toggle in the header
              </span>
              <ArrowRight className="w-4 h-4 text-primary-400" />
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}