import React, { useState, useCallback } from 'react';

export interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: 'default' | 'destructive' | 'success' | 'warning';
  duration?: number;
}

type ToastActionFunction = (toast: Omit<Toast, 'id' | 'variant'>) => void;

interface UseToastReturn {
  toasts: Toast[];
  toast: (toast: Omit<Toast, 'id'>) => void;
  success: ToastActionFunction;
  error: ToastActionFunction;
  warning: ToastActionFunction;
  info: ToastActionFunction;
  dismiss: (id: string) => void;
}

const TOAST_LIMIT = 3;
const TOAST_REMOVE_DELAY = 1000000;

let count = 0;

function genId() {
  count = (count + 1) % Number.MAX_VALUE;
  return count.toString();
}

let toasts: Toast[] = [];
const listeners: Array<(toasts: Toast[]) => void> = [];

function addToast(toast: Omit<Toast, 'id'>) {
  const id = genId();
  const newToast = { ...toast, id };

  toasts = [newToast, ...toasts].slice(0, TOAST_LIMIT);
  listeners.forEach((listener) => listener(toasts));

  if (toast.duration !== Infinity) {
    setTimeout(() => dismissToast(id), toast.duration || 5000);
  }

  return id;
}

function dismissToast(id: string) {
  toasts = toasts.filter((toast) => toast.id !== id);
  listeners.forEach((listener) => listener(toasts));
}

function subscribe(listener: (toasts: Toast[]) => void) {
  listeners.push(listener);
  return () => {
    const index = listeners.indexOf(listener);
    if (index > -1) {
      listeners.splice(index, 1);
    }
  };
}

export function useToast(): UseToastReturn {
  const [state, setState] = useState<Toast[]>(toasts);

  const toast = useCallback((toast: Omit<Toast, 'id'>) => {
    return addToast(toast);
  }, []);

  const success = useCallback((toast: Omit<Toast, 'id' | 'variant'>) => {
    return addToast({ ...toast, variant: 'success' });
  }, []);

  const error = useCallback((toast: Omit<Toast, 'id' | 'variant'>) => {
    return addToast({ ...toast, variant: 'destructive' });
  }, []);

  const warning = useCallback((toast: Omit<Toast, 'id' | 'variant'>) => {
    return addToast({ ...toast, variant: 'warning' });
  }, []);

  const info = useCallback((toast: Omit<Toast, 'id' | 'variant'>) => {
    return addToast({ ...toast, variant: 'default' });
  }, []);

  const dismiss = useCallback((id: string) => {
    dismissToast(id);
  }, []);

  // Subscribe to toast changes
  React.useEffect(() => {
    return subscribe((newToasts) => {
      setState(newToasts);
    });
  }, []);

  return {
    toasts: state,
    toast,
    success,
    error,
    warning,
    info,
    dismiss,
  };
}

// Utility function for API error handling
export function handleApiError(error: any, toastFn: UseToastReturn['error']) {
  console.error('API Error:', error);
  
  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const message = error.response.data?.message || error.response.statusText || 'An error occurred';
    
    toastFn({
      title: `Error ${status}`,
      description: message
    });
  } else if (error.request) {
    // Network error
    toastFn({
      title: 'Connection Error',
      description: 'Unable to connect to the server. Please check your internet connection.'
    });
  } else {
    // Other error
    toastFn({
      title: 'Unexpected Error',
      description: error.message || 'An unexpected error occurred'
    });
  }
}