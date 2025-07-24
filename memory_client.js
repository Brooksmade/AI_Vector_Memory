/**
 * Claude Memory Client - JavaScript library for Claude Desktop integration
 * Provides seamless access to the Claude Memory API from web interfaces
 * 
 * Usage:
 *   const client = new ClaudeMemoryClient('http://localhost:8080');
 *   const results = await client.search('python flask development');
 */

class ClaudeMemoryClient {
    constructor(baseUrl = 'http://localhost:8080', options = {}) {
        this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
        this.timeout = options.timeout || 5000; // 5 second default timeout
        this.retries = options.retries || 3;
        this.retryDelay = options.retryDelay || 1000;
        this.debug = options.debug || false;
        
        // Connection status
        this.connected = false;
        this.lastError = null;
        
        // Initialize connection check
        this._checkConnection();
    }

    /**
     * Check if the API server is accessible
     */
    async _checkConnection() {
        try {
            const response = await this._makeRequest('/api/health', { method: 'GET' });
            this.connected = response.success;
            this.lastError = null;
            if (this.debug) console.log('Memory API connected:', this.connected);
        } catch (error) {
            this.connected = false;
            this.lastError = error.message;
            if (this.debug) console.warn('Memory API connection failed:', error.message);
        }
    }

    /**
     * Search for memories based on query
     * @param {string} query - Search query
     * @param {Object} options - Search options
     * @returns {Promise<Object>} Search results
     */
    async search(query, options = {}) {
        if (!query || typeof query !== 'string') {
            throw new Error('Query must be a non-empty string');
        }

        const requestData = {
            query: query.trim(),
            max_results: Math.min(options.maxResults || 3, 10),
            similarity_threshold: options.similarityThreshold || 0.3,
            source_filter: options.sourceFilter || null
        };

        try {
            const response = await this._makeRequest('/api/search', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            if (response.success) {
                return {
                    success: true,
                    results: response.data.results,
                    totalResults: response.data.total_results,
                    searchTime: response.data.search_time_ms,
                    query: response.data.query
                };
            } else {
                throw new Error(response.error?.message || 'Search failed');
            }
        } catch (error) {
            return this._handleError(error, 'search');
        }
    }

    /**
     * Add a new memory to the database
     * @param {string} content - Memory content
     * @param {Object} metadata - Memory metadata
     * @returns {Promise<Object>} Add result
     */
    async addMemory(content, metadata = {}) {
        if (!content || typeof content !== 'string') {
            throw new Error('Content must be a non-empty string');
        }

        const requestData = {
            content: content.trim(),
            title: metadata.title || this._generateTitle(content),
            date: metadata.date || new Date().toISOString().split('T')[0],
            source: metadata.source || 'claude_desktop',
            technologies: metadata.technologies || [],
            file_paths: metadata.filePaths || [],
            complexity: metadata.complexity || 'medium',
            project: metadata.project || '',
            metadata: metadata.additionalData || {}
        };

        try {
            const response = await this._makeRequest('/api/add_memory', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            if (response.success) {
                return {
                    success: true,
                    id: response.data.id,
                    title: response.data.title,
                    message: response.data.message
                };
            } else {
                throw new Error(response.error?.message || 'Failed to add memory');
            }
        } catch (error) {
            return this._handleError(error, 'addMemory');
        }
    }

    /**
     * Get list of memories with pagination
     * @param {Object} options - Pagination options
     * @returns {Promise<Object>} Memory list
     */
    async listMemories(options = {}) {
        const page = Math.max(options.page || 1, 1);
        const limit = Math.min(Math.max(options.limit || 10, 1), 50);

        try {
            const response = await this._makeRequest(`/api/memories?page=${page}&limit=${limit}`, {
                method: 'GET'
            });

            if (response.success) {
                return {
                    success: true,
                    memories: response.data.memories,
                    pagination: response.data.pagination
                };
            } else {
                throw new Error(response.error?.message || 'Failed to list memories');
            }
        } catch (error) {
            return this._handleError(error, 'listMemories');
        }
    }

    /**
     * Delete a memory by ID
     * @param {string} memoryId - Memory ID to delete
     * @returns {Promise<Object>} Delete result
     */
    async deleteMemory(memoryId) {
        if (!memoryId) {
            throw new Error('Memory ID is required');
        }

        try {
            const response = await this._makeRequest(`/api/memory/${encodeURIComponent(memoryId)}`, {
                method: 'DELETE'
            });

            if (response.success) {
                return {
                    success: true,
                    message: response.data.message
                };
            } else {
                throw new Error(response.error?.message || 'Failed to delete memory');
            }
        } catch (error) {
            return this._handleError(error, 'deleteMemory');
        }
    }

    /**
     * Get system health status
     * @returns {Promise<Object>} Health status
     */
    async getHealth() {
        try {
            const response = await this._makeRequest('/api/health', { method: 'GET' });
            
            if (response.success) {
                this.connected = response.data.status === 'healthy';
                return {
                    success: true,
                    status: response.data.status,
                    database: response.data.database,
                    api: response.data.api,
                    performance: response.data.performance
                };
            } else {
                this.connected = false;
                throw new Error(response.error?.message || 'Health check failed');
            }
        } catch (error) {
            this.connected = false;
            return this._handleError(error, 'getHealth');
        }
    }

    /**
     * Trigger database reindex (admin operation)
     * @param {boolean} confirm - Confirmation flag
     * @returns {Promise<Object>} Reindex result
     */
    async reindex(confirm = false) {
        if (!confirm) {
            throw new Error('Reindex requires explicit confirmation');
        }

        try {
            const response = await this._makeRequest('/api/reindex', {
                method: 'POST',
                body: JSON.stringify({ confirm: true })
            });

            if (response.success) {
                return {
                    success: true,
                    message: response.data.message,
                    statistics: response.data.statistics
                };
            } else {
                throw new Error(response.error?.message || 'Reindex failed');
            }
        } catch (error) {
            return this._handleError(error, 'reindex');
        }
    }

    /**
     * Make HTTP request with retry logic
     * @private
     */
    async _makeRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const requestOptions = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...options.headers
            },
            signal: AbortSignal.timeout(this.timeout),
            ...options
        };

        let lastError;
        
        for (let attempt = 1; attempt <= this.retries; attempt++) {
            try {
                if (this.debug) {
                    console.log(`Memory API request (attempt ${attempt}):`, url, requestOptions);
                }

                const response = await fetch(url, requestOptions);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    let errorData;
                    try {
                        errorData = JSON.parse(errorText);
                    } catch {
                        errorData = { error: { message: errorText } };
                    }
                    
                    throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                
                if (this.debug) {
                    console.log('Memory API response:', data);
                }

                return data;
                
            } catch (error) {
                lastError = error;
                
                if (this.debug) {
                    console.warn(`Memory API request failed (attempt ${attempt}):`, error.message);
                }

                // Don't retry on certain errors
                if (error.name === 'AbortError' || 
                    error.message.includes('404') || 
                    error.message.includes('400') ||
                    attempt === this.retries) {
                    break;
                }

                // Wait before retry
                await new Promise(resolve => setTimeout(resolve, this.retryDelay * attempt));
            }
        }

        throw lastError;
    }

    /**
     * Handle and format errors consistently
     * @private
     */
    _handleError(error, operation) {
        const errorResponse = {
            success: false,
            error: {
                operation: operation,
                message: error.message,
                timestamp: new Date().toISOString()
            }
        };

        if (this.debug) {
            console.error(`Memory API ${operation} error:`, error);
        }

        return errorResponse;
    }

    /**
     * Generate a title from content
     * @private
     */
    _generateTitle(content) {
        // Extract first meaningful line or sentence
        const lines = content.split('\n').filter(line => line.trim().length > 0);
        
        if (lines.length === 0) {
            return 'Untitled Memory';
        }

        let title = lines[0].trim();
        
        // Remove common prefixes
        title = title.replace(/^(title:|summary:|description:)/i, '').trim();
        
        // Truncate if too long
        if (title.length > 100) {
            title = title.substring(0, 97) + '...';
        }

        return title || 'Untitled Memory';
    }

    /**
     * Get connection status
     */
    isConnected() {
        return this.connected;
    }

    /**
     * Get last error
     */
    getLastError() {
        return this.lastError;
    }
}

/**
 * Memory integration helper functions for Claude Desktop
 */
class MemoryIntegration {
    constructor(client) {
        this.client = client;
    }

    /**
     * Auto-search for relevant memories before tasks
     * @param {string} userRequest - User's request text
     * @returns {Promise<Object>} Relevant memories
     */
    async searchRelevantMemories(userRequest) {
        // Extract key terms from user request
        const keyTerms = this._extractKeyTerms(userRequest);
        
        if (keyTerms.length === 0) {
            return { success: true, results: [], message: 'No key terms found for search' };
        }

        // Search for memories
        const searchQuery = keyTerms.join(' ');
        const results = await this.client.search(searchQuery, { maxResults: 5 });
        
        if (results.success && results.results.length > 0) {
            return {
                success: true,
                results: results.results,
                searchQuery: searchQuery,
                message: `Found ${results.results.length} relevant memories`
            };
        }

        return { success: true, results: [], message: 'No relevant memories found' };
    }

    /**
     * Save conversation summary as memory
     * @param {string} conversationText - Full conversation text
     * @param {Object} metadata - Additional metadata
     * @returns {Promise<Object>} Save result
     */
    async saveConversationSummary(conversationText, metadata = {}) {
        // Generate summary from conversation
        const summary = this._generateSummary(conversationText);
        
        // Extract metadata from conversation
        const extractedMetadata = this._extractMetadata(conversationText);
        
        // Combine metadata
        const memoryMetadata = {
            ...extractedMetadata,
            ...metadata,
            source: 'claude_desktop',
            conversationLength: conversationText.length
        };

        return await this.client.addMemory(summary, memoryMetadata);
    }

    /**
     * Create memory status indicator for UI
     * @returns {Object} Status indicator data
     */
    async createMemoryStatusIndicator() {
        const health = await this.client.getHealth();
        
        return {
            connected: health.success && health.status === 'healthy',
            documentCount: health.success ? health.database?.document_count : 0,
            status: health.success ? health.status : 'disconnected',
            lastCheck: new Date().toISOString()
        };
    }

    /**
     * Extract key terms from text
     * @private
     */
    _extractKeyTerms(text) {
        // Simple key term extraction
        const words = text.toLowerCase()
            .replace(/[^\w\s]/g, ' ')
            .split(/\s+/)
            .filter(word => word.length > 3)
            .filter(word => !this._isStopWord(word));

        // Remove duplicates and return most relevant terms
        return [...new Set(words)].slice(0, 10);
    }

    /**
     * Check if word is a stop word
     * @private
     */
    _isStopWord(word) {
        const stopWords = ['this', 'that', 'with', 'from', 'they', 'been', 'have', 'were', 'what', 'when', 'where', 'will', 'there', 'would', 'could', 'should'];
        return stopWords.includes(word);
    }

    /**
     * Generate summary from conversation
     * @private
     */
    _generateSummary(conversationText) {
        // Simple summary generation - take first portion and key sections
        const lines = conversationText.split('\n').filter(line => line.trim().length > 0);
        
        if (lines.length <= 10) {
            return conversationText;
        }

        // Take first few lines and any lines with code or important keywords
        const summaryLines = lines.slice(0, 5);
        const codeLines = lines.filter(line => line.includes('```') || line.includes('def ') || line.includes('function'));
        
        return [...summaryLines, ...codeLines.slice(0, 5)].join('\n');
    }

    /**
     * Extract metadata from conversation
     * @private
     */
    _extractMetadata(text) {
        const metadata = {
            technologies: [],
            complexity: 'medium',
            codeBlocks: (text.match(/```/g) || []).length / 2
        };

        // Simple technology detection
        const techKeywords = {
            python: /python|django|flask|fastapi|pandas/i,
            javascript: /javascript|js|node|react|vue|angular/i,
            html: /html|css|scss|sass/i,
            sql: /sql|mysql|postgresql|sqlite/i,
            docker: /docker|container|kubernetes/i,
            git: /git|github|gitlab|commit/i
        };

        for (const [tech, regex] of Object.entries(techKeywords)) {
            if (regex.test(text)) {
                metadata.technologies.push(tech);
            }
        }

        // Estimate complexity based on content
        if (metadata.codeBlocks > 5 || text.length > 5000) {
            metadata.complexity = 'high';
        } else if (metadata.codeBlocks < 2 && text.length < 1000) {
            metadata.complexity = 'low';
        }

        return metadata;
    }
}

// Browser compatibility check
if (typeof window !== 'undefined') {
    // Browser environment
    window.ClaudeMemoryClient = ClaudeMemoryClient;
    window.MemoryIntegration = MemoryIntegration;
} else if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment
    module.exports = { ClaudeMemoryClient, MemoryIntegration };
}

// Usage example for Claude Desktop integration
const MEMORY_INTEGRATION_EXAMPLE = `
// Initialize memory client
const memoryClient = new ClaudeMemoryClient('http://localhost:8080', { debug: true });
const memoryIntegration = new MemoryIntegration(memoryClient);

// Before starting a task, search for relevant memories
async function beforeTask(userRequest) {
    const relevantMemories = await memoryIntegration.searchRelevantMemories(userRequest);
    
    if (relevantMemories.results.length > 0) {
        console.log('Found relevant memories:', relevantMemories.results);
        // Display to user or use in context
    }
}

// After completing a conversation, save it as memory
async function afterConversation(conversationText, metadata = {}) {
    const saveResult = await memoryIntegration.saveConversationSummary(conversationText, metadata);
    
    if (saveResult.success) {
        console.log('Conversation saved as memory:', saveResult.id);
    }
}

// Show memory status in UI
async function showMemoryStatus() {
    const status = await memoryIntegration.createMemoryStatusIndicator();
    console.log('Memory system status:', status);
}
`;