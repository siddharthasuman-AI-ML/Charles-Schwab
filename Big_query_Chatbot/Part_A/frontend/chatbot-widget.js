/**
 * BigQuery Chatbot Widget
 * Embeddable chat widget for natural language queries to BigQuery
 * Version: 1.0
 */

(function() {
    'use strict';
    
    // Widget namespace
    window.ChatbotWidget = {
        config: {
            apiUrl: 'http://localhost:8501',
            position: 'bottom-right',
            theme: 'light'
        },
        isOpen: false,
        isInitialized: false,
        chatHistory: [],
        
        /**
         * Initialize the chatbot widget
         * @param {Object} options - Configuration options
         */
        init: function(options) {
            if (this.isInitialized) {
                console.warn('Chatbot widget already initialized');
                return;
            }
            
            // Merge custom config with defaults
            this.config = { ...this.config, ...options };
            
            // Create widget HTML
            this.createWidget();
            
            // Attach event listeners
            this.attachEventListeners();
            
            this.isInitialized = true;
            console.log('BigQuery Chatbot Widget initialized');
        },
        
        /**
         * Create the widget HTML structure
         */
        createWidget: function() {
            // Create widget container
            const widgetContainer = document.createElement('div');
            widgetContainer.id = 'bq-chatbot-widget';
            widgetContainer.className = 'bq-chatbot-container';
            
            widgetContainer.innerHTML = `
                <!-- Chat Toggle Button -->
                <button id="bq-chat-toggle" class="bq-chat-toggle" aria-label="Toggle chat">
                    <svg class="bq-chat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    <svg class="bq-close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
                
                <!-- Chat Window -->
                <div id="bq-chat-window" class="bq-chat-window">
                    <!-- Chat Header -->
                    <div class="bq-chat-header">
                        <div class="bq-header-content">
                            <div class="bq-header-icon">
                                <svg viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                                </svg>
                            </div>
                            <div class="bq-header-text">
                                <h3>BigQuery Assistant</h3>
                                <p>Ask me anything about your data</p>
                            </div>
                        </div>
                        <button id="bq-minimize" class="bq-minimize-btn" aria-label="Minimize chat">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Chat Messages -->
                    <div id="bq-chat-messages" class="bq-chat-messages">
                        <div class="bq-message bq-bot-message">
                            <div class="bq-message-content">
                                <p>👋 Hi! I'm your BigQuery assistant. Ask me anything about your data using natural language!</p>
                                <p class="bq-message-hint">Example: "Show me the top 10 customers by revenue"</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Chat Input -->
                    <div class="bq-chat-input-container">
                        <textarea 
                            id="bq-chat-input" 
                            class="bq-chat-input" 
                            placeholder="Type your question here..."
                            rows="1"
                        ></textarea>
                        <button id="bq-send-btn" class="bq-send-btn" aria-label="Send message">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Powered By Footer -->
                    <div class="bq-chat-footer">
                        <span>Powered by Gemini AI & BigQuery</span>
                    </div>
                </div>
            `;
            
            document.body.appendChild(widgetContainer);
        },
        
        /**
         * Attach event listeners to widget elements
         */
        attachEventListeners: function() {
            const toggleBtn = document.getElementById('bq-chat-toggle');
            const minimizeBtn = document.getElementById('bq-minimize');
            const sendBtn = document.getElementById('bq-send-btn');
            const chatInput = document.getElementById('bq-chat-input');
            
            // Toggle chat window
            toggleBtn.addEventListener('click', () => this.toggleChat());
            minimizeBtn.addEventListener('click', () => this.toggleChat());
            
            // Send message
            sendBtn.addEventListener('click', () => this.sendMessage());
            
            // Send on Enter (but Shift+Enter for new line)
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            // Auto-resize textarea
            chatInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
        },
        
        /**
         * Toggle chat window open/close
         */
        toggleChat: function() {
            this.isOpen = !this.isOpen;
            const chatWindow = document.getElementById('bq-chat-window');
            const toggleBtn = document.getElementById('bq-chat-toggle');
            
            if (this.isOpen) {
                chatWindow.classList.add('bq-open');
                toggleBtn.classList.add('bq-active');
                document.getElementById('bq-chat-input').focus();
            } else {
                chatWindow.classList.remove('bq-open');
                toggleBtn.classList.remove('bq-active');
            }
        },
        
        /**
         * Send user message and get response
         */
        sendMessage: async function() {
            const inputField = document.getElementById('bq-chat-input');
            const message = inputField.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            this.addMessage(message, 'user');
            
            // Clear input
            inputField.value = '';
            inputField.style.height = 'auto';
            
            // Show typing indicator
            this.showTypingIndicator();
            
            try {
                // Send request to API
                const response = await this.callAPI(message);
                
                // Remove typing indicator
                this.removeTypingIndicator();
                
                // Add bot response
                this.addBotResponse(response);
                
            } catch (error) {
                console.error('Error sending message:', error);
                this.removeTypingIndicator();
                this.addMessage(
                    '❌ Sorry, I encountered an error processing your request. Please try again.',
                    'bot',
                    true
                );
            }
        },
        
        /**
         * Call the backend API
         * @param {string} query - User query
         * @returns {Promise<Object>} API response
         */
        callAPI: async function(query) {
            const apiEndpoint = `${this.config.apiUrl}/?query=${encodeURIComponent(query)}`;
            
            const response = await fetch(apiEndpoint, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.status}`);
            }
            
            return await response.json();
        },
        
        /**
         * Add message to chat
         * @param {string} message - Message text
         * @param {string} sender - 'user' or 'bot'
         * @param {boolean} isError - Whether this is an error message
         */
        addMessage: function(message, sender, isError = false) {
            const messagesContainer = document.getElementById('bq-chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `bq-message bq-${sender}-message`;
            
            if (isError) {
                messageDiv.classList.add('bq-error-message');
            }
            
            messageDiv.innerHTML = `
                <div class="bq-message-content">
                    <p>${this.escapeHtml(message)}</p>
                </div>
            `;
            
            messagesContainer.appendChild(messageDiv);
            this.scrollToBottom();
            
            // Add to history
            this.chatHistory.push({ message, sender, timestamp: new Date() });
        },
        
        /**
         * Add bot response with formatted data
         * @param {Object} response - API response
         */
        addBotResponse: function(response) {
            const messagesContainer = document.getElementById('bq-chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'bq-message bq-bot-message';
            
            let content = '<div class="bq-message-content">';
            
            if (response.success) {
                // Always show Natural Language Summary first (if available)
                if (response.summary) {
                    content += `
                        <div class="bq-summary-block">
                            <p class="bq-summary-text">${this.escapeHtml(response.summary)}</p>
                        </div>
                    `;
                }
                
                // ============================================================================
                // MODE 1: Show SQL and Table (Current - Comment out this block for Mode 2)
                // ============================================================================
                
                // Show SQL query
                if (response.sql) {
                    content += `
                        <div class="bq-sql-block">
                            <div class="bq-sql-label">Generated SQL:</div>
                            <code class="bq-sql-code">${this.escapeHtml(response.sql)}</code>
                        </div>
                    `;
                }
                
                // Show results table
                if (response.data && response.data.length > 0) {
                    content += `<p><strong>Results:</strong> (${response.row_count} rows)</p>`;
                    content += this.formatDataTable(response.data, response.columns);
                } else {
                    content += '<p>✅ Query executed successfully, but no data was returned.</p>';
                }
                
                // ============================================================================
                // MODE 2: Only Natural Language (Uncomment below and comment out above block)
                // ============================================================================
                // if (response.summary) {
                //     // Only summary shown - no SQL or table
                //     // content += '<p class="bq-message-hint">💡 Natural language summary only mode</p>';
                // }
                
                // Show demo mode warning if applicable
                if (response.demo_mode || response.note) {
                    content += `<p class="bq-test-note">⚠️ ${response.note || 'Demo mode - Sample data'}</p>`;
                }
            } else {
                content += `<p>❌ <strong>Error:</strong> ${this.escapeHtml(response.error || 'Unknown error')}</p>`;
                if (response.sql) {
                    content += `
                        <div class="bq-sql-block">
                            <div class="bq-sql-label">Generated SQL:</div>
                            <code class="bq-sql-code">${this.escapeHtml(response.sql)}</code>
                        </div>
                    `;
                }
            }
            
            content += '</div>';
            messageDiv.innerHTML = content;
            
            messagesContainer.appendChild(messageDiv);
            this.scrollToBottom();
        },
        
        /**
         * Format data as HTML table
         * @param {Array} data - Array of data objects
         * @param {Array} columns - Column names
         * @returns {string} HTML table string
         */
        formatDataTable: function(data, columns) {
            if (!data || data.length === 0) return '<p>No data</p>';
            
            // Limit to first 10 rows for display
            const displayData = data.slice(0, 10);
            const hasMore = data.length > 10;
            
            let table = '<div class="bq-table-container"><table class="bq-data-table">';
            
            // Header
            table += '<thead><tr>';
            columns.forEach(col => {
                table += `<th>${this.escapeHtml(col)}</th>`;
            });
            table += '</tr></thead>';
            
            // Body
            table += '<tbody>';
            displayData.forEach(row => {
                table += '<tr>';
                columns.forEach(col => {
                    const value = row[col];
                    table += `<td>${this.escapeHtml(String(value ?? ''))}</td>`;
                });
                table += '</tr>';
            });
            table += '</tbody>';
            
            table += '</table></div>';
            
            if (hasMore) {
                table += `<p class="bq-table-note">Showing 10 of ${data.length} rows</p>`;
            }
            
            return table;
        },
        
        /**
         * Show typing indicator
         */
        showTypingIndicator: function() {
            const messagesContainer = document.getElementById('bq-chat-messages');
            const typingDiv = document.createElement('div');
            typingDiv.id = 'bq-typing-indicator';
            typingDiv.className = 'bq-message bq-bot-message bq-typing';
            typingDiv.innerHTML = `
                <div class="bq-message-content">
                    <div class="bq-typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            messagesContainer.appendChild(typingDiv);
            this.scrollToBottom();
        },
        
        /**
         * Remove typing indicator
         */
        removeTypingIndicator: function() {
            const typingIndicator = document.getElementById('bq-typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        },
        
        /**
         * Scroll chat to bottom
         */
        scrollToBottom: function() {
            const messagesContainer = document.getElementById('bq-chat-messages');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        },
        
        /**
         * Escape HTML to prevent XSS
         * @param {string} text - Text to escape
         * @returns {string} Escaped text
         */
        escapeHtml: function(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };
    
    // Auto-initialize if config is provided
    if (window.BQ_CHATBOT_CONFIG) {
        document.addEventListener('DOMContentLoaded', function() {
            ChatbotWidget.init(window.BQ_CHATBOT_CONFIG);
        });
    }
})();




