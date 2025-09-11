import { useState } from 'react';
import { EnhancedButton } from './enhanced-button';
import { EnhancedCard, CardHeader, CardTitle, CardContent, StatsCard } from './enhanced-card';
import { EnhancedInput, SearchInput } from './enhanced-input';
import { 
  SparklesIcon, 
  HeartIcon, 
  ChartBarIcon,
  MagnifyingGlassIcon 
} from '@heroicons/react/24/outline';

/**
 * Design System Style Guide Component
 * 
 * This component showcases all the design system components
 * and serves as living documentation for developers
 */

export function StyleGuide() {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'colors', label: 'Colors' },
    { id: 'typography', label: 'Typography' },
    { id: 'buttons', label: 'Buttons' },
    { id: 'cards', label: 'Cards' },
    { id: 'inputs', label: 'Inputs' },
    { id: 'layouts', label: 'Layouts' },
  ];

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary">
      {/* Header */}
      <header className="bg-bg-secondary border-b border-border-primary px-6 py-4">
        <div className="container mx-auto">
          <h1 className="text-3xl font-bold text-gradient-primary">
            Unified Donkey Betz Design System
          </h1>
          <p className="text-text-secondary mt-2">
            Dark Mode Pro - Component library and style guide
          </p>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-bg-secondary border-b border-border-primary px-6 py-2">
        <div className="container mx-auto">
          <div className="flex space-x-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-primary-500/20 text-primary-400'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="container mx-auto py-8">
        {activeTab === 'overview' && <OverviewSection />}
        {activeTab === 'colors' && <ColorsSection />}
        {activeTab === 'typography' && <TypographySection />}
        {activeTab === 'buttons' && <ButtonsSection />}
        {activeTab === 'cards' && <CardsSection />}
        {activeTab === 'inputs' && <InputsSection />}
        {activeTab === 'layouts' && <LayoutsSection />}
      </main>
    </div>
  );
}

function OverviewSection() {
  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-2xl font-bold mb-4">Design Philosophy</h2>
        <EnhancedCard>
          <CardContent>
            <p className="text-text-secondary leading-relaxed">
              The Dark Mode Pro design system is built for power users who work with complex data 
              and workflows. It emphasizes high contrast, reduced eye strain, and sophisticated 
              interactions while maintaining accessibility standards.
            </p>
          </CardContent>
        </EnhancedCard>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">Key Principles</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <EnhancedCard variant="tech">
            <CardHeader>
              <CardTitle as="h3">Accessibility First</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-text-secondary">
                WCAG 2.1 AA compliant with carefully calibrated contrast ratios and full keyboard navigation.
              </p>
            </CardContent>
          </EnhancedCard>

          <EnhancedCard variant="tech">
            <CardHeader>
              <CardTitle as="h3">Performance Focused</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-text-secondary">
                Hardware-accelerated animations and efficient CSS for smooth interactions.
              </p>
            </CardContent>
          </EnhancedCard>

          <EnhancedCard variant="tech">
            <CardHeader>
              <CardTitle as="h3">Systematic Design</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-text-secondary">
                Consistent spacing, typography, and color scales based on design tokens.
              </p>
            </CardContent>
          </EnhancedCard>
        </div>
      </section>
    </div>
  );
}

function ColorsSection() {
  const colorPalettes = {
    primary: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#a78bfa',
      500: '#8b5cf6',
      600: '#7c3aed',
      700: '#6d28d9',
      800: '#5b21b6',
      900: '#4c1d95',
    },
    background: {
      primary: '#0a0a0b',
      secondary: '#18181b',
      tertiary: '#27272a',
      elevated: '#2d2d30',
    },
    status: {
      success: '#10b981',
      warning: '#f59e0b',
      error: '#f43f5e',
      info: '#06b6d4',
    },
  };

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-2xl font-bold mb-4">Color Palette</h2>
        
        {/* Primary Colors */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">Primary Colors</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(colorPalettes.primary).map(([shade, color]) => (
              <div key={shade} className="space-y-2">
                <div 
                  className="h-20 rounded-lg border border-border-primary"
                  style={{ backgroundColor: color }}
                />
                <div className="text-sm">
                  <div className="font-mono text-xs text-text-muted">primary-{shade}</div>
                  <div className="font-mono text-xs text-text-secondary">{color}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Background Colors */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">Background Colors</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(colorPalettes.background).map(([name, color]) => (
              <div key={name} className="space-y-2">
                <div 
                  className="h-20 rounded-lg border border-border-primary"
                  style={{ backgroundColor: color }}
                />
                <div className="text-sm">
                  <div className="font-mono text-xs text-text-muted">bg-{name}</div>
                  <div className="font-mono text-xs text-text-secondary">{color}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Status Colors */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">Status Colors</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(colorPalettes.status).map(([name, color]) => (
              <div key={name} className="space-y-2">
                <div 
                  className="h-20 rounded-lg border border-border-primary"
                  style={{ backgroundColor: color }}
                />
                <div className="text-sm">
                  <div className="font-mono text-xs text-text-muted">status-{name}</div>
                  <div className="font-mono text-xs text-text-secondary">{color}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function TypographySection() {
  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-2xl font-bold mb-4">Typography Scale</h2>
        <EnhancedCard>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <h1 className="text-5xl font-bold">Heading 1</h1>
              <p className="text-sm text-text-muted font-mono">text-5xl / 48px</p>
            </div>
            <div className="space-y-2">
              <h2 className="text-4xl font-bold">Heading 2</h2>
              <p className="text-sm text-text-muted font-mono">text-4xl / 36px</p>
            </div>
            <div className="space-y-2">
              <h3 className="text-3xl font-bold">Heading 3</h3>
              <p className="text-sm text-text-muted font-mono">text-3xl / 30px</p>
            </div>
            <div className="space-y-2">
              <h4 className="text-2xl font-semibold">Heading 4</h4>
              <p className="text-sm text-text-muted font-mono">text-2xl / 24px</p>
            </div>
            <div className="space-y-2">
              <h5 className="text-xl font-semibold">Heading 5</h5>
              <p className="text-sm text-text-muted font-mono">text-xl / 20px</p>
            </div>
            <div className="space-y-2">
              <h6 className="text-lg font-semibold">Heading 6</h6>
              <p className="text-sm text-text-muted font-mono">text-lg / 18px</p>
            </div>
            <div className="space-y-2">
              <p className="text-base">Body text - Regular paragraph content</p>
              <p className="text-sm text-text-muted font-mono">text-base / 16px</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-text-secondary">Small text - Secondary information</p>
              <p className="text-sm text-text-muted font-mono">text-sm / 14px</p>
            </div>
            <div className="space-y-2">
              <p className="text-xs text-text-muted">Extra small text - Captions and labels</p>
              <p className="text-sm text-text-muted font-mono">text-xs / 12px</p>
            </div>
          </CardContent>
        </EnhancedCard>
      </section>
    </div>
  );
}

function ButtonsSection() {
  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-2xl font-bold mb-4">Button Variants</h2>
        
        <div className="space-y-6">
          {/* Primary Buttons */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Primary Buttons</h3>
            <div className="flex flex-wrap gap-4">
              <EnhancedButton variant="primary" size="sm">Small</EnhancedButton>
              <EnhancedButton variant="primary" size="md">Medium</EnhancedButton>
              <EnhancedButton variant="primary" size="lg">Large</EnhancedButton>
              <EnhancedButton variant="primary" size="xl">Extra Large</EnhancedButton>
            </div>
          </div>

          {/* Secondary Buttons */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Secondary Buttons</h3>
            <div className="flex flex-wrap gap-4">
              <EnhancedButton variant="secondary" size="sm">Small</EnhancedButton>
              <EnhancedButton variant="secondary" size="md">Medium</EnhancedButton>
              <EnhancedButton variant="secondary" size="lg">Large</EnhancedButton>
              <EnhancedButton variant="secondary" size="xl">Extra Large</EnhancedButton>
            </div>
          </div>

          {/* Tech Buttons */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Tech Buttons</h3>
            <div className="flex flex-wrap gap-4">
              <EnhancedButton variant="tech" size="md">Tech Style</EnhancedButton>
              <EnhancedButton variant="tech" size="md" icon={<SparklesIcon className="w-4 h-4" />}>
                With Icon
              </EnhancedButton>
            </div>
          </div>

          {/* Status Buttons */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Status Buttons</h3>
            <div className="flex flex-wrap gap-4">
              <EnhancedButton variant="success">Success</EnhancedButton>
              <EnhancedButton variant="danger">Danger</EnhancedButton>
              <EnhancedButton variant="ghost">Ghost</EnhancedButton>
              <EnhancedButton variant="outline">Outline</EnhancedButton>
            </div>
          </div>

          {/* Button States */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Button States</h3>
            <div className="flex flex-wrap gap-4">
              <EnhancedButton variant="primary">Normal</EnhancedButton>
              <EnhancedButton variant="primary" loading>Loading</EnhancedButton>
              <EnhancedButton variant="primary" disabled>Disabled</EnhancedButton>
              <EnhancedButton variant="primary" icon={<HeartIcon className="w-4 h-4" />}>
                With Icon
              </EnhancedButton>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function CardsSection() {
  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-2xl font-bold mb-4">Card Variants</h2>
        
        <div className="space-y-8">
          {/* Basic Cards */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Basic Cards</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <EnhancedCard variant="default">
                <CardHeader>
                  <CardTitle>Default Card</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-text-secondary">Basic card with default styling.</p>
                </CardContent>
              </EnhancedCard>

              <EnhancedCard variant="elevated">
                <CardHeader>
                  <CardTitle>Elevated Card</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-text-secondary">Card with enhanced shadow.</p>
                </CardContent>
              </EnhancedCard>

              <EnhancedCard variant="interactive">
                <CardHeader>
                  <CardTitle>Interactive Card</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-text-secondary">Clickable card with hover effects.</p>
                </CardContent>
              </EnhancedCard>
            </div>
          </div>

          {/* Tech Cards */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Tech Cards</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <EnhancedCard variant="tech">
                <CardHeader>
                  <CardTitle>Tech Card</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-text-secondary">
                    Advanced card with gradient effects and hover animations.
                  </p>
                </CardContent>
              </EnhancedCard>

              <EnhancedCard variant="glass">
                <CardHeader>
                  <CardTitle>Glass Card</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-text-secondary">
                    Translucent card with glass morphism effect.
                  </p>
                </CardContent>
              </EnhancedCard>
            </div>
          </div>

          {/* Stats Cards */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Stats Cards</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatsCard
                title="Total Revenue"
                value="$24,500"
                description="Last 30 days"
                trend={{ value: "+12%", isPositive: true }}
                icon={<ChartBarIcon className="w-6 h-6" />}
              />

              <StatsCard
                title="Active Users"
                value="1,234"
                description="Current month"
                trend={{ value: "-3%", isPositive: false }}
                icon={<SparklesIcon className="w-6 h-6" />}
              />

              <StatsCard
                title="Conversion Rate"
                value="3.4%"
                description="This quarter"
                icon={<HeartIcon className="w-6 h-6" />}
              />
            </div>
          </div>

          {/* Status Cards */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Status Cards</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <EnhancedCard variant="status" status="success">
                <CardHeader>
                  <CardTitle>Success Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-text-secondary">Card with success status indicator.</p>
                </CardContent>
              </EnhancedCard>

              <EnhancedCard variant="status" status="error">
                <CardHeader>
                  <CardTitle>Error Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-text-secondary">Card with error status indicator.</p>
                </CardContent>
              </EnhancedCard>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function InputsSection() {
  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-2xl font-bold mb-4">Input Components</h2>
        
        <div className="space-y-8">
          {/* Basic Inputs */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Basic Inputs</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <EnhancedInput
                label="Default Input"
                placeholder="Enter text..."
                helper="This is helper text"
              />

              <EnhancedInput
                label="Required Field"
                placeholder="Required field..."
                required
              />

              <EnhancedInput
                label="Success State"
                placeholder="Valid input..."
                success="Input is valid"
                defaultValue="Valid input"
              />

              <EnhancedInput
                label="Error State"
                placeholder="Invalid input..."
                error="This field is required"
              />
            </div>
          </div>

          {/* Input Variants */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Input Variants</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <EnhancedInput
                variant="default"
                label="Default Variant"
                placeholder="Default style..."
              />

              <EnhancedInput
                variant="filled"
                label="Filled Variant"
                placeholder="Filled style..."
              />

              <EnhancedInput
                variant="tech"
                label="Tech Variant"
                placeholder="Tech style..."
              />
            </div>
          </div>

          {/* Input Sizes */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Input Sizes</h3>
            <div className="space-y-4">
              <EnhancedInput
                size="sm"
                label="Small Input"
                placeholder="Small size..."
              />

              <EnhancedInput
                size="md"
                label="Medium Input"
                placeholder="Medium size..."
              />

              <EnhancedInput
                size="lg"
                label="Large Input"
                placeholder="Large size..."
              />
            </div>
          </div>

          {/* Special Inputs */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Special Inputs</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <EnhancedInput
                type="password"
                label="Password Input"
                placeholder="Enter password..."
              />

              <SearchInput
                label="Search Input"
                placeholder="Search..."
                onSearch={(value) => console.log('Search:', value)}
              />

              <EnhancedInput
                label="With Prefix Icon"
                placeholder="Search..."
                prefixIcon={<MagnifyingGlassIcon className="w-5 h-5" />}
              />

              <EnhancedInput
                label="Loading State"
                placeholder="Processing..."
                loading
              />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function LayoutsSection() {
  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-2xl font-bold mb-4">Layout System</h2>
        
        <div className="space-y-8">
          {/* Grid System */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Responsive Grid</h3>
            <EnhancedCard>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[1, 2, 3, 4, 5, 6].map((num) => (
                    <div
                      key={num}
                      className="bg-bg-tertiary p-4 rounded-lg text-center border border-border-primary"
                    >
                      Grid Item {num}
                    </div>
                  ))}
                </div>
              </CardContent>
            </EnhancedCard>
          </div>

          {/* Spacing Scale */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Spacing Scale</h3>
            <EnhancedCard>
              <CardContent>
                <div className="space-y-4">
                  {[1, 2, 3, 4, 6, 8, 12, 16].map((space) => (
                    <div key={space} className="flex items-center gap-4">
                      <div className="w-16 text-sm font-mono text-text-muted">
                        space-{space}
                      </div>
                      <div
                        className="bg-primary-500 h-4 rounded"
                        style={{ width: `${space * 4}px` }}
                      />
                      <div className="text-sm text-text-secondary">
                        {space * 4}px
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </EnhancedCard>
          </div>

          {/* Container Sizes */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Container Sizes</h3>
            <EnhancedCard>
              <CardContent>
                <div className="space-y-4 text-sm">
                  <div className="grid grid-cols-3 gap-4 font-semibold border-b border-border-primary pb-2">
                    <div>Breakpoint</div>
                    <div>Size</div>
                    <div>Max Width</div>
                  </div>
                  
                  {[
                    { name: 'sm', size: '640px', max: '640px' },
                    { name: 'md', size: '768px', max: '768px' },
                    { name: 'lg', size: '1024px', max: '1024px' },
                    { name: 'xl', size: '1280px', max: '1280px' },
                    { name: '2xl', size: '1536px', max: '1536px' },
                  ].map((container) => (
                    <div key={container.name} className="grid grid-cols-3 gap-4">
                      <div className="font-mono text-text-muted">{container.name}</div>
                      <div className="text-text-secondary">{container.size}</div>
                      <div className="text-text-secondary">{container.max}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </EnhancedCard>
          </div>
        </div>
      </section>
    </div>
  );
}

export default StyleGuide;