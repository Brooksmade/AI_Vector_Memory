# Claude Memory API - Integration Guide

This guide provides complete instructions for integrating the Claude Memory API with both Claude Code CLI and Claude Desktop.

## 🚀 **Prerequisites**

1. **Start the Memory API Server**:
   ```bash
   cd E:\tools\claude-code-vector-memory
   python memory_api_server.py
   ```
   
2. **Verify API is Running**:
   ```bash
   curl http://localhost:8080/api/health
   ```

---

## 📟 **Claude Code CLI Integration**

### **Step 1: Update CLAUDE.md**

The CLAUDE.md file in your project has been updated with Memory API integration. The key sections are:

- **Memory API Usage**: Instructions for searching memories before tasks
- **API Endpoints**: All available endpoints and their purposes  
- **Request/Response Formats**: JSON schemas for API calls
- **Memory Presentation**: How to present found memories to users
- **After Task Completion**: How to save conversation summaries

### **Step 2: Memory Search Workflow**

Before starting any task, Claude Code should:

1. **Extract key terms** from user request
2. **Search memories** using the API:
   ```bash
   curl -X POST http://localhost:8080/api/search \
     -H "Content-Type: application/json" \
     -d '{"query": "react components inventory", "max_results": 3}'
   ```
3. **Present findings** to user with relevance scores
4. **Ask user** about building on previous work

### **Step 3: Save Completed Work**

After completing significant tasks:

```bash
curl -X POST http://localhost:8080/api/add_memory \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Detailed summary of work completed...",
    "title": "React Component Refactoring Session",  
    "source": "claude_code",
    "technologies": ["react", "typescript", "components"],
    "complexity": "medium",
    "project": "warehouse-inventory-management"
  }'
```

### **Step 4: Example Integration**

Here's how Claude Code should integrate memory search:

```
User: "Help me create a new inventory component"

Claude Code Response:
📚 Searching for relevant past work...

[Calls Memory API]

📚 I found relevant past work (via Memory API):
1. Inventory Table Component - 2025-07-20 (Similarity: 92%): We built a comprehensive inventory table with sorting and filtering
   - Relevant because: Shows patterns for inventory data display and interaction
2. Item Detail Modal - 2025-07-18 (Similarity: 78%): We created a modal for viewing/editing item details  
   - Could apply here for: Component structure and form handling patterns

Would you like me to build on any of these previous approaches, or should we start fresh?

[User responds, then Claude proceeds with the task]
```

---

## 🖥️ **Claude Desktop Integration**

### **Step 1: Include JavaScript Client**

Add the JavaScript client to your Claude Desktop environment:

```html
<script src="E:\tools\claude-code-vector-memory\memory_client.js"></script>
```

### **Step 2: Initialize Memory Client**

```javascript
// Initialize the memory client
const memoryClient = new ClaudeMemoryClient('http://localhost:8080', { 
  debug: true 
});

// Initialize integration helper
const memoryIntegration = new MemoryIntegration(memoryClient);

// Check if memory system is available
async function checkMemorySystem() {
  const health = await memoryClient.getHealth();
  if (health.success) {
    console.log('✅ Memory system connected');
    console.log(`📊 Documents: ${health.database.document_count}`);
  } else {
    console.log('❌ Memory system unavailable');
  }
}

checkMemorySystem();
```

### **Step 3: Auto-Search Before Tasks**

Implement automatic memory search before tasks:

```javascript
// Before starting any task
async function beforeTask(userRequest) {
  console.log('🔍 Searching for relevant memories...');
  
  const relevantMemories = await memoryIntegration.searchRelevantMemories(userRequest);
  
  if (relevantMemories.results.length > 0) {
    console.log('📚 Found relevant past work:');
    
    relevantMemories.results.forEach((memory, index) => {
      console.log(`${index + 1}. ${memory.title} - ${memory.date} (${(memory.similarity * 100).toFixed(0)}%)`);
      console.log(`   Preview: ${memory.preview.substring(0, 100)}...`);
      console.log(`   Technologies: ${memory.metadata.technologies.join(', ')}`);
    });
    
    // Present to user (implement UI as needed)
    displayMemoriesToUser(relevantMemories.results);
    
    return relevantMemories.results;
  } else {
    console.log('📭 No relevant past work found');
    return [];
  }
}

// Example usage
async function handleUserRequest(userInput) {
  // Search for relevant memories first
  const relevantMemories = await beforeTask(userInput);
  
  // Ask user about building on previous work
  const shouldBuildOn = await askUserAboutPreviousWork(relevantMemories);
  
  // Proceed with task based on user choice
  if (shouldBuildOn) {
    // Use context from previous work
    await processTaskWithContext(userInput, relevantMemories);
  } else {
    // Start fresh
    await processTaskFresh(userInput);
  }
}
```

### **Step 4: Save Conversation Summaries**

After completing conversations:

```javascript
// After completing a conversation
async function afterConversation(conversationText, metadata = {}) {
  console.log('💾 Saving conversation summary...');
  
  const saveResult = await memoryIntegration.saveConversationSummary(
    conversationText, 
    {
      title: metadata.title || generateTitleFromConversation(conversationText),
      source: 'claude_desktop',
      technologies: metadata.technologies || extractTechnologies(conversationText),
      complexity: metadata.complexity || assessComplexity(conversationText),
      project: metadata.project || 'general'
    }
  );
  
  if (saveResult.success) {
    console.log(`✅ Conversation saved as memory: ${saveResult.id}`);
    showSuccessNotification('Conversation saved to memory');
  } else {
    console.log('❌ Failed to save conversation:', saveResult.error);
    showErrorNotification('Failed to save conversation');
  }
}

// Example helper functions
function generateTitleFromConversation(text) {
  // Extract meaningful title from conversation
  const lines = text.split('\n').filter(line => line.trim().length > 0);
  return lines[0].substring(0, 100) + (lines[0].length > 100 ? '...' : '');
}

function extractTechnologies(text) {
  // Simple technology detection
  const techKeywords = {
    'react': /react|jsx|component/i,
    'typescript': /typescript|tsx|type/i,
    'javascript': /javascript|js|node/i,
    'python': /python|py|django|flask/i,
    'database': /sql|database|postgres|mysql/i
  };
  
  const technologies = [];
  for (const [tech, regex] of Object.entries(techKeywords)) {
    if (regex.test(text)) {
      technologies.push(tech);
    }
  }
  
  return technologies;
}
```

### **Step 5: Memory Status Display**

Add a memory system status indicator:

```javascript
// Create memory status indicator
async function createMemoryStatusWidget() {
  const statusContainer = document.createElement('div');
  statusContainer.id = 'memory-status';
  statusContainer.style.cssText = `
    position: fixed;
    top: 10px;
    right: 10px;
    background: #f0f0f0;
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 10px;
    font-family: monospace;
    font-size: 12px;
    z-index: 1000;
  `;
  
  // Update status periodically
  const updateStatus = async () => {
    const status = await memoryIntegration.createMemoryStatusIndicator();
    
    statusContainer.innerHTML = `
      <div><strong>Memory System</strong></div>
      <div>Status: ${status.connected ? '🟢 Connected' : '🔴 Disconnected'}</div>
      <div>Documents: ${status.documentCount}</div>
      <div>Last Check: ${new Date(status.lastCheck).toLocaleTimeString()}</div>
    `;
    
    statusContainer.style.background = status.connected ? '#e8f5e8' : '#f5e8e8';
  };
  
  // Initial update
  await updateStatus();
  
  // Update every 30 seconds
  setInterval(updateStatus, 30000);
  
  // Add to page
  document.body.appendChild(statusContainer);
}

// Initialize status widget when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', createMemoryStatusWidget);
} else {
  createMemoryStatusWidget();
}
```

---

## 🔧 **Advanced Integration Options**

### **Custom Memory Search**

For more advanced search functionality:

```javascript
// Advanced memory search with filters
async function advancedMemorySearch(query, options = {}) {
  const searchParams = {
    query: query,
    max_results: options.maxResults || 5,
    similarity_threshold: options.threshold || 0.3,
    source_filter: options.source || null  // 'claude_code' or 'claude_desktop'
  };
  
  const response = await memoryClient.search(query, searchParams);
  
  if (response.success) {
    // Filter results by additional criteria
    let filteredResults = response.results;
    
    if (options.technologies) {
      filteredResults = filteredResults.filter(memory => 
        options.technologies.some(tech => 
          memory.metadata.technologies.includes(tech)
        )
      );
    }
    
    if (options.complexity) {
      filteredResults = filteredResults.filter(memory => 
        memory.metadata.complexity === options.complexity
      );
    }
    
    return filteredResults;
  }
  
  return [];
}

// Usage example
const results = await advancedMemorySearch('component development', {
  maxResults: 3,
  threshold: 0.5,
  technologies: ['react', 'typescript'],
  complexity: 'high'
});
```

### **Memory Analytics**

Track memory usage and effectiveness:

```javascript
// Memory analytics helper
class MemoryAnalytics {
  constructor(memoryClient) {
    this.client = memoryClient;
    this.searchHistory = [];
  }
  
  async trackSearch(query, results) {
    this.searchHistory.push({
      timestamp: new Date().toISOString(),
      query: query,
      resultCount: results.length,
      topSimilarity: results.length > 0 ? results[0].similarity : 0
    });
    
    // Limit history size
    if (this.searchHistory.length > 100) {
      this.searchHistory = this.searchHistory.slice(-100);
    }
  }
  
  getSearchAnalytics() {
    const totalSearches = this.searchHistory.length;
    const avgResults = this.searchHistory.reduce((sum, search) => 
      sum + search.resultCount, 0) / totalSearches;
    const avgSimilarity = this.searchHistory.reduce((sum, search) => 
      sum + search.topSimilarity, 0) / totalSearches;
    
    return {
      totalSearches,
      averageResults: avgResults.toFixed(2),
      averageSimilarity: (avgSimilarity * 100).toFixed(1) + '%'
    };
  }
}

// Initialize analytics
const analytics = new MemoryAnalytics(memoryClient);
```

---

## 🧪 **Testing Integration**

Test your integration:

```javascript
// Integration test suite
async function testMemoryIntegration() {
  console.log('🧪 Testing Memory Integration...');
  
  // Test 1: Health Check
  const health = await memoryClient.getHealth();
  console.log('✓ Health Check:', health.success ? 'PASS' : 'FAIL');
  
  // Test 2: Search
  const searchResults = await memoryClient.search('test query');
  console.log('✓ Search:', searchResults.success ? 'PASS' : 'FAIL');
  
  // Test 3: Add Memory
  const addResult = await memoryClient.addMemory('Test memory content', {
    title: 'Integration Test',
    source: 'claude_desktop'
  });
  console.log('✓ Add Memory:', addResult.success ? 'PASS' : 'FAIL');
  
  // Test 4: List Memories
  const listResult = await memoryClient.listMemories();
  console.log('✓ List Memories:', listResult.success ? 'PASS' : 'FAIL');
  
  console.log('🧪 Integration tests complete');
}

// Run tests
testMemoryIntegration();
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **API Server Not Running**
   ```javascript
   // Check if server is accessible
   const health = await memoryClient.getHealth();
   if (!health.success) {
     console.error('Memory API server is not running');
     console.log('Start with: python memory_api_server.py');
   }
   ```

2. **CORS Issues**
   - Ensure the API server includes your domain in CORS origins
   - Check browser console for CORS errors

3. **Search Returns No Results**
   - Lower similarity threshold: `{"similarity_threshold": 0.1}`
   - Check if memories exist: `GET /api/memories`
   - Verify search terms are meaningful

### **Debug Mode**

Enable debug mode for detailed logging:

```javascript
const memoryClient = new ClaudeMemoryClient('http://localhost:8080', { 
  debug: true  // Enable detailed logging
});
```

---

## 📊 **Monitoring & Maintenance**

### **Health Monitoring**

```javascript
// Monitor system health
setInterval(async () => {
  const health = await memoryClient.getHealth();
  
  if (!health.success) {
    console.warn('⚠️ Memory system health check failed');
    // Implement notification or fallback
  } else {
    console.log(`✅ Memory system healthy: ${health.database.document_count} documents`);
  }
}, 60000); // Check every minute
```

### **Performance Monitoring**

```javascript
// Track API performance
const performanceTracker = {
  searchTimes: [],
  
  async timedSearch(query, options) {
    const start = performance.now();
    const result = await memoryClient.search(query, options);
    const duration = performance.now() - start;
    
    this.searchTimes.push(duration);
    
    if (duration > 2000) { // Log slow searches
      console.warn(`🐌 Slow search: ${duration.toFixed(2)}ms for "${query}"`);
    }
    
    return result;
  },
  
  getAverageSearchTime() {
    const avg = this.searchTimes.reduce((a, b) => a + b, 0) / this.searchTimes.length;
    return avg.toFixed(2) + 'ms';
  }
};
```

---

This integration guide provides everything needed to connect both Claude Code CLI and Claude Desktop to the Memory API system. The integration ensures conversation continuity and builds on previous work automatically.