;; src/ical_viewer/core.clj
;; Plumbing: HTTP routes, server lifecycle, and a tiny non-JS UI.
(ns ical-viewer.core
  (:require [ring.adapter.jetty :refer [run-jetty]]
            [ring.middleware.params :refer [wrap-params]]
            [compojure.core :refer [defroutes GET POST]]
            [compojure.route :as route]
            [hiccup.page :refer [html5]]
            [ical-viewer.logic :as logic]
            [clojure.string :as str]))

;; -- Minimal HTML UI (non-JS fallback) --
(defn layout [body]
  (html5
   [:head
    [:title "iCal Viewer"]]
   [:body body]))

(defn form-page []
  (layout
   [:div
    [:h1 "iCal Viewer"]
    [:form {:method "post" :action "/parse"}
     [:label "Enter iCal URL: "]
     [:input {:type "text" :name "ics-url" :size 60}]
     [:br]
     [:label "Save as name (optional): "]
     [:input {:type "text" :name "name" :size 30}]
     [:br]
     [:button {:type "submit"} "Load Events"]]
    [:p [:a {:href "/entries/first"} "View events for first saved entry"]]]))

(defn table-page [events]
  (layout
   [:div
    [:p [:a {:href "/"} "← back"]]
    (if (seq events)
      [:table
       [:thead [:tr [:th "Summary"] [:th "Start"] [:th "End"] [:th "Location"]]]
       [:tbody (for [{:keys [summary dtstart dtend location]} events]
                 [:tr [:td (or summary "")] [:td (or dtstart "")] [:td (or dtend "")] [:td (or location "")]])]]
      [:p "No events found."])]))

;; -- Routes --
(defroutes app-routes
  (GET "/" [] (form-page))

  (POST "/parse" {params :params}
    (let [url  (get params "ics-url")
          name (get params "name")
          events (logic/fetch-and-parse url)]
      (when (and name (not (str/blank? name)))
        (logic/save-entry! name url))
      (table-page events)))

  ;; Show events for the first saved entry
  (GET "/entries/first" []
    (let [entries (logic/entries-with-events)
          first-entry (first entries)]
      (if first-entry
        (table-page (:events first-entry))
        (layout [:p "No entries saved."]))))

  ;; API: return saved entries as EDN
  (GET "/api/entries" {params :params}
    (let [year (some-> (get params "year") (Integer/parseInt))]
      {:status 200
       :headers {"Content-Type" "application/edn"}
       :body (pr-str (logic/list-entries year))}))

  ;; API: return events for the first saved entry (as EDN)
  (GET "/api/entries/first" {params :params}
    (let [year (some-> (get params "year") (Integer/parseInt))
          entries (logic/entries-with-events year)
          first-entry (first entries)
          events (or (:events first-entry) [])]
      {:status 200
       :headers {"Content-Type" "application/edn"}
       :body (pr-str events)}))

  (route/resources "/")
  (route/not-found "Page not found"))

;; -- App lifecycle --
(defn wrap-cors [handler]
  (fn [req]
    (if (= (:request-method req) :options)
      {:status 200
       :headers {"Access-Control-Allow-Origin" "*"
                 "Access-Control-Allow-Methods" "GET,POST,OPTIONS"
                 "Access-Control-Allow-Headers" "Content-Type"}
       :body ""}
      (let [resp (handler req)]
        (if (map? resp)
          (update resp :headers merge {"Access-Control-Allow-Origin" "*"
                                       "Access-Control-Allow-Methods" "GET,POST,OPTIONS"
                                       "Access-Control-Allow-Headers" "Content-Type"})
          resp)))))

(def app (-> app-routes
             wrap-params
             wrap-cors))

(defonce server (atom nil))

(defn start! []
  (when @server
    (.stop @server))
  (reset! server (run-jetty #'app {:port 3000 :join? false}))
  (println "✅ Server running at http://localhost:3000"))

(defn stop! []
  (when @server
    (.stop @server)
    (reset! server nil)
    (println "🛑 Server stopped")))

(defn -main []
  (start!))


