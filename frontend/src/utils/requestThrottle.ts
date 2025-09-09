/**
 * Request Throttle Utility
 * 
 * Provides rate limiting for API requests to avoid 429 errors
 */

interface QueueItem {
  fn: () => Promise<any>;
  resolve: (value: any) => void;
  reject: (error: any) => void;
}

class RequestThrottler {
  private queue: QueueItem[] = [];
  private running = 0;
  private maxConcurrent: number;
  private delayMs: number;
  private lastRequestTime = 0;

  constructor(maxConcurrent = 2, delayMs = 200) {
    this.maxConcurrent = maxConcurrent;
    this.delayMs = delayMs;
  }

  async throttle<T>(fn: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push({ fn, resolve, reject });
      this.processQueue();
    });
  }

  private async processQueue() {
    if (this.running >= this.maxConcurrent || this.queue.length === 0) {
      return;
    }

    // Ensure minimum delay between requests
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    if (timeSinceLastRequest < this.delayMs) {
      setTimeout(() => this.processQueue(), this.delayMs - timeSinceLastRequest);
      return;
    }

    const item = this.queue.shift();
    if (!item) return;

    this.running++;
    this.lastRequestTime = Date.now();

    try {
      const result = await item.fn();
      item.resolve(result);
    } catch (error) {
      item.reject(error);
    } finally {
      this.running--;
      // Process next item after a delay
      setTimeout(() => this.processQueue(), this.delayMs);
    }
  }

  clear() {
    this.queue = [];
    this.running = 0;
  }
}

// Create a singleton instance for sports API requests
export const sportsApiThrottler = new RequestThrottler(2, 500); // 2 concurrent, 500ms delay

/**
 * Helper function to process an array with throttling
 */
export async function throttledMap<T, R>(
  items: T[],
  fn: (item: T, index: number) => Promise<R>,
  throttler = sportsApiThrottler
): Promise<R[]> {
  return Promise.all(
    items.map((item, index) => throttler.throttle(() => fn(item, index)))
  );
}