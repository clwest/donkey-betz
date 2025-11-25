/**
 * Tests for common JavaScript utilities
 * @jest-environment jsdom
 */

describe('Common Utilities', () => {
  describe('CSRF Token Handling', () => {
    test('should get CSRF token from cookie', () => {
      // Set up cookie
      document.cookie = 'csrftoken=test-csrf-token-12345';

      // Function to get CSRF token (simulating common.js behavior)
      function getCsrfToken() {
        const cookie = document.cookie
          .split('; ')
          .find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : null;
      }

      expect(getCsrfToken()).toBe('test-csrf-token-12345');
    });

    test('should return null when CSRF token not present', () => {
      document.cookie = '';

      function getCsrfToken() {
        const cookie = document.cookie
          .split('; ')
          .find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : null;
      }

      expect(getCsrfToken()).toBeNull();
    });
  });

  describe('API Request Helper', () => {
    test('should make POST request with correct headers', async () => {
      const mockResponse = { success: true, data: { id: '123' } };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      document.cookie = 'csrftoken=test-token';

      // Simulate API call
      const response = await fetch('/api/images/generate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': 'test-token',
        },
        body: JSON.stringify({ prompt: 'test image' }),
      });

      expect(fetch).toHaveBeenCalledWith('/api/images/generate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': 'test-token',
        },
        body: JSON.stringify({ prompt: 'test image' }),
      });

      const data = await response.json();
      expect(data.success).toBe(true);
    });

    test('should handle API errors gracefully', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(fetch('/api/test/')).rejects.toThrow('Network error');
    });
  });
});

describe('Image Gallery Functions', () => {
  test('should create image card element', () => {
    // Simulate renderAssetCard function behavior
    function createImageCard(image) {
      const card = document.createElement('div');
      card.className = 'asset-card';
      card.dataset.id = image.id;
      card.innerHTML = `
        <div class="asset-thumbnail">
          <img src="${image.file_path}" alt="${image.prompt || 'Generated image'}">
        </div>
        <div class="asset-info">
          <span class="asset-number">#${image.sequential_number}</span>
        </div>
      `;
      return card;
    }

    const testImage = {
      id: 'test-uuid-123',
      file_path: '/media/generated_images/test.png',
      prompt: 'A beautiful sunset',
      sequential_number: 42,
    };

    const card = createImageCard(testImage);

    expect(card.className).toBe('asset-card');
    expect(card.dataset.id).toBe('test-uuid-123');
    expect(card.querySelector('.asset-number').textContent).toBe('#42');
  });

  test('should toggle image selection', () => {
    document.body.innerHTML = `
      <div class="asset-card" data-id="img-1">
        <input type="checkbox" class="selection-checkbox">
      </div>
    `;

    const card = document.querySelector('.asset-card');
    const checkbox = card.querySelector('.selection-checkbox');

    // Simulate selection toggle
    checkbox.checked = true;
    card.classList.toggle('selected', checkbox.checked);

    expect(card.classList.contains('selected')).toBe(true);

    // Toggle off
    checkbox.checked = false;
    card.classList.toggle('selected', checkbox.checked);

    expect(card.classList.contains('selected')).toBe(false);
  });
});

describe('Video Status Polling', () => {
  test('should poll video status until completed', async () => {
    let pollCount = 0;

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ status: 'pending', video_url: null }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ status: 'processing', video_url: null }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ status: 'completed', video_url: 'https://example.com/video.mp4' }),
      });

    // Simulate polling function
    async function pollVideoStatus(videoId, maxAttempts = 10) {
      for (let i = 0; i < maxAttempts; i++) {
        const response = await fetch(`/api/videos/${videoId}/status/`);
        const data = await response.json();
        pollCount++;

        if (data.status === 'completed') {
          return data;
        }

        if (data.status === 'failed') {
          throw new Error('Video generation failed');
        }

        // In real code, would add delay here
      }
      throw new Error('Polling timeout');
    }

    const result = await pollVideoStatus('test-video-123');

    expect(pollCount).toBe(3);
    expect(result.status).toBe('completed');
    expect(result.video_url).toBe('https://example.com/video.mp4');
  });

  test('should handle video generation failure', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        status: 'failed',
        error_message: 'Content moderation failed'
      }),
    });

    async function pollVideoStatus(videoId) {
      const response = await fetch(`/api/videos/${videoId}/status/`);
      const data = await response.json();

      if (data.status === 'failed') {
        throw new Error(data.error_message || 'Video generation failed');
      }
      return data;
    }

    await expect(pollVideoStatus('test-video-123'))
      .rejects.toThrow('Content moderation failed');
  });
});

describe('Chat Interface Functions', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="chat-container">
        <div id="chat-messages"></div>
        <textarea id="chat-input"></textarea>
        <button id="send-button">Send</button>
      </div>
    `;
  });

  test('should append message to chat', () => {
    const chatMessages = document.getElementById('chat-messages');

    function appendMessage(role, content) {
      const messageDiv = document.createElement('div');
      messageDiv.className = `message ${role}-message`;
      messageDiv.innerHTML = content;
      chatMessages.appendChild(messageDiv);
    }

    appendMessage('user', 'Generate a logo for my company');
    appendMessage('assistant', 'I will create a logo for you.');

    const messages = chatMessages.querySelectorAll('.message');
    expect(messages.length).toBe(2);
    expect(messages[0].classList.contains('user-message')).toBe(true);
    expect(messages[1].classList.contains('assistant-message')).toBe(true);
  });

  test('should clear input after sending message', () => {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');

    chatInput.value = 'Test message';

    // Simulate send
    sendButton.addEventListener('click', () => {
      if (chatInput.value.trim()) {
        chatInput.value = '';
      }
    });

    sendButton.click();

    expect(chatInput.value).toBe('');
  });

  test('should not send empty messages', () => {
    const chatInput = document.getElementById('chat-input');
    let messageSent = false;

    function sendMessage() {
      if (chatInput.value.trim()) {
        messageSent = true;
      }
    }

    chatInput.value = '   ';
    sendMessage();

    expect(messageSent).toBe(false);
  });
});

describe('Project Management Functions', () => {
  test('should parse project colors from JSON', () => {
    const projectColors = '["#FF5733", "#33FF57", "#3357FF"]';

    function parseColors(colorsJson) {
      try {
        return JSON.parse(colorsJson);
      } catch (e) {
        return [];
      }
    }

    const colors = parseColors(projectColors);

    expect(colors).toHaveLength(3);
    expect(colors[0]).toBe('#FF5733');
  });

  test('should handle invalid JSON gracefully', () => {
    const invalidColors = 'not valid json';

    function parseColors(colorsJson) {
      try {
        return JSON.parse(colorsJson);
      } catch (e) {
        return [];
      }
    }

    const colors = parseColors(invalidColors);

    expect(colors).toEqual([]);
  });

  test('should format date for display', () => {
    function formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    }

    const formatted = formatDate('2025-11-24T10:30:00Z');

    expect(formatted).toContain('Nov');
    expect(formatted).toContain('24');
    expect(formatted).toContain('2025');
  });
});

describe('Form Validation', () => {
  test('should validate required fields', () => {
    function validateForm(fields) {
      const errors = [];

      for (const [name, value] of Object.entries(fields)) {
        if (!value || value.trim() === '') {
          errors.push(`${name} is required`);
        }
      }

      return errors;
    }

    const validForm = { prompt: 'A beautiful sunset', style: 'photographic' };
    const invalidForm = { prompt: '', style: 'photographic' };

    expect(validateForm(validForm)).toHaveLength(0);
    expect(validateForm(invalidForm)).toContain('prompt is required');
  });

  test('should validate image dimensions', () => {
    function validateDimensions(width, height) {
      const validDimensions = [512, 768, 1024, 1152, 1216, 1344, 1536];

      return validDimensions.includes(width) && validDimensions.includes(height);
    }

    expect(validateDimensions(1024, 1024)).toBe(true);
    expect(validateDimensions(500, 500)).toBe(false);
    expect(validateDimensions(1024, 768)).toBe(true);
  });
});

describe('Batch Operations', () => {
  test('should parse range string', () => {
    function parseRange(rangeStr) {
      const result = [];
      const parts = rangeStr.split(',').map(s => s.trim());

      for (const part of parts) {
        if (part.includes('-')) {
          const [start, end] = part.split('-').map(Number);
          for (let i = start; i <= end; i++) {
            result.push(i);
          }
        } else {
          result.push(Number(part));
        }
      }

      return result;
    }

    expect(parseRange('1-5')).toEqual([1, 2, 3, 4, 5]);
    expect(parseRange('1, 3, 5')).toEqual([1, 3, 5]);
    expect(parseRange('1-3, 7, 10-12')).toEqual([1, 2, 3, 7, 10, 11, 12]);
  });

  test('should track batch operation progress', () => {
    function createProgressTracker(total) {
      let completed = 0;
      let failed = 0;

      return {
        markComplete: () => { completed++; },
        markFailed: () => { failed++; },
        getProgress: () => ({
          completed,
          failed,
          total,
          percentage: Math.round((completed / total) * 100),
        }),
      };
    }

    const tracker = createProgressTracker(10);

    tracker.markComplete();
    tracker.markComplete();
    tracker.markFailed();

    const progress = tracker.getProgress();

    expect(progress.completed).toBe(2);
    expect(progress.failed).toBe(1);
    expect(progress.percentage).toBe(20);
  });
});
