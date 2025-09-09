;; === ENHANCED UI COMPONENTS ===
;; Modern interface components with smart filtering - Main module

(ns app.ui.components
  (:require [app.ui.filter-builder :as filter-builder]
            [app.ui.event-display :as event-display]
            [app.ui.styles :as styles]))

;; Re-export main components for backward compatibility
(def event-type-selector filter-builder/event-type-selector)
(def smart-filter-builder filter-builder/smart-filter-builder)
(def filter-card filter-builder/filter-card)

(def event-statistics event-display/event-statistics)
(def event-list-view event-display/event-list-view)
(def view-mode-selector event-display/view-mode-selector)
(def action-panel event-display/action-panel)

(def enhanced-styles styles/enhanced-styles)
(def filter-javascript styles/filter-javascript)

;; === COMPLETE UI LAYOUT ===

(defn complete-filter-interface
  "Complete filtering interface with all components"
  [events calendar-id & [selected-summaries]]
  [:div.complete-filter-interface
   ;; Search and filter controls placeholder
   
   ;; Statistics panel
   (let [grouped-events (app.core.filtering/group-by-summary events)]
     [:div
      (event-display/event-statistics events grouped-events)
      
      ;; Smart filter builder
      (filter-builder/smart-filter-builder events calendar-id selected-summaries)
      
      ;; View mode selector
      (event-display/view-mode-selector)
      
      ;; Event display (default table view)
      (event-display/event-list-view grouped-events "table")
      
      ;; Action panel
      (event-display/action-panel calendar-id)])])

;; === PAGE LAYOUT HELPERS ===

(defn page-with-styles
  "Wrap page content with required styles and JavaScript"
  [title content]
  [:html
   [:head
    [:title title]
    [:meta {:charset "utf-8"}]
    [:meta {:name "viewport" :content "width=device-width, initial-scale=1"}]
    [:style styles/enhanced-styles]]
   [:body
    content
    [:script styles/filter-javascript]]])

(defn filter-management-page
  "Complete page for managing saved filters"
  [filters calendars]
  (page-with-styles
    "Manage Filters"
    [:div.container
     [:h1 "📂 Saved Filters"]
     [:div.filters-grid
      (for [filter filters]
        (let [calendar (first (filter #(= (:id %) (:calendar-id filter)) calendars))
              calendar-name (or (:name calendar) "Unknown Calendar")]
          (filter-builder/filter-card filter calendar-name)))]]))