# TODO — iCal Viewer

## ⚡ Quick Capture
> **Drop new ideas here without thinking about priority - sort later!**


## 🚨 NEXT UP (Pick One & Focus)
> **Most impactful items that solve real user problems**


## 🎯 HIGH PRIORITY (After Current Focus)
> **Core functionality improvements - high user impact**



## 🔧 MEDIUM PRIORITY (Polish & Quality)
> **Important improvements when core features are stable**

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

The big overview: We want to be able to create community calenders which are customizable by admins. They get there own url (i.e. 
  /exter) and a password to protect it. On these community websites, there is 1 calender available, which the user can create filters 
  for. The user must be able to subscribe to groups (which are created partially automatically, and adjusted by the admins), which 
  contain categories (which mainly are the single events, grouped by name). The user must also be able to indiviudally subsribe or 
  unsubscribe from categories (i.e. he wants all new football categories, but explicitly unsubscribes for U16 and Girls U23). One 
  category will be in different groups, but that doesn't matter. If he unsubscribes from a category, it will show as unsubscribed in all 
  groups. We still have an include and exclude mode, as some users want "all events, but not youth events", and some want "only football 
  and youth events". This combination of mode, groups and categories can be used by the user to create a filter, just as we have on the 
  normal website, with the small adition that we know also must show the user which groups he is subscribed to. \
  \
  When new categories are added to the calender, it will be automatically (or by an admin) added to a group in the database, and the 
  users that are either "not unsubscribed to that group or category", or which are "subscribed to that group", will get all the events in
   that category in his personal ICAL link.\
  \
  Does that make sense?
