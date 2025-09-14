# TODO — iCal Viewer

## ⚡ Quick Capture
> **Drop new ideas here without thinking about priority - sort later!**

- I don't like the design of the renaming icon, and does it make sense to rename it where it is, without a toast notification?

## 🚨 NEXT UP (Pick One & Focus)
> **Most impactful items that solve real user problems**

- [ ] **Fix "Create Calendar" functionality** - Currently not working and showing individual files instead of clear inclusion logic
- [ ] **Fix filter logic display** - "🔍 Filter Logic:📋 ALL EVENTS" must be precise and clear

## 🎯 HIGH PRIORITY (After Current Focus)
> **Core functionality improvements - high user impact**

- [ ] **Generate working iCal links** - Ensure filtered calendars produce functional iCal URLs
- [ ] **Individual events inclusion logic** - Clear UX for whether new events are included, with granular control
- [ ] **Fix double loading cards** in the calendar view  
- [ ] **User Experience**: Add calendar sync status indicators (last sync, errors)
- [ ] Allow multiple saved filters per calendar with simple UX
- [ ] Implement proper server setup for real-time filtered iCal serving
- [ ] **Simple default calendar UX**: Create `exter.filter-ical.de` for users who only need the default calendar (better UX for most people)
- [ ] Support calendar sharing between users

## 🔧 MEDIUM PRIORITY (Polish & Quality)
> **Important improvements when core features are stable**

- [ ] **Improve filter/calendar editing UX** - Combine preview and edit mode, clear "edit mode" indicators
- [ ] **Refactor main.py** - Assess complexity and break down if needed
- [ ] **Improve naming consistency** - "Filtered calendars" vs "filters" - clarify terminology
- [ ] Create API.md and DEVELOPMENT.md documentation
- [ ] Add basic performance monitoring (response times)  
- [ ] Add dependency security scanning (pip-audit, npm audit)


## 💡 FUTURE IDEAS (Someday/Maybe)
> **Dream features - only consider when core app is perfect**

### 🤖 Intelligence Features
- [ ] **SICP Chapter 2 connection** - Explore links between data abstraction and backend API design
- [ ] Smart recommendations ("users who selected X also selected Y")
- [ ] Calendar health score analysis
- [ ] AI-powered filter creation
- [ ] Usage analytics and user patterns

### 💫 UX Enhancements
- [ ] PWA capabilities for mobile
- [ ] Keyboard shortcuts (Ctrl+A, etc.)
- [ ] Drag & drop category selection
- [ ] Undo/redo functionality

### ⚙️ Technical Nice-to-Haves
- [ ] Code formatting/linting setup
- [ ] Lazy loading for huge calendars
- [ ] Debounced search optimization

---

## 📝 HOW TO USE THIS TODO

**🎯 Daily Workflow:**
1. **Quick Capture** → Add new ideas without overthinking
2. **Focus on "NEXT UP"** → Pick ONE item and complete it fully
3. **Remove completed items** → Finished tasks are deleted (git tracks completion)
4. **Weekly review** → Sort "Quick Capture" into priority sections

**💡 Tips for Success:**
- Focus on one item at a time - quality over quantity
- Clean up completed items immediately to maintain focus
- Review priorities weekly to keep aligned with user needs
- Keep "Future Ideas" collapsed to avoid distraction