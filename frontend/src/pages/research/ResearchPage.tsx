import { ResearchBooks } from '../../components/features/research-books/ResearchBooks';

export function ResearchPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Research & Books</h1>
        <p className="text-gray-400 mt-1">
          Transform research sources into comprehensive books with AI-powered writing and citations
        </p>
      </div>
      
      <ResearchBooks />
    </div>
  );
}