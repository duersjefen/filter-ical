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
      body { font-family: system-ui, sans-serif; max-width: 1400px; margin: 0 auto; padding: 20px; background: #f8f9fa; }
      .header { text-align: center; margin-bottom: 30px; }
      .header h1 { color: #2c3e50; margin-bottom: 10px; }
      .subtitle { color: #6c757d; margin-bottom: 30px; }
      
      .calendar-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
      .calendar-card { background: white; border: 1px solid #dee2e6; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
      .calendar-card h3 { margin-top: 0; color: #495057; }
      .calendar-url { color: #6c757d; font-size: 0.9em; word-break: break-all; }
      
      .form-section { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }
      .form-row { margin-bottom: 15px; }
      .form-row label { display: block; margin-bottom: 5px; font-weight: 500; color: #495057; }
      .form-row input[type='text'] { width: 100%; max-width: 500px; padding: 8px 12px; border: 1px solid #ced4da; border-radius: 4px; }
      
      .events-section { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
      .filter-controls { margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px; }
      .filter-actions { display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap; }
      
      .events-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
      .events-table th, .events-table td { border: 1px solid #dee2e6; padding: 12px 8px; text-align: left; }
      .events-table th { background-color: #f8f9fa; font-weight: 600; color: #495057; }
      .group-header { background-color: #e9ecef; font-weight: bold; }
      .group-header td { padding: 10px 8px; }
      .event-row:nth-child(even) { background-color: #f8f9fa; }
      
      .btn { padding: 8px 16px; margin: 5px; border: 1px solid #ced4da; background: white; cursor: pointer; border-radius: 4px; text-decoration: none; display: inline-block; font-size: 14px; }
      .btn:hover { background: #e9ecef; }
      .btn-primary { background: #007bff; color: white; border-color: #007bff; }
      .btn-primary:hover { background: #0056b3; }
      .btn-success { background: #28a745; color: white; border-color: #28a745; }
      .btn-success:hover { background: #1e7e34; }
      .btn-danger { background: #dc3545; color: white; border-color: #dc3545; }
      .btn-danger:hover { background: #c82333; }
      .btn-secondary { background: #6c757d; color: white; border-color: #6c757d; }
      .btn-secondary:hover { background: #545b62; }
      
      .saved-filters { margin-top: 20px; }
      .filter-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #f8f9fa; margin: 5px 0; border-radius: 4px; }
      .subscription-info { background: #d1ecf1; padding: 15px; border-radius: 4px; margin: 15px 0; }
      .subscription-url { font-family: monospace; background: #f8f9fa; padding: 8px; border-radius: 4px; word-break: break-all; }
      
      .stats { display: flex; gap: 20px; margin: 15px 0; }
      .stat { text-align: center; }
      .stat-number { font-size: 1.5em; font-weight: bold; color: #007bff; }
      .stat-label { font-size: 0.9em; color: #6c757d; }
    "]]
   [:body body]))

(defn home-page []
  (let [entries (storage/all-entries)
        total-filters (count (storage/all-filters))]
    (layout "iCal Filter & Subscribe"
            [:div.header
             [:h1 "🗓️ iCal Filter & Subscribe"]
             [:p.subtitle "Easily filter your iCal feeds and create custom subscriptions"]]
            
            [:div.form-section
             [:h2 "Add New Calendar"]
             (form-to [:post "/add"]
                      [:div.form-row
                       (label "name" "Calendar Name")
                       (text-field {:placeholder "My Work Calendar"} "name")]
                      [:div.form-row
                       (label "url" "iCal URL")
                       (text-field {:placeholder "https://example.com/calendar.ics"} "url")]
                      [:div.form-row
                       (submit-button {:class "btn btn-primary"} "Add Calendar")])]
            
            (if (seq entries)
              [:div
               [:h2 "Your Calendars (" (count entries) ")"]
               (when (> total-filters 0)
                 [:div.stats
                  [:div.stat
                   [:div.stat-number (count entries)]
                   [:div.stat-label "Calendars"]]
                  [:div.stat
                   [:div.stat-number total-filters]
                   [:div.stat-label "Saved Filters"]]])
               
               [:div.calendar-list
                (for [entry entries]
                  (let [calendar-filters (storage/filters-for-calendar (:id entry))]
                    [:div.calendar-card
                     [:h3 (:name entry)]
                     [:p.calendar-url (:url entry)]
                     [:div.stats
                      (when (seq calendar-filters)
                        [:div.stat
                         [:div.stat-number (count calendar-filters)]
                         [:div.stat-label "Saved Filters"]])]
                     [:div
                      [:a {:href (str "/view/" (:id entry)) :class "btn btn-primary"} "📊 Filter Events"]
                      (form-to [:post (str "/delete/" (:id entry))]
                               [:input {:type "submit" :value "🗑️ Delete" :class "btn btn-danger"
                                        :onclick "return confirm('Delete this calendar and all its filters?')"}])]]))]]
              [:div.form-section
               [:h2 "Get Started"]
               [:p "Add your first iCal feed above to start filtering events and creating custom subscriptions."]
               [:p "You can filter by event types, save your filters, and get a subscription URL to use in any calendar app."]]))))

(defn group-events-by-summary [events]
  (group-by :summary events))

(defn view-page [entry events & [selected-filter-id]]
  (let [grouped-events (group-events-by-summary events)
        saved-filters (storage/filters-for-calendar (:id entry))
        selected-filter (when selected-filter-id (storage/get-filter selected-filter-id))]
    (layout (str "Filter: " (:name entry))
            [:div
             [:a {:href "/" :class "btn btn-secondary"} "← Back to Home"]
             [:h2 "📊 " (:name entry)]
             [:p.calendar-url (:url entry)]]

            (if (seq events)
              [:div.events-section
               [:div.filter-controls
                [:h3 "Quick Actions"]
                [:div.filter-actions
                 [:button {:onclick "selectAll()" :class "btn"} "✅ Select All"]
                 [:button {:onclick "selectNone()" :class "btn"} "❌ Select None"]
                 [:button {:onclick "selectByKeyword()" :class "btn"} "🔍 Select by Keyword"]]
                
                (when (seq saved-filters)
                  [:div.saved-filters
                   [:h4 "📋 Saved Filters (" (count saved-filters) ")"]
                   (for [filter saved-filters]
                     [:div.filter-item
                      [:div
                       [:strong (:name filter)]
                       [:small " (" (count (:selected-summaries filter)) " event types)"]]
                      [:div
                       [:a {:href (str "/view/" (:id entry) "?filter=" (:id filter)) :class "btn btn-primary"} "📊 Apply"]
                       [:a {:href (str "/filter/info/" (:id filter)) :class "btn btn-success"} "🔗 Subscribe"]
                       (form-to [:post (str "/filter/delete/" (:id filter))]
                                [:input {:type "submit" :value "🗑️" :class "btn btn-danger"
                                         :onclick "return confirm('Delete this saved filter?')"}])]])])]
               
               (form-to [:post "/filter/save"]
                        (hidden-field "entry-id" (:id entry))
                        
                        [:div.stats
                         [:div.stat
                          [:div.stat-number (count events)]
                          [:div.stat-label "Total Events"]]
                         [:div.stat
                          [:div.stat-number (count grouped-events)]
                          [:div.stat-label "Event Types"]]]

                        [:h3 "📅 Events by Type"]
                        [:table.events-table
                         [:thead
                          [:tr
                           [:th "Select"]
                           [:th "Event Type"]
                           [:th "Count"]
                           [:th "Sample Dates"]]]
                         [:tbody
                          (for [[summary group-events] (sort-by first grouped-events)]
                            (let [is-selected (if selected-filter
                                              (contains? (set (:selected-summaries selected-filter)) summary)
                                              false)]
                              [:tr.group-header
                               [:td (check-box "selected-summaries" summary is-selected)]
                               [:td [:strong summary]]
                               [:td (count group-events) " events"]
                               [:td (->> group-events
                                        (take 3)
                                        (map #(or (:dtstart %) "No date"))
                                        (str/join ", "))]]))]]

                        [:div.filter-actions
                         [:div.form-row
                          (label "filter-name" "Save this filter as:")
                          (text-field {:placeholder "My Custom Filter"} "filter-name")]
                         [:input {:type "submit" :value "💾 Save Filter" :class "btn btn-success"}]
                         [:input {:type "submit" :name "action" :value "📥 Download .ics" :class "btn btn-primary"}]])]
              [:div.form-section
               [:h3 "⚠️ No Events Found"]
               [:p "This calendar appears to be empty or the URL might be invalid."]])
            
            [:script "
              function selectAll() {
                document.querySelectorAll('input[name=\"selected-summaries\"]').forEach(cb => cb.checked = true);
              }
              function selectNone() {
                document.querySelectorAll('input[name=\"selected-summaries\"]').forEach(cb => cb.checked = false);
              }
              function selectByKeyword() {
                const keyword = prompt('Enter keyword to select (case insensitive):');
                if (keyword) {
                  document.querySelectorAll('input[name=\"selected-summaries\"]').forEach(cb => {
                    const row = cb.closest('tr');
                    const summary = row.querySelector('td:nth-child(2)').textContent;
                    cb.checked = summary.toLowerCase().includes(keyword.toLowerCase());
                  });
                }
              }
            "])))

(defn subscription-info-page [filter]
  (let [entry (storage/get-entry (:calendar-id filter))
        base-url "http://localhost:9000"
        subscription-url (str base-url "/subscribe/" (:id filter))]
    (layout (str "Subscribe: " (:name filter))
            [:div
             [:a {:href (str "/view/" (:calendar-id filter)) :class "btn btn-secondary"} "← Back to Calendar"]
             [:h2 "🔗 " (:name filter)]
             [:p "Subscription for: " [:strong (:name entry)]]]
            
            [:div.subscription-info
             [:h3 "📋 Filter Details"]
             [:p "This filter includes events of these types:"]
             [:ul (for [summary (:selected-summaries filter)]
                    [:li summary])]
             [:p [:small "Created: " (java.util.Date. (:created-at filter))]]]
            
            [:div.subscription-info
             [:h3 "🔗 Subscription URL"]
             [:p "Copy this URL and add it to your calendar application:"]
             [:div.subscription-url subscription-url]
             [:div.filter-actions
              [:button {:onclick (str "navigator.clipboard.writeText('" subscription-url "')") :class "btn btn-primary"} "📋 Copy URL"]
              [:a {:href subscription-url :class "btn btn-success"} "📥 Download .ics"]]]
            
            [:div.form-section
             [:h3 "📱 How to Subscribe"]
             [:h4 "Google Calendar"]
             [:p "1. Open Google Calendar"]
             [:p "2. Click the '+' next to 'Other calendars'"]
             [:p "3. Select 'From URL'"]
             [:p "4. Paste the subscription URL above"]
             
             [:h4 "Apple Calendar (iOS/macOS)"]
             [:p "1. Copy the subscription URL"]
             [:p "2. Open Calendar app"]
             [:p "3. Go to File → New Calendar Subscription (macOS) or Settings → Accounts → Add Account (iOS)"]
             [:p "4. Paste the URL"]
             
             [:h4 "Outlook"]
             [:p "1. In Outlook, go to Calendar"]
             [:p "2. Select 'Add calendar' → 'From internet'"]
             [:p "3. Paste the subscription URL"]])))

(defn filter-events-by-summaries [events selected-summaries]
  (filter #(contains? (set selected-summaries) (:summary %)) events))

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

  (GET "/view/:id" [id & {filter-id :filter}]
    (if-let [entry (storage/get-entry id)]
      (let [events (ics/events-for-url (:url entry))]
        (view-page entry events filter-id))
      (response/redirect "/")))

  (POST "/filter/save" {params :params}
    (let [entry-id (get params "entry-id")
          filter-name (get params "filter-name")
          action (get params "action")
          selected-summaries (let [sel (get params "selected-summaries")]
                             (cond
                               (nil? sel) []
                               (string? sel) [sel]
                               :else (vec sel)))
          entry (storage/get-entry entry-id)]
      
      (cond
        ;; Save filter action
        (and (not (str/blank? filter-name)) (seq selected-summaries))
        (do
          (storage/add-filter! filter-name entry-id selected-summaries)
          (response/redirect (str "/view/" entry-id)))
        
        ;; Download action
        (= action "📥 Download .ics")
        (if (and entry (seq selected-summaries))
          (let [all-events (ics/events-for-url (:url entry))
                selected-events (filter-events-by-summaries all-events selected-summaries)]
            (if (seq selected-events)
              {:status 200
               :headers {"Content-Type" "text/calendar"
                         "Content-Disposition" (str "attachment; filename=\"filtered-" (:name entry) ".ics\"")}
               :body (ics/build-calendar selected-events)}
              (response/redirect (str "/view/" entry-id))))
          (response/redirect (str "/view/" entry-id)))
        
        :else
        (response/redirect (str "/view/" entry-id)))))

  (POST "/filter/delete/:id" [id]
    (storage/delete-filter! id)
    (response/redirect "/"))

  (GET "/filter/info/:filter-id" [filter-id]
    (if-let [filter (storage/get-filter filter-id)]
      (subscription-info-page filter)
      (response/redirect "/")))

  (GET "/subscribe/:filter-id" [filter-id]
    (if-let [filter (storage/get-filter filter-id)]
      (let [entry (storage/get-entry (:calendar-id filter))
            all-events (ics/events-for-url (:url entry))
            filtered-events (filter-events-by-summaries all-events (:selected-summaries filter))]
        {:status 200
         :headers {"Content-Type" "text/calendar"}
         :body (ics/build-calendar filtered-events)})
      {:status 404
       :body "Filter not found"}))

  (route/not-found "Page not found"))

(def app (wrap-params routes))

(defn start-server! [& [port]]
  (let [port (cond
               (nil? port) 3000
               (number? port) port
               (string? port) (try (Integer/parseInt port) (catch Exception _ 3000))
               :else 3000)]
    (println "Starting iCal Viewer server on port" port)
    (println "Open http://localhost:" port " in your browser")
    (run-jetty app {:port port :join? false})))

(defn- find-flag-index [args flags]
  (first (keep-indexed (fn [i v] (when (some #{v} flags) i)) args)))

(defn parse-port-arg [args]
  ;; Return a string port value if present in args. Supports -p, -port, --port or a single numeric arg.
  (when (seq args)
    (let [flags ["-p" "-port" "--port"]]
      (if-let [fi (find-flag-index args flags)]
        (nth args (inc fi) nil)
        (first args)))))

(defn -main [& args]
  (let [port-str (parse-port-arg args)
        port (try (when port-str (Integer/parseInt port-str)) (catch Exception _ nil))]
    (start-server! port)
    @(promise)))
