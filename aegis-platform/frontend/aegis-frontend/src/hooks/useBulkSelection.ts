import { useState, useCallback, useMemo } from 'react';

export interface BulkSelectionHookProps<T> {
  items: T[];
  getItemId: (item: T) => string | number;
  onSelectionChange?: (selectedItems: T[], selectedIds: Set<string | number>) => void;
}

export function useBulkSelection<T>({
  items,
  getItemId,
  onSelectionChange,
}: BulkSelectionHookProps<T>) {
  const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set());

  const selectedItems = useMemo(() => {
    return items.filter(item => selectedIds.has(getItemId(item)));
  }, [items, selectedIds, getItemId]);

  const isAllSelected = useMemo(() => {
    return items.length > 0 && selectedIds.size === items.length;
  }, [items.length, selectedIds.size]);

  const isIndeterminate = useMemo(() => {
    return selectedIds.size > 0 && selectedIds.size < items.length;
  }, [selectedIds.size, items.length]);

  const selectItem = useCallback((itemId: string | number) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      newSet.add(itemId);
      
      if (onSelectionChange) {
        const newSelectedItems = items.filter(item => 
          newSet.has(getItemId(item))
        );
        onSelectionChange(newSelectedItems, newSet);
      }
      
      return newSet;
    });
  }, [items, getItemId, onSelectionChange]);

  const deselectItem = useCallback((itemId: string | number) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      newSet.delete(itemId);
      
      if (onSelectionChange) {
        const newSelectedItems = items.filter(item => 
          newSet.has(getItemId(item))
        );
        onSelectionChange(newSelectedItems, newSet);
      }
      
      return newSet;
    });
  }, [items, getItemId, onSelectionChange]);

  const toggleItem = useCallback((itemId: string | number) => {
    if (selectedIds.has(itemId)) {
      deselectItem(itemId);
    } else {
      selectItem(itemId);
    }
  }, [selectedIds, selectItem, deselectItem]);

  const selectAll = useCallback(() => {
    const allIds = new Set(items.map(getItemId));
    setSelectedIds(allIds);
    
    if (onSelectionChange) {
      onSelectionChange(items, allIds);
    }
  }, [items, getItemId, onSelectionChange]);

  const deselectAll = useCallback(() => {
    setSelectedIds(new Set());
    
    if (onSelectionChange) {
      onSelectionChange([], new Set());
    }
  }, [onSelectionChange]);

  const toggleAll = useCallback(() => {
    if (isAllSelected) {
      deselectAll();
    } else {
      selectAll();
    }
  }, [isAllSelected, selectAll, deselectAll]);

  const selectRange = useCallback((startIndex: number, endIndex: number) => {
    const start = Math.min(startIndex, endIndex);
    const end = Math.max(startIndex, endIndex);
    const rangeItems = items.slice(start, end + 1);
    const rangeIds = rangeItems.map(getItemId);
    
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      rangeIds.forEach(id => newSet.add(id));
      
      if (onSelectionChange) {
        const newSelectedItems = items.filter(item => 
          newSet.has(getItemId(item))
        );
        onSelectionChange(newSelectedItems, newSet);
      }
      
      return newSet;
    });
  }, [items, getItemId, onSelectionChange]);

  const isItemSelected = useCallback((itemId: string | number) => {
    return selectedIds.has(itemId);
  }, [selectedIds]);

  const getSelectedCount = useCallback(() => {
    return selectedIds.size;
  }, [selectedIds.size]);

  const reset = useCallback(() => {
    setSelectedIds(new Set());
    if (onSelectionChange) {
      onSelectionChange([], new Set());
    }
  }, [onSelectionChange]);

  return {
    selectedIds,
    selectedItems,
    isAllSelected,
    isIndeterminate,
    selectedCount: selectedIds.size,
    selectItem,
    deselectItem,
    toggleItem,
    selectAll,
    deselectAll,
    toggleAll,
    selectRange,
    isItemSelected,
    getSelectedCount,
    reset,
  };
}