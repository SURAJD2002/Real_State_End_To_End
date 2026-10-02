import { useState, useCallback } from 'react';
import { Coordinate } from './cadGeometry';

export interface HistoryEntry {
  coordinates: Coordinate[];
  description: string;
  timestamp: number;
}

const MAX_HISTORY_LENGTH = 50;

export function useCadHistory(initialCoordinates: Coordinate[] = []) {
  const [history, setHistory] = useState<HistoryEntry[]>([
    {
      coordinates: initialCoordinates,
      description: 'Initial State',
      timestamp: Date.now()
    }
  ]);
  const [currentIndex, setCurrentIndex] = useState(0);

  /**
   * Pushes a new coordinate state onto the history stack
   */
  const recordAction = useCallback((nextCoords: Coordinate[], description: string) => {
    setHistory((prev) => {
      // Discard future states if we performed an action while navigated back
      const truncated = prev.slice(0, currentIndex + 1);
      const newEntry: HistoryEntry = {
        coordinates: nextCoords.map((c) => [...c] as Coordinate),
        description,
        timestamp: Date.now()
      };
      const updated = [...truncated, newEntry];
      if (updated.length > MAX_HISTORY_LENGTH) {
        return updated.slice(updated.length - MAX_HISTORY_LENGTH);
      }
      return updated;
    });
    setCurrentIndex((prev) => Math.min(prev + 1, MAX_HISTORY_LENGTH - 1));
  }, [currentIndex]);

  /**
   * Undo to the previous geometry state
   */
  const undo = useCallback((): Coordinate[] | null => {
    if (currentIndex <= 0) return null;
    const targetIdx = currentIndex - 1;
    setCurrentIndex(targetIdx);
    return history[targetIdx].coordinates;
  }, [currentIndex, history]);

  /**
   * Redo to the next geometry state
   */
  const redo = useCallback((): Coordinate[] | null => {
    if (currentIndex >= history.length - 1) return null;
    const targetIdx = currentIndex + 1;
    setCurrentIndex(targetIdx);
    return history[targetIdx].coordinates;
  }, [currentIndex, history]);

  /**
   * Resets history with a clean slate
   */
  const resetHistory = useCallback((coords: Coordinate[], description: string = 'Reset') => {
    setHistory([
      {
        coordinates: coords.map((c) => [...c] as Coordinate),
        description,
        timestamp: Date.now()
      }
    ]);
    setCurrentIndex(0);
  }, []);

  return {
    recordAction,
    undo,
    redo,
    resetHistory,
    canUndo: currentIndex > 0,
    canRedo: currentIndex < history.length - 1,
    currentAction: history[currentIndex]?.description || 'Ready',
    historyCount: history.length,
    currentIndex
  };
}
