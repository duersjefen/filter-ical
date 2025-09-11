# Complete Filtering System Implementation Plan

## Current System Analysis
- ✅ Event type checkboxes working
- ✅ Basic UI for filtering
- ❌ Only exact summary matching (no keywords)
- ❌ No timeframe filtering  
- ❌ Saved filters don't work (backend missing)
- ❌ No sorting options

## Phase 1: Fix Foundation (30 min)

### 1.1 Fix Filtering Logic
**File: `frontend/src/stores/app.js`**
```javascript
// Current (broken):
return state.events.filter(event => 
  state.selectedEventTypes.has(event.summary)
)

// New (keyword matching):
return state.events.filter(event => {
  // Event type filtering
  if (state.selectedEventTypes.size > 0) {
    if (!state.selectedEventTypes.has(event.summary)) return false
  }
  
  // Keyword filtering
  if (state.keywordFilter) {
    const searchText = `${event.summary} ${event.description || ''} ${event.location || ''}`.toLowerCase()
    if (!searchText.includes(state.keywordFilter.toLowerCase())) return false
  }
  
  // Date range filtering
  if (state.dateRange.start || state.dateRange.end) {
    const eventDate = new Date(event.dtstart)
    if (state.dateRange.start && eventDate < state.dateRange.start) return false
    if (state.dateRange.end && eventDate > state.dateRange.end) return false
  }
  
  return true
})
```

### 1.2 Add State for New Filters
**File: `frontend/src/stores/app.js`**
```javascript
// Add to state:
keywordFilter: '',
dateRange: { start: null, end: null },
sortBy: 'date', // 'date', 'title', 'matches'
sortDirection: 'asc'
```

### 1.3 Backend: Implement Filter CRUD
**File: `backend/app/main.py`** 
```python
@app.get("/api/filters")
async def get_filters(x_user_id: str = Header("anonymous")):
    # Return user's saved filters from persistent store
    filters = store.get_filters(x_user_id)
    return {"filters": filters}

@app.post("/api/filters")  
async def create_filter(data: dict, x_user_id: str = Header("anonymous")):
    # Save filter to persistent store
    filter_obj = store.add_filter(data["name"], data["config"], x_user_id)
    return {"message": "Filter saved", "id": filter_obj.id}

@app.delete("/api/filters/{filter_id}")
async def delete_filter(filter_id: str, x_user_id: str = Header("anonymous")):
    # Delete filter from persistent store
    if store.delete_filter(filter_id, x_user_id):
        return {"message": "Filter deleted"}
    raise HTTPException(status_code=404, detail="Filter not found")
```

## Phase 2: Enhanced Filtering UI (1 hour)

### 2.1 Add Keyword Search
**File: `frontend/src/views/CalendarView.vue`**
```vue
<!-- Add above event type checkboxes -->
<div class="search-section" style="margin-bottom: 20px;">
  <label for="keyword-search">🔍 Search Events:</label>
  <input 
    id="keyword-search"
    v-model="appStore.keywordFilter" 
    type="text" 
    placeholder="Enter keywords (title, description, location)..."
    class="form-control"
  />
</div>
```

### 2.2 Add Timeframe Presets
```vue
<div class="timeframe-section" style="margin-bottom: 20px;">
  <h4>📅 Timeframe:</h4>
  <div class="btn-group">
    <button @click="setTimeframe('week')" class="btn btn-secondary">This Week</button>
    <button @click="setTimeframe('month')" class="btn btn-secondary">This Month</button>
    <button @click="setTimeframe('year')" class="btn btn-secondary">This Year</button>
    <button @click="clearTimeframe()" class="btn btn-outline">All Time</button>
  </div>
</div>
```

### 2.3 Add Sorting Options
```vue
<div class="sort-section" style="margin-bottom: 20px;">
  <label for="sort-by">Sort by:</label>
  <select v-model="appStore.sortBy" id="sort-by" class="form-control" style="width: auto; display: inline-block;">
    <option value="date">Date</option>
    <option value="title">Title</option>
    <option value="matches">Relevance</option>
  </select>
  <button @click="toggleSortDirection()" class="btn btn-secondary">
    {{ appStore.sortDirection === 'asc' ? '↑' : '↓' }}
  </button>
</div>
```

## Phase 3: Saved Filters Management (45 min)

### 3.1 Saved Filters UI
```vue
<div class="saved-filters-section">
  <h4>💾 Saved Filters:</h4>
  <div v-for="filter in appStore.savedFilters" :key="filter.id" class="saved-filter-item">
    <span>{{ filter.name }}</span>
    <button @click="loadFilter(filter)" class="btn btn-sm">Load</button>
    <button @click="deleteFilter(filter.id)" class="btn btn-sm btn-danger">×</button>
  </div>
  
  <div class="save-new-filter">
    <input v-model="newFilterName" placeholder="Filter name..." />
    <button @click="saveCurrentFilter()" class="btn">Save Current</button>
  </div>
</div>
```

### 3.2 Performance Optimization
```javascript
// Add to store - debounced filtering
const debouncedFilter = debounce((searchTerm) => {
  this.keywordFilter = searchTerm
}, 300)

// Memoized filtering for large datasets
filteredEvents: (state) => {
  return memoize(() => {
    // ... filtering logic
  }, [state.events, state.selectedEventTypes, state.keywordFilter, state.dateRange])
}
```

## Implementation Order
1. ✅ Fix basic keyword filtering (15 min)
2. ✅ Add keyword search input (10 min) 
3. ✅ Add timeframe presets (15 min)
4. ✅ Backend filter CRUD (20 min)
5. ✅ Saved filters UI (30 min)
6. ✅ Sorting options (20 min)
7. ✅ Performance optimization (15 min)

**Total: ~2 hours for complete filtering system**

## Success Criteria
- ✅ Search by keywords in title/description/location
- ✅ Quick timeframe selection (week/month/year)
- ✅ Save and manage multiple filters per calendar
- ✅ Sort results by date/title/relevance
- ✅ Fast performance with large calendars (>1000 events)
- ✅ Intuitive UX - discoverable and simple