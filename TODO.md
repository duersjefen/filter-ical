# TODO — iCal Viewer

## 🚨 Next Priority (Choose One)
> **Pick the most impactful item that solves real user problems**

- [ ] **Data Quality**: Remove invalid calendars, validate iCal URLs before adding
- [ ] **User Experience**: Add calendar sync status indicators (last sync, errors)

## 🎯 Medium Priority (Feature Improvements)
> **Enhance core functionality - do after fixing critical issues**

- [ ] Allow multiple saved filters per calendar with simple UX
- [ ] Implement proper server setup for real-time filtered iCal serving
- [ ] Support calendar sharing between users  
- [ ] Add fuzzy search across event descriptions
- [ ] Multi-language support (English/German)

## 📚 Documentation & Polish (Low Priority)
> **Important but not user-facing - do when core features are stable**

- [ ] Create API.md and DEVELOPMENT.md documentation
- [ ] Add basic performance monitoring (response times)
- [ ] Add dependency security scanning (pip-audit, npm audit)

## ✅ Recently Completed (2024)

### **Major Architecture Improvements**
- [x] **Break down CalendarView.vue** (1695 → 169 lines, 90% reduction)
- [x] **Clean frontend architecture** (composables, feature-based components)
- [x] **Verify exclude mode works** (backend already implemented + tested)
- [x] **Add .env.example** for environment management

### **Core Features**
- [x] Category-based filtering system with premium UI
- [x] Include/exclude mode switching with auto-inversion  
- [x] Advanced preview with sorting and grouping
- [x] Responsive card-based interface
- [x] Professional design system with gradients and animations
- [x] Enhanced statistics display (4 statistics cards)
- [x] Proper iCal file generation and download

## 🚀 Future Ideas (Not Prioritized)
> **Dream features - only implement if core app is perfect and users are requesting**
 
### UX Enhancements
- [ ] Dark mode toggle
- [ ] PWA capabilities for mobile
- [ ] Keyboard shortcuts (Ctrl+A, etc.)
- [ ] Drag & drop category selection
- [ ] Undo/redo functionality

### Intelligence Features  
- [ ] Smart recommendations ("users who selected X also selected Y")
- [ ] Calendar health score analysis
- [ ] AI-powered filter creation
- [ ] Usage analytics and user patterns

### Technical Nice-to-Haves
- [ ] Code formatting/linting setup
- [ ] Lazy loading for huge calendars
- [ ] Debounced search optimization


---

## 📋 Done ✓ (Historical Archive)
<details>
<summary>Previously completed features</summary>

- [x] Basic calendar subscription and display
- [x] Event caching for performance  
- [x] User isolation and data persistence
- [x] Comprehensive backend API tests
- [x] Test data isolation
- [x] Fix login page reload issue
- [x] Add basic E2E smoke test
- [x] Ability to remove entire calendars
- [x] Smart category selection buttons
- [x] Time display fixes in dropdowns
- [x] Collapsible single-event categories section

</details>

---

**🎯 Focus**: Pick ONE item from "Next Priority" and complete it fully before moving to the next. Quality over quantity.