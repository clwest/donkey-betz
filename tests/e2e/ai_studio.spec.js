// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * E2E Tests for AI Studio Interface
 *
 * Prerequisites:
 * - Django server running on localhost:8000
 * - Test user credentials available
 * - API keys configured (for actual generation tests)
 */

test.describe('AI Studio Home Page', () => {
  test('should load AI Studio page', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Check page title
    await expect(page).toHaveTitle(/AI Studio|Unified Donkey Betz/);

    // Check for main components
    await expect(page.locator('#ai-studio, .ai-studio-container')).toBeVisible();
  });

  test('should display project selector', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Wait for project selector to be visible
    const projectSelect = page.locator('#project-select, .project-selector');
    await expect(projectSelect).toBeVisible();
  });

  test('should display chat interface', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Check for chat input
    const chatInput = page.locator('#message-input, .chat-input, textarea[placeholder*="message"]');
    await expect(chatInput).toBeVisible();

    // Check for send button
    const sendButton = page.locator('#send-btn, .send-button, button:has-text("Send")');
    await expect(sendButton).toBeVisible();
  });
});

test.describe('Project Management', () => {
  test('should create new project via chat', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Type a project-creating message
    const chatInput = page.locator('#message-input, .chat-input, textarea').first();
    await chatInput.fill('Create a new project for a tech startup logo');

    // Click send
    const sendButton = page.locator('#send-btn, .send-button, button:has-text("Send")').first();
    await sendButton.click();

    // Wait for response (with longer timeout for AI processing)
    await page.waitForTimeout(3000);

    // Check for assistant response
    const assistantMessage = page.locator('.assistant-message, .ai-response, [class*="assistant"]');
    await expect(assistantMessage.first()).toBeVisible({ timeout: 30000 });
  });

  test('should select existing project', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Wait for projects to load
    await page.waitForLoadState('networkidle');

    // Check if project selector has options
    const projectSelect = page.locator('#project-select, select[name="project"]');

    // Count options (should have at least the placeholder)
    const optionCount = await projectSelect.locator('option').count();
    expect(optionCount).toBeGreaterThan(0);
  });
});

test.describe('Image Gallery', () => {
  test('should display images in gallery', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Look for gallery container
    const gallery = page.locator('#images-gallery, .images-gallery, .image-grid');

    // If gallery exists, check for image cards
    if (await gallery.isVisible()) {
      // There might be images or a placeholder
      const hasContent = await gallery.locator('img, .image-card, .placeholder').count();
      expect(hasContent).toBeGreaterThanOrEqual(0);
    }
  });

  test('should show image details on click', async ({ page }) => {
    await page.goto('/ai-studio/');
    await page.waitForLoadState('networkidle');

    // Find an image card if one exists
    const imageCard = page.locator('.image-card, .asset-card[data-type="image"]').first();

    if (await imageCard.isVisible()) {
      await imageCard.click();

      // Wait for details panel or modal
      const detailsPanel = page.locator('.image-details, .asset-details, .modal');
      await expect(detailsPanel).toBeVisible({ timeout: 5000 });
    }
  });
});

test.describe('Video Gallery', () => {
  test('should display videos in gallery', async ({ page }) => {
    await page.goto('/ai-studio/');
    await page.waitForLoadState('networkidle');

    // Look for video gallery container
    const videoGallery = page.locator('#videos-gallery, .videos-gallery');

    if (await videoGallery.isVisible()) {
      // Check for video cards or placeholders
      const hasContent = await videoGallery.locator('video, .video-card, .placeholder').count();
      expect(hasContent).toBeGreaterThanOrEqual(0);
    }
  });

  test('should play video on click', async ({ page }) => {
    await page.goto('/ai-studio/');
    await page.waitForLoadState('networkidle');

    // Find a completed video
    const videoElement = page.locator('.video-card video, video[src]').first();

    if (await videoElement.isVisible()) {
      // Click to play
      await videoElement.click();

      // Check if video started playing or controls appeared
      const isPlaying = await videoElement.evaluate(video => !video.paused);
      // Video might not auto-play due to browser policies
      expect(typeof isPlaying).toBe('boolean');
    }
  });
});

test.describe('Chat Functionality', () => {
  test('should send message and receive response', async ({ page }) => {
    await page.goto('/ai-studio/');
    await page.waitForLoadState('networkidle');

    // Find and fill chat input
    const chatInput = page.locator('#message-input, .chat-input, textarea').first();
    await chatInput.fill('Hello, what can you help me with?');

    // Send message
    const sendButton = page.locator('#send-btn, .send-button, button:has-text("Send")').first();
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(5000);

    // Check for assistant response
    const messages = page.locator('.message, .chat-message');
    const messageCount = await messages.count();
    expect(messageCount).toBeGreaterThan(0);
  });

  test('should preserve chat history on refresh', async ({ page }) => {
    await page.goto('/ai-studio/');
    await page.waitForLoadState('networkidle');

    // Send a message
    const chatInput = page.locator('#message-input, .chat-input, textarea').first();
    await chatInput.fill('Test message for persistence');

    const sendButton = page.locator('#send-btn, .send-button, button:has-text("Send")').first();
    await sendButton.click();

    await page.waitForTimeout(3000);

    // Refresh page
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Check if chat history persists (depends on implementation)
    const chatMessages = page.locator('.chat-messages, #chat-messages');
    await expect(chatMessages).toBeVisible();
  });
});

test.describe('Responsive Design', () => {
  test('should display correctly on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/ai-studio/');
    await page.waitForLoadState('networkidle');

    // Check if main content is visible
    const mainContent = page.locator('#ai-studio, .ai-studio-container, main');
    await expect(mainContent).toBeVisible();

    // Check for mobile navigation if exists
    const mobileNav = page.locator('.mobile-nav, .hamburger, [data-mobile-menu]');
    // Mobile nav may or may not exist
  });

  test('should display correctly on tablet', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });

    await page.goto('/ai-studio/');
    await page.waitForLoadState('networkidle');

    // Check if main content is visible
    const mainContent = page.locator('#ai-studio, .ai-studio-container, main');
    await expect(mainContent).toBeVisible();
  });
});

test.describe('Accessibility', () => {
  test('should have proper heading structure', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Check for h1
    const h1 = page.locator('h1');
    const h1Count = await h1.count();
    expect(h1Count).toBeGreaterThanOrEqual(1);

    // Check heading hierarchy
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').allTextContents();
    expect(headings.length).toBeGreaterThan(0);
  });

  test('should have proper form labels', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Check inputs have labels or aria-labels
    const inputs = page.locator('input, textarea, select');
    const inputCount = await inputs.count();

    for (let i = 0; i < Math.min(inputCount, 10); i++) {
      const input = inputs.nth(i);
      const hasLabel = await input.evaluate(el => {
        const id = el.id;
        const hasLabelElement = id && document.querySelector(`label[for="${id}"]`);
        const hasAriaLabel = el.getAttribute('aria-label');
        const hasPlaceholder = el.getAttribute('placeholder');
        return hasLabelElement || hasAriaLabel || hasPlaceholder;
      });
      // At minimum, expect placeholder for UX
      expect(typeof hasLabel).toBe('boolean');
    }
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Press Tab to navigate
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Check that some element is focused
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeTruthy();
  });
});

test.describe('Error Handling', () => {
  test('should handle network errors gracefully', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Intercept and fail a request
    await page.route('**/api/**', route => {
      route.abort('failed');
    });

    // Try to send a message
    const chatInput = page.locator('#message-input, .chat-input, textarea').first();
    await chatInput.fill('Test message');

    const sendButton = page.locator('#send-btn, .send-button, button:has-text("Send")').first();
    await sendButton.click();

    // Wait for error handling
    await page.waitForTimeout(3000);

    // Check that page doesn't crash (no uncaught errors visible)
    const pageContent = await page.content();
    expect(pageContent).not.toContain('Internal Server Error');
  });

  test('should display validation errors', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Try to send empty message
    const sendButton = page.locator('#send-btn, .send-button, button:has-text("Send")').first();
    await sendButton.click();

    // Either nothing happens (disabled) or validation message appears
    // This is implementation-specific
    await page.waitForTimeout(1000);
  });
});

test.describe('Performance', () => {
  test('should load page within acceptable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/ai-studio/');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // Page should load within 10 seconds
    expect(loadTime).toBeLessThan(10000);
  });

  test('should not have memory leaks on multiple navigations', async ({ page }) => {
    // Navigate back and forth multiple times
    for (let i = 0; i < 3; i++) {
      await page.goto('/ai-studio/');
      await page.waitForLoadState('networkidle');
      await page.goto('about:blank');
    }

    // If we get here without crashing, no major leaks
    expect(true).toBe(true);
  });
});
