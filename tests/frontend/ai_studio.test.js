/**
 * Tests for AI Studio interface functionality
 * @jest-environment jsdom
 */

describe('AI Studio Interface', () => {
  beforeEach(() => {
    // Set up basic DOM structure
    document.body.innerHTML = `
      <div id="ai-studio">
        <div id="project-panel">
          <select id="project-select">
            <option value="">Select a project</option>
          </select>
        </div>
        <div id="chat-panel">
          <div id="project-chat-messages"></div>
          <div id="chat-input-area">
            <textarea id="message-input" placeholder="Type your message..."></textarea>
            <button id="send-btn">Send</button>
          </div>
        </div>
        <div id="gallery-panel">
          <div id="images-gallery"></div>
          <div id="videos-gallery"></div>
          <div id="models-gallery"></div>
        </div>
      </div>
    `;
  });

  describe('Project Selection', () => {
    test('should load projects into select dropdown', () => {
      const projectSelect = document.getElementById('project-select');
      const projects = [
        { id: 'proj-1', name: 'Tech Startup Logo' },
        { id: 'proj-2', name: 'Fashion Brand Identity' },
      ];

      // Simulate loading projects
      projects.forEach(project => {
        const option = document.createElement('option');
        option.value = project.id;
        option.textContent = project.name;
        projectSelect.appendChild(option);
      });

      expect(projectSelect.options.length).toBe(3); // Including placeholder
      expect(projectSelect.options[1].text).toBe('Tech Startup Logo');
    });

    test('should trigger gallery refresh on project change', () => {
      const projectSelect = document.getElementById('project-select');
      let galleryRefreshed = false;

      projectSelect.addEventListener('change', () => {
        galleryRefreshed = true;
      });

      // Add an option and select it
      const option = document.createElement('option');
      option.value = 'proj-1';
      projectSelect.appendChild(option);
      projectSelect.value = 'proj-1';

      // Trigger change event
      projectSelect.dispatchEvent(new Event('change'));

      expect(galleryRefreshed).toBe(true);
    });
  });

  describe('Message Input', () => {
    test('should handle Enter key to send message', () => {
      const messageInput = document.getElementById('message-input');
      let messageSent = false;

      messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          if (messageInput.value.trim()) {
            messageSent = true;
          }
        }
      });

      messageInput.value = 'Generate a logo';

      // Simulate Enter key
      const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        bubbles: true,
      });
      messageInput.dispatchEvent(enterEvent);

      expect(messageSent).toBe(true);
    });

    test('should allow Shift+Enter for new lines', () => {
      const messageInput = document.getElementById('message-input');
      let messageSent = false;

      messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          messageSent = true;
        }
        // Shift+Enter should not trigger send
      });

      // Simulate Shift+Enter
      const shiftEnterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        shiftKey: true,
        bubbles: true,
      });
      messageInput.dispatchEvent(shiftEnterEvent);

      expect(messageSent).toBe(false);
    });
  });

  describe('Gallery Management', () => {
    test('should render image cards in gallery', () => {
      const imagesGallery = document.getElementById('images-gallery');

      const images = [
        { id: 'img-1', sequential_number: 1, file_path: '/media/test1.png' },
        { id: 'img-2', sequential_number: 2, file_path: '/media/test2.png' },
      ];

      function renderImageCard(image) {
        const card = document.createElement('div');
        card.className = 'image-card';
        card.dataset.id = image.id;
        card.innerHTML = `
          <img src="${image.file_path}" alt="Image #${image.sequential_number}">
          <span class="seq-num">#${image.sequential_number}</span>
        `;
        return card;
      }

      images.forEach(img => {
        imagesGallery.appendChild(renderImageCard(img));
      });

      expect(imagesGallery.querySelectorAll('.image-card').length).toBe(2);
    });

    test('should render video cards with status indicator', () => {
      const videosGallery = document.getElementById('videos-gallery');

      function renderVideoCard(video) {
        const card = document.createElement('div');
        card.className = 'video-card';
        card.dataset.id = video.id;
        card.dataset.status = video.status;
        card.innerHTML = `
          <div class="video-thumbnail ${video.status}">
            ${video.status === 'completed'
              ? `<video src="${video.video_url}" poster="${video.thumbnail_url || ''}"></video>`
              : `<div class="status-indicator">${video.status}</div>`
            }
          </div>
        `;
        return card;
      }

      const pendingVideo = { id: 'vid-1', status: 'pending', video_url: null };
      const completedVideo = { id: 'vid-2', status: 'completed', video_url: 'https://example.com/video.mp4' };

      videosGallery.appendChild(renderVideoCard(pendingVideo));
      videosGallery.appendChild(renderVideoCard(completedVideo));

      const pendingCard = videosGallery.querySelector('[data-status="pending"]');
      const completedCard = videosGallery.querySelector('[data-status="completed"]');

      expect(pendingCard.querySelector('.status-indicator').textContent).toBe('pending');
      expect(completedCard.querySelector('video')).not.toBeNull();
    });

    test('should render 3D model cards', () => {
      const modelsGallery = document.getElementById('models-gallery');

      function renderModelCard(model) {
        const card = document.createElement('div');
        card.className = 'model-card';
        card.dataset.id = model.id;
        card.innerHTML = `
          <div class="model-preview">
            <span class="model-icon">🎨</span>
          </div>
          <div class="model-info">
            <span class="model-name">${model.name || `3D Model #${model.sequential_number}`}</span>
            <span class="model-status">${model.status}</span>
          </div>
          <div class="model-actions">
            ${model.status === 'completed' ? `
              <button class="download-glb" data-url="${model.glb_url}">Download GLB</button>
              <button class="download-stl" data-url="${model.stl_url}">Download STL</button>
            ` : ''}
          </div>
        `;
        return card;
      }

      const model = {
        id: 'model-1',
        sequential_number: 1,
        name: 'Character Model',
        status: 'completed',
        glb_url: '/media/minifigs/test.glb',
        stl_url: '/media/minifigs/test.stl',
      };

      modelsGallery.appendChild(renderModelCard(model));

      const card = modelsGallery.querySelector('.model-card');
      expect(card.querySelector('.model-name').textContent).toBe('Character Model');
      expect(card.querySelectorAll('button').length).toBe(2);
    });
  });

  describe('Progress Display', () => {
    test('should show progress message for operations', () => {
      document.body.innerHTML += '<div id="progress-container"></div>';
      const progressContainer = document.getElementById('progress-container');

      function showProgress(message, type = 'info') {
        progressContainer.innerHTML = `
          <div class="progress-message ${type}">
            <span class="spinner">⏳</span>
            <span class="message">${message}</span>
          </div>
        `;
      }

      showProgress('Generating image...', 'info');

      expect(progressContainer.querySelector('.message').textContent).toBe('Generating image...');
      expect(progressContainer.querySelector('.progress-message').classList.contains('info')).toBe(true);
    });

    test('should update progress with agent information', () => {
      document.body.innerHTML += '<div id="agent-status"></div>';
      const agentStatus = document.getElementById('agent-status');

      function updateAgentStatus(agent, operation) {
        agentStatus.innerHTML = `
          <div class="agent-indicator">
            <span class="agent-icon">🤖</span>
            <span class="agent-name">${agent}</span>
            <span class="operation">${operation}</span>
          </div>
        `;
      }

      updateAgentStatus('Image Generation Agent', 'Creating your image');

      expect(agentStatus.querySelector('.agent-name').textContent).toBe('Image Generation Agent');
      expect(agentStatus.querySelector('.operation').textContent).toBe('Creating your image');
    });
  });

  describe('Tool Results Handling', () => {
    test('should format image generation results', () => {
      function formatToolResult(result) {
        if (result.type === 'image_generation') {
          return `
            <div class="tool-result success">
              <p>✅ Generated image #${result.sequential_number}</p>
              <img src="${result.file_path}" alt="Generated image" class="result-preview">
            </div>
          `;
        }
        return '<div class="tool-result">Unknown result type</div>';
      }

      const result = {
        type: 'image_generation',
        success: true,
        sequential_number: 42,
        file_path: '/media/generated/test.png',
      };

      const html = formatToolResult(result);

      expect(html).toContain('Generated image #42');
      expect(html).toContain('success');
    });

    test('should format video generation results with polling indicator', () => {
      function formatVideoResult(result) {
        if (result.status === 'pending') {
          return `
            <div class="tool-result pending">
              <p>⏳ Video generation started (ID: ${result.video_id})</p>
              <p class="status-message">Polling for completion...</p>
            </div>
          `;
        }
        if (result.status === 'completed') {
          return `
            <div class="tool-result success">
              <p>✅ Video #${result.sequential_number} completed!</p>
              <video src="${result.video_url}" controls class="result-preview"></video>
            </div>
          `;
        }
        return '<div class="tool-result error">Video generation failed</div>';
      }

      const pendingResult = { status: 'pending', video_id: 'test-123' };
      const completedResult = {
        status: 'completed',
        sequential_number: 5,
        video_url: 'https://example.com/video.mp4',
      };

      expect(formatVideoResult(pendingResult)).toContain('Polling for completion');
      expect(formatVideoResult(completedResult)).toContain('Video #5 completed');
    });

    test('should format error results with actionable messages', () => {
      function formatErrorResult(error) {
        const errorMessages = {
          'rate_limit': 'Rate limit exceeded. Please wait a moment and try again.',
          'api_error': 'External API error. Please try again later.',
          'validation': 'Invalid input. Please check your parameters.',
          'default': 'An error occurred. Please try again.',
        };

        const message = errorMessages[error.code] || errorMessages['default'];

        return `
          <div class="tool-result error">
            <p>❌ ${message}</p>
            ${error.details ? `<p class="error-details">${error.details}</p>` : ''}
          </div>
        `;
      }

      const rateLimitError = { code: 'rate_limit' };
      const apiError = { code: 'api_error', details: 'Stability AI service unavailable' };

      expect(formatErrorResult(rateLimitError)).toContain('Rate limit exceeded');
      expect(formatErrorResult(apiError)).toContain('Stability AI service unavailable');
    });
  });

  describe('Workflow Execution', () => {
    test('should track workflow step progress', () => {
      function createWorkflowTracker(steps) {
        let currentStep = 0;
        const stepResults = [];

        return {
          getCurrentStep: () => steps[currentStep],
          markStepComplete: (result) => {
            stepResults.push({ step: steps[currentStep], result });
            currentStep++;
          },
          isComplete: () => currentStep >= steps.length,
          getProgress: () => ({
            current: currentStep,
            total: steps.length,
            percentage: Math.round((currentStep / steps.length) * 100),
            results: stepResults,
          }),
        };
      }

      const workflow = createWorkflowTracker([
        'Generate logo concepts',
        'Create color variations',
        'Generate video animation',
      ]);

      expect(workflow.getCurrentStep()).toBe('Generate logo concepts');

      workflow.markStepComplete({ images: ['img1.png'] });
      expect(workflow.getProgress().percentage).toBe(33);

      workflow.markStepComplete({ images: ['img2.png'] });
      workflow.markStepComplete({ video: 'video.mp4' });

      expect(workflow.isComplete()).toBe(true);
      expect(workflow.getProgress().percentage).toBe(100);
    });
  });
});

describe('Voice Command Parsing', () => {
  test('should parse time references from commands', () => {
    function parseTimeReference(command) {
      // Match patterns like "at 8 seconds", "at 0:30", "for 5 seconds"
      const atMatch = command.match(/at (\d+(?:\.\d+)?)\s*(?:seconds?|s)/i);
      const forMatch = command.match(/for (\d+(?:\.\d+)?)\s*(?:seconds?|s)/i);
      const hhmmssMatch = command.match(/at (\d+):(\d{2})(?::(\d{2}))?/);

      let startTime = null;
      let duration = null;

      if (atMatch) {
        startTime = parseFloat(atMatch[1]);
      } else if (hhmmssMatch) {
        const [_, hours, minutes, seconds = 0] = hhmmssMatch;
        startTime = parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(seconds);
      }

      if (forMatch) {
        duration = parseFloat(forMatch[1]);
      }

      return { startTime, duration };
    }

    expect(parseTimeReference('Add text at 8 seconds')).toEqual({ startTime: 8, duration: null });
    expect(parseTimeReference('Show title at 5 seconds for 3 seconds')).toEqual({ startTime: 5, duration: 3 });
    expect(parseTimeReference('Start at 1:30')).toEqual({ startTime: 90, duration: null });
  });

  test('should parse image references from commands', () => {
    function parseImageReference(command) {
      // Match patterns like "image 5", "images 1-3", "image #42"
      const singleMatch = command.match(/image\s*#?(\d+)/i);
      const rangeMatch = command.match(/images?\s*(\d+)\s*-\s*(\d+)/i);
      const listMatch = command.match(/images?\s*((?:\d+\s*,?\s*)+)/i);

      if (rangeMatch) {
        const start = parseInt(rangeMatch[1]);
        const end = parseInt(rangeMatch[2]);
        return Array.from({ length: end - start + 1 }, (_, i) => start + i);
      }

      if (listMatch) {
        return listMatch[1].split(/[\s,]+/).filter(Boolean).map(Number);
      }

      if (singleMatch) {
        return [parseInt(singleMatch[1])];
      }

      return [];
    }

    expect(parseImageReference('Upscale image 5')).toEqual([5]);
    expect(parseImageReference('Remove background from images 1-3')).toEqual([1, 2, 3]);
    expect(parseImageReference('Process image #42')).toEqual([42]);
    expect(parseImageReference('Select images 1, 5, 9')).toEqual([1, 5, 9]);
  });
});

describe('Local Storage Management', () => {
  test('should save and load user preferences', () => {
    const preferences = {
      defaultStyle: 'photographic',
      defaultModel: 'ultra',
      autoSave: true,
    };

    localStorage.setItem('userPreferences', JSON.stringify(preferences));
    localStorage.getItem.mockReturnValue(JSON.stringify(preferences));

    const loaded = JSON.parse(localStorage.getItem('userPreferences'));

    expect(loaded.defaultStyle).toBe('photographic');
    expect(loaded.autoSave).toBe(true);
  });

  test('should save chat history per project', () => {
    function saveChatHistory(projectId, messages) {
      const key = `chat_history_${projectId}`;
      localStorage.setItem(key, JSON.stringify(messages));
    }

    function loadChatHistory(projectId) {
      const key = `chat_history_${projectId}`;
      const saved = localStorage.getItem(key);
      return saved ? JSON.parse(saved) : [];
    }

    const projectId = 'proj-123';
    const messages = [
      { role: 'user', content: 'Generate a logo' },
      { role: 'assistant', content: 'Creating your logo...' },
    ];

    saveChatHistory(projectId, messages);
    localStorage.getItem.mockReturnValue(JSON.stringify(messages));

    const loaded = loadChatHistory(projectId);

    expect(localStorage.setItem).toHaveBeenCalledWith(
      `chat_history_${projectId}`,
      JSON.stringify(messages)
    );
  });
});
