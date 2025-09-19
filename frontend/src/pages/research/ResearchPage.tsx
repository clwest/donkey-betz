import { ResearchBooks } from '../../components/features/research-books/ResearchBooks';

export function ResearchPage() {
  return (
    <div className="space-y-8" style={{ backgroundColor: 'hsl(var(--muted))', minHeight: '100vh' }}>
      {/* Header - Gaming Style */}
      <div className="bg-card p-6">
        <div className="bg-card"></div>
        <div className="relative z-10">
          <h1 className="text-4xl font-black font-mono uppercase tracking-wider" 
              style={{ 
                color: 'hsl(var(--muted))',
                textShadow: '0 0 20px rgba(0, 255, 255, 0.5)'
              }}>NEURAL RESEARCH MATRIX</h1>
          <p className="mt-3 font-mono" style={{ color: 'hsl(var(--muted))' }}>
            TRANSFORM RESEARCH SOURCES INTO COMPREHENSIVE NEURAL KNOWLEDGE ARCHIVES
          </p>
        </div>
      </div>
      
      <ResearchBooks />
    </div>
  );
}