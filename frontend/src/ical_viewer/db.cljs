(ns ical-viewer.db)

(def default-db
  {:current-view :login
   :user {:username nil :logged-in? false}
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
   :login-form {:username ""}
   :loading? false
   :error nil
   :statistics {:total-events 0
                :event-types 0
                :years-covered 0}})