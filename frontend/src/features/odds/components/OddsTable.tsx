import { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from '../../../components/ui/table';
import { LoadingSpinner } from '../../../components/common/LoadingSpinner';
import { TrashIcon } from '@heroicons/react/24/outline';
import { toast } from 'sonner';
import type { OddsRow, ToolbarParams } from '../types';
import { 
  convertAmericanToDecimal, 
  computeKelly, 
  isValidAmericanOdds,
  formatAmericanOdds,
  formatPercentage,
  formatCurrency
} from '../api/odds';

interface OddsTableProps {
  rows: OddsRow[];
  params: ToolbarParams;
  onRowsChange: (rows: OddsRow[]) => void;
}

// Debounce utility
function useDebounce<T extends any[]>(
  callback: (...args: T) => void,
  delay: number,
  deps: any[]
) {
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const debouncedCallback = useCallback((...args: T) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  }, [callback, delay, ...deps]);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  return debouncedCallback;
}

export function OddsTable({ rows, params, onRowsChange }: OddsTableProps) {
  // Create stable refs for parameters to avoid recreating debounced function
  const paramsRef = useRef(params);
  paramsRef.current = params;
  
  const onRowsChangeRef = useRef(onRowsChange);
  onRowsChangeRef.current = onRowsChange;

  // Track previous parameters to avoid unnecessary recalculations
  const prevParamsRef = useRef(params);

  // Debounced API call function using the direct odds API
  const debouncedCalculateOdds = useDebounce(
    async (rowId: string, american: number | string) => {
      if (!isValidAmericanOdds(american)) {
        const updatedRows = rows.map(row => 
          row.id === rowId ? { ...row, error: 'Invalid odds format' } : row
        );
        onRowsChangeRef.current(updatedRows);
        return;
      }

      try {
        // Set loading state
        let updatedRows = rows.map(row => 
          row.id === rowId ? { ...row, loading: true, error: null } : row
        );
        onRowsChangeRef.current(updatedRows);

        const currentParams = paramsRef.current;

        // Get conversion data directly from odds API (not orchestra)
        const conversion = await convertAmericanToDecimal(american);
        
        if (!conversion.success || !conversion.result) {
          throw new Error('Failed to convert odds');
        }
        
        // Get Kelly calculation directly from odds API (not orchestra)
        const kelly = await computeKelly(
          american,
          currentParams.winProbability,
          currentParams.bankroll,
          currentParams.fractionalKelly
        );

        if (!kelly.success || !kelly.result) {
          throw new Error('Failed to calculate Kelly criterion');
        }

        // Update row with calculated values
        updatedRows = rows.map(row => 
          row.id === rowId ? {
            ...row,
            decimal: conversion.result!.decimal,
            implied: conversion.result!.implied_probability,
            ev: kelly.result!.edge * 100, // Convert edge to percentage for EV
            kelly: kelly.result!.kelly_percentage,
            stake: kelly.result!.recommended_stake,
            notes: kelly.result!.warnings,
            loading: false,
            error: null
          } : row
        );
        onRowsChangeRef.current(updatedRows);

      } catch (error) {
        const message = error instanceof Error ? error.message : 'Calculation failed';
        console.error(`[OddsTable] Calculation error for row ${rowId}:`, message);
        const updatedRows = rows.map(row => 
          row.id === rowId ? { ...row, loading: false, error: 'Calculation failed' } : row
        );
        onRowsChangeRef.current(updatedRows);
      }
    },
    250, // 250ms debounce
    [] // Empty deps array to prevent recreation
  );


  // Handle field updates
  const updateRowField = (rowId: string, field: keyof OddsRow, value: any) => {
    const updatedRows = rows.map(row => 
      row.id === rowId ? { ...row, [field]: value } : row
    );
    onRowsChange(updatedRows);

    // Trigger calculation if odds changed
    if (field === 'american' && value !== '') {
      debouncedCalculateOdds(rowId, value);
    }
  };

  const deleteRow = (rowId: string) => {
    onRowsChange(rows.filter(row => row.id !== rowId));
  };

  // Recalculate all rows when parameters change
  useEffect(() => {
    const prevParams = prevParamsRef.current;
    const hasParamsChanged = 
      prevParams.winProbability !== params.winProbability ||
      prevParams.bankroll !== params.bankroll ||
      prevParams.fractionalKelly !== params.fractionalKelly;

    if (hasParamsChanged) {
      rows.forEach(row => {
        if (isValidAmericanOdds(row.american)) {
          debouncedCalculateOdds(row.id, row.american);
        }
      });
      prevParamsRef.current = params;
    }
  }, [params.winProbability, params.bankroll, params.fractionalKelly, rows]);

  const renderEVBadge = (ev?: number) => {
    if (ev === undefined) return null;
    
    const isPositive = ev > 0;
    return (
      <Badge 
        variant={isPositive ? 'success' : 'error'} 
        size="sm"
      >
        {ev > 0 ? '+' : ''}{ev.toFixed(2)}%
      </Badge>
    );
  };

  const renderStake = (stake?: number, kelly?: number) => {
    if (stake === undefined || kelly === undefined) return '—';
    
    // If negative Kelly, show no bet warning
    if (kelly < 0) {
      return (
        <div className="flex items-center gap-2">
          <span className="text-red-400">$0.00</span>
          <Badge variant="warning" size="sm">No Bet</Badge>
        </div>
      );
    }
    
    return (
      <div className="flex items-center gap-2">
        <span className="text-green-400 font-medium">{formatCurrency(stake)}</span>
        {kelly > 0.1 && (
          <Badge variant="warning" size="sm">High Kelly</Badge>
        )}
      </div>
    );
  };

  if (rows.length === 0) {
    return (
      <Card className="py-12 text-center">
        <CardContent>
          <div className="text-gray-400">
            <p className="text-lg font-medium">No betting rows</p>
            <p className="text-sm mt-2">Click "Add Row" to start analyzing odds</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="text-xs font-medium uppercase tracking-wider">Book</TableHead>
              <TableHead className="text-xs font-medium uppercase tracking-wider">Market</TableHead>
              <TableHead className="text-xs font-medium uppercase tracking-wider">American Odds</TableHead>
              <TableHead className="text-xs font-medium uppercase tracking-wider">Decimal</TableHead>
              <TableHead className="text-xs font-medium uppercase tracking-wider">Implied Prob</TableHead>
              <TableHead className="text-xs font-medium uppercase tracking-wider">EV</TableHead>
              <TableHead className="text-xs font-medium uppercase tracking-wider">Kelly %</TableHead>
              <TableHead className="text-xs font-medium uppercase tracking-wider">Recommended Stake</TableHead>
              <TableHead className="text-xs font-medium uppercase tracking-wider">Notes</TableHead>
              <TableHead className="text-right text-xs font-medium uppercase tracking-wider">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id}>
                {/* Book */}
                <TableCell>
                  <input
                    type="text"
                    value={row.book}
                    onChange={(e) => updateRowField(row.id, 'book', e.target.value)}
                    className="w-full bg-transparent text-white text-sm focus:outline-none focus:ring-1 focus:ring-primary-500 rounded px-2 py-1"
                    placeholder="Sportsbook"
                  />
                </TableCell>

                {/* Market */}
                <TableCell>
                  <input
                    type="text"
                    value={row.market}
                    onChange={(e) => updateRowField(row.id, 'market', e.target.value)}
                    className="w-full bg-transparent text-white text-sm focus:outline-none focus:ring-1 focus:ring-primary-500 rounded px-2 py-1"
                    placeholder="e.g., Team A ML"
                  />
                </TableCell>

                {/* American Odds */}
                <TableCell>
                  <div className="relative">
                    <input
                      type="text"
                      value={row.american}
                      onChange={(e) => updateRowField(row.id, 'american', e.target.value)}
                      className={`w-full bg-transparent text-white text-sm focus:outline-none focus:ring-1 rounded px-2 py-1 ${
                        row.error ? 'focus:ring-red-500 ring-1 ring-red-500' : 'focus:ring-primary-500'
                      }`}
                      placeholder="+110 or -135"
                    />
                    {row.loading && (
                      <div className="absolute right-2 top-1/2 -translate-y-1/2">
                        <LoadingSpinner size="sm" />
                      </div>
                    )}
                  </div>
                  {row.error && (
                    <p className="text-red-400 text-xs mt-1">{row.error}</p>
                  )}
                </TableCell>

                {/* Decimal */}
                <TableCell className="text-sm">
                  {row.decimal ? row.decimal.toFixed(2) : '—'}
                </TableCell>

                {/* Implied Probability */}
                <TableCell className="text-sm">
                  {row.implied ? formatPercentage(row.implied) : '—'}
                </TableCell>

                {/* EV */}
                <TableCell>
                  {renderEVBadge(row.ev)}
                </TableCell>

                {/* Kelly % */}
                <TableCell className="text-sm">
                  {row.kelly !== undefined ? formatPercentage(row.kelly) : '—'}
                </TableCell>

                {/* Recommended Stake */}
                <TableCell>
                  {renderStake(row.stake, row.kelly)}
                </TableCell>

                {/* Notes */}
                <TableCell>
                  {row.notes && row.notes.length > 0 && (
                    <div className="space-y-1">
                      {row.notes.slice(0, 2).map((note, index) => (
                        <Badge key={index} variant="warning" size="sm">
                          {note.length > 20 ? `${note.substring(0, 20)}...` : note}
                        </Badge>
                      ))}
                      {row.notes.length > 2 && (
                        <Badge variant="info" size="sm">
                          +{row.notes.length - 2} more
                        </Badge>
                      )}
                    </div>
                  )}
                </TableCell>

                {/* Actions */}
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteRow(row.id)}
                    className="text-gray-400 hover:text-red-400 transition-colors"
                    title="Delete row"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        
        {/* Summary */}
        <div className="px-4 py-3 border-t border-dark-700 bg-dark-700/30">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <span>
              {rows.length} row{rows.length !== 1 ? 's' : ''} • {rows.filter(r => (r.ev || 0) > 0).length} positive EV opportunities
            </span>
            <span>
              Total Recommended Stakes: {formatCurrency(
                rows.reduce((sum, row) => sum + (row.stake && (row.kelly || 0) >= 0 ? row.stake : 0), 0)
              )}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}