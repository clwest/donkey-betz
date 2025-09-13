/**
 * Date formatting utilities for MST/MDT timezone
 * All dates are displayed in Mountain Time (Denver timezone)
 */

/**
 * Format a date string to MST/MDT with full date and time
 */
export const formatDateMST = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    timeZone: 'America/Denver',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
};

/**
 * Format a date string to MST/MDT - date only
 */
export const formatDateOnlyMST = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    timeZone: 'America/Denver',
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};

/**
 * Format a date string to MST/MDT - time only
 */
export const formatTimeOnlyMST = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    timeZone: 'America/Denver',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
};

/**
 * Check if a date is today in MST/MDT
 */
export const isTodayMST = (dateString: string): boolean => {
  const date = new Date(dateString);
  const today = new Date();
  
  // Convert both to MST/MDT for comparison
  const dateMST = date.toLocaleDateString('en-US', { timeZone: 'America/Denver' });
  const todayMST = today.toLocaleDateString('en-US', { timeZone: 'America/Denver' });
  
  return dateMST === todayMST;
};

/**
 * Check if a date is tomorrow in MST/MDT
 */
export const isTomorrowMST = (dateString: string): boolean => {
  const date = new Date(dateString);
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  
  // Convert both to MST/MDT for comparison
  const dateMST = date.toLocaleDateString('en-US', { timeZone: 'America/Denver' });
  const tomorrowMST = tomorrow.toLocaleDateString('en-US', { timeZone: 'America/Denver' });
  
  return dateMST === tomorrowMST;
};

/**
 * Format game time with relative day (Today, Tomorrow, or date)
 */
export const formatGameTime = (dateString: string): { day: string; time: string } => {
  const isToday = isTodayMST(dateString);
  const isTomorrow = isTomorrowMST(dateString);
  
  let day: string;
  if (isToday) {
    day = 'Today';
  } else if (isTomorrow) {
    day = 'Tomorrow';
  } else {
    const date = new Date(dateString);
    day = date.toLocaleDateString('en-US', {
      timeZone: 'America/Denver',
      month: 'short',
      day: 'numeric'
    });
  }
  
  const time = formatTimeOnlyMST(dateString);
  
  return { day, time };
};

/**
 * Get the current time in MST/MDT
 */
export const getCurrentTimeMST = (): string => {
  return new Date().toLocaleString('en-US', {
    timeZone: 'America/Denver',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  });
};