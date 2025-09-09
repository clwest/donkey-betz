import { useEffect } from 'react';
import { toast } from 'sonner';
import { OddsToolbar } from '../components/OddsToolbar';
import { OddsTable } from '../components/OddsTable';
import { useOddsStore, useOddsSelectors } from '../../../store/oddsStore';
import type { OddsRow, ToolbarParams } from '../types';
import { 
  DEFAULT_TOOLBAR_PARAMS, 
  DEFAULT_ROWS, 
  STORAGE_KEYS 
} from '../types';

// Generate unique ID for rows
const generateRowId = () => `row-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

export function OddsPage() {
  // Use the dedicated odds store
  const {
    rows,
    params,
    updateRows,
    updateParams,
    addRow,
    clearRows,
  } = useOddsStore();

  const {
    totalRows,
    isLoading,
  } = useOddsSelectors();

  // Initialize data from localStorage or defaults on first load
  useEffect(() => {
    const initializeData = () => {
      try {
        // Load stored rows or use defaults
        const storedRows = localStorage.getItem(STORAGE_KEYS.ROWS_DATA);
        
        if (storedRows) {
          const parsedRows = JSON.parse(storedRows);
          updateRows(parsedRows);
        } else if (rows.length === 0) {
          // Initialize with default rows only if no rows exist
          const initialRows: OddsRow[] = DEFAULT_ROWS.map(row => ({
            ...row,
            id: generateRowId(),
          }));
          updateRows(initialRows);
        }

        // Load stored params or use defaults
        const storedParams = localStorage.getItem(STORAGE_KEYS.TOOLBAR_PARAMS);
        if (storedParams) {
          const parsedParams = JSON.parse(storedParams);
          updateParams(parsedParams);
        } else {
          // Only set defaults if params are not already set
          if (params.winProbability === 0.52 && params.bankroll === 1000 && params.fractionalKelly === 0.25) {
            updateParams(DEFAULT_TOOLBAR_PARAMS);
          }
        }
      } catch (error) {
        console.error('Failed to initialize odds page data:', error);
        toast.error('Failed to load saved data, using defaults');
        
        // Fallback to defaults
        const initialRows: OddsRow[] = DEFAULT_ROWS.map(row => ({
          ...row,
          id: generateRowId(),
        }));
        updateRows(initialRows);
        updateParams(DEFAULT_TOOLBAR_PARAMS);
      }
    };

    initializeData();
  }, []); // Empty dependency array for one-time initialization

  // Save rows to localStorage whenever they change
  useEffect(() => {
    if (rows.length > 0) {
      localStorage.setItem(STORAGE_KEYS.ROWS_DATA, JSON.stringify(rows));
    }
  }, [rows]);

  // Save params to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.TOOLBAR_PARAMS, JSON.stringify(params));
  }, [params]);

  // Handle parameter changes
  const handleParamsChange = (newParams: ToolbarParams) => {
    updateParams(newParams);
  };

  // Handle adding new row
  const handleAddRow = () => {
    addRow();
    toast.success('New row added');
  };

  // Handle clearing all rows
  const handleClearRows = () => {
    if (totalRows === 0) return;
    
    if (window.confirm(`Are you sure you want to clear all ${totalRows} rows? This action cannot be undone.`)) {
      clearRows();
      toast.success('All rows cleared');
    }
  };

  // Handle row changes
  const handleRowsChange = (newRows: OddsRow[]) => {
    updateRows(newRows);
  };

  // Show loading state during initialization
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading odds calculator...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">
          Betting Odds Calculator
        </h1>
        <p className="text-muted-foreground text-lg">
          Analyze betting odds, calculate Kelly stakes, and identify positive EV opportunities
        </p>
      </div>

        {/* Toolbar */}
        <OddsToolbar
          params={params}
          onParamsChange={handleParamsChange}
          onAddRow={handleAddRow}
          onClearRows={handleClearRows}
          rowCount={totalRows}
        />

        {/* Table */}
        <OddsTable
          rows={rows}
          params={params}
          onRowsChange={handleRowsChange}
        />

        {/* Help Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass rounded-xl p-6">
            <h3 className="text-lg font-semibold text-foreground mb-3">How to Use</h3>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>1. Set your bankroll and estimated win probability</p>
              <p>2. Choose your Kelly fraction (0.25 is conservative, 1.0 is aggressive)</p>
              <p>3. Enter odds from different sportsbooks</p>
              <p>4. Review EV and stake recommendations</p>
              <p>5. Focus on positive EV opportunities</p>
            </div>
          </div>

          <div className="glass rounded-xl p-6">
            <h3 className="text-lg font-semibold text-foreground mb-3">Understanding the Results</h3>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p><strong>EV (Expected Value):</strong> Profit expectation per $100 bet</p>
              <p><strong>Kelly %:</strong> Optimal bet size as percentage of bankroll</p>
              <p><strong>Recommended Stake:</strong> Dollar amount based on fractional Kelly</p>
              <p><strong>Negative Kelly:</strong> Indicates -EV bet, recommendation is $0</p>
              <p><strong>High Kelly:</strong> Warning for stakes over 10% of bankroll</p>
            </div>
          </div>
        </div>
    </div>
  );
}