(ns ical-viewer.db)

(def default-db
  {:current-view :home
   :events []
   :grouped-events {}
   :calendars []
   :selected-calendar nil
   :selected-calendar-id nil
   :filters []
   :selected-event-types #{}
   :view-mode "table"
   :search-text ""
   :date-from nil
   :date-to nil
   :new-calendar {:name "" :url ""}
   :loading? false
   :error nil
   :statistics {:total-events 0
                :event-types 0
                :years-covered 0}})