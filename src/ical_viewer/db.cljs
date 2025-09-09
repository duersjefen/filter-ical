(ns ical-viewer.db)

(def default-db
  {:events []
   :calendars []
   :filters []
   :selected-calendar-id nil
   :selected-event-types #{}
   :view-mode "table"
   :search-text ""
   :date-from nil
   :date-to nil
   :loading? false
   :error nil
   :statistics {:total-events 0
                :event-types 0
                :years-covered 0}})