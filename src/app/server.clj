(ns app.server
  (:gen-class)
  (:require [compojure.core :refer [defroutes GET POST]]
            [compojure.route :as route]
            [ring.adapter.jetty :refer [run-jetty]]
            [ring.middleware.params :refer [wrap-params]]
            [ring.util.response :as response]
            [hiccup.page :refer [html5]]
            [hiccup.form :refer [form-to label text-field submit-button hidden-field check-box]]
            [app.storage :as storage]
            [app.ics :as ics]
            [clojure.string :as str]))

(defn layout [title & body]
  (html5
   [:head
    [:meta {:charset "utf-8"}]
    [:meta {:name "viewport" :content "width=device-width,initial-scale=1"}]
    [:title title]
    [:style "
      body { font-family: system-ui, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
      .calendar-list { display: flex; flex-wrap: wrap; gap: 20px; }
      .calendar-card { border: 1px solid #ccc; padding: 15px; border-radius: 5px; min-width: 250px; }
      .events-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
      .events-table th, .events-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
      .events-table th { background-color: #f2f2f2; }
      .group-header { background-color: #e9e9e9; font-weight: bold; }
      .btn { padding: 8px 12px; margin: 5px; border: 1px solid #ccc; background: white; cursor: pointer; }
      .btn:hover { background: #f0f0f0; }
      .btn-primary { background: #007bff; color: white; }
    "]]
   [:body body]))

(defn home-page []
  (layout "iCal Viewer"
          [:h1 "iCal Viewer"]
          [:div
           [:h2 "Add New Calendar"]
           (form-to [:post "/add"]
                    [:div
                     (label "name" "Name: ")
                     (text-field {:placeholder "My Calendar"} "name")]
                    [:div
                     (label "url" "iCal URL: ")
                     (text-field {:placeholder "https://example.com/calendar.ics" :size 60} "url")]
                    [:div (submit-button {:class "btn btn-primary"} "Add Calendar")])]

          [:hr]

          [:h2 "Saved Calendars"]
          (if (seq (storage/all-entries))
            [:div.calendar-list
             (for [entry (storage/all-entries)]
               [:div.calendar-card
                [:h3 (:name entry)]
                [:p [:small (:url entry)]]
                [:div
                 [:a {:href (str "/view/" (:id entry)) :class "btn"} "View Events"]
                 (form-to [:post (str "/delete/" (:id entry))]
                          [:input {:type "submit" :value "Delete" :class "btn"
                                   :onclick "return confirm('Are you sure?')"}])]])]
            [:p "No calendars added yet. Add one above to get started!"])))

(defn group-events-by-summary [events]
  (group-by :summary events))

(defn view-page [entry events]
  (let [grouped-events (group-events-by-summary events)]
    (layout (str "View: " (:name entry))
            [:p [:a {:href "/" :class "btn"} "← Back to Home"]]
            [:h2 (:name entry)]
            [:p [:small "URL: " (:url entry)]]

            (if (seq events)
              [:div
               (form-to [:post "/generate"]
                        (hidden-field "entry-id" (:id entry))

                        [:h3 "Events (grouped by summary)"]
                        [:table.events-table
                         [:thead
                          [:tr
                           [:th "Select"]
                           [:th "Summary"]
                           [:th "Start"]
                           [:th "End"]
                           [:th "Location"]]]
                         [:tbody
                          (for [[summary group-events] grouped-events]
                            (list
                             [:tr.group-header
                              [:td {:colspan 5}
                               [:strong summary " (" (count group-events) " events)"]]]
                             (for [event group-events]
                               [:tr
                                [:td (check-box "selected" (:uid event))]
                                [:td (:summary event)]
                                [:td (:dtstart event)]
                                [:td (:dtend event)]
                                [:td (:location event)]])))]]

                        [:div
                         [:input {:type "submit" :value "Generate Filtered .ics" :class "btn btn-primary"}]])]
              [:p "No events found for this calendar."]))))

(defroutes routes
  (GET "/" [] (home-page))

  (POST "/add" {params :params}
    (let [name (get params "name")
          url (get params "url")]
      (if (and (not (str/blank? name)) (not (str/blank? url)))
        (do
          (storage/add-entry! name url)
          (response/redirect "/"))
        (response/redirect "/"))))

  (POST "/delete/:id" [id]
    (storage/delete-entry! id)
    (response/redirect "/"))

  (GET "/view/:id" [id]
    (if-let [entry (storage/get-entry id)]
      (let [events (ics/events-for-url (:url entry))]
        (view-page entry events))
      (response/redirect "/")))

  (POST "/generate" {params :params}
    (let [entry-id (get params "entry-id")
          selected-uids (let [sel (get params "selected")]
                          (cond
                            (nil? sel) []
                            (string? sel) [sel]
                            :else (vec sel)))
          entry (storage/get-entry entry-id)]

      (if entry
        (let [all-events (ics/events-for-url (:url entry))
              selected-events (filter #(contains? (set selected-uids) (:uid %)) all-events)]
          (if (seq selected-events)
            {:status 200
             :headers {"Content-Type" "text/calendar"
                       "Content-Disposition" (str "attachment; filename=\"filtered-" (:name entry) ".ics\"")}
             :body (ics/build-calendar selected-events)}
            (response/redirect (str "/view/" entry-id))))
        (response/redirect "/"))))

  (route/not-found "Page not found"))

(def app (wrap-params routes))

(defn start-server! [& [port]]
  (let [port (or port 3000)]
    (println "Starting iCal Viewer server on port" port)
    (println "Open http://localhost:" port " in your browser")
    (run-jetty app {:port port :join? false})))

(defn -main [& args]
  (let [port (if (seq args) (Integer/parseInt (first args)) 3000)]
    (start-server! port)
    @(promise)))
