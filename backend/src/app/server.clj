(ns app.server
  (:gen-class)
  (:require [compojure.core :refer [defroutes GET POST DELETE]]
            [compojure.route :as route]
            [ring.adapter.jetty :refer [run-jetty]]
            [ring.middleware.params :refer [wrap-params]]
            [ring.middleware.json :refer [wrap-json-response wrap-json-body]]
            [ring.middleware.cors :refer [wrap-cors]]
            [ring.util.response :as response]
            [app.storage :as storage]
            [app.ics :as ics]
            [app.core.types :refer [calendar-url]]
            [app.core.filtering :refer [by-summary any-filter]]
            [app.core.user-storage :as user-storage]
            [app.core.auth :as auth]))

(defn filter-events-by-summaries 
  "Filter events using the filtering system"
  [events selected-summaries]
  (if (seq selected-summaries)
    (let [summary-filter (apply any-filter (map by-summary selected-summaries))]
      (filter summary-filter events))
    []))

(defroutes routes
  ;; Redirect root to the SPA
  (GET "/" [] 
    (response/redirect "/app"))
  
  ;; Health check endpoint for deployment validation
  (GET "/health" [] 
    {:status 200 
     :headers {"Content-Type" "application/json"}
     :body "{\"status\":\"healthy\",\"service\":\"ical-viewer\"}"})

  ;; ClojureScript SPA
  (GET "/app" [] 
    (slurp "resources/index.html"))

  ;; iCal subscription endpoints (still needed for calendar apps)
  (GET "/subscribe/:filter-id" [filter-id]
    (if-let [filter (storage/get-filter filter-id)]
      (let [entry (storage/get-entry (:calendar-id filter))
            all-events (ics/events-for-url (calendar-url entry))
            filtered-events (filter-events-by-summaries all-events (storage/filter-selected-summaries filter))]
        {:status 200
         :headers {"Content-Type" "text/calendar"}
         :body (ics/build-calendar filtered-events)})
      {:status 404
       :body "Filter not found"}))

  ;; API Routes for ClojureScript SPA - Now with user-specific storage
  (GET "/api/calendars" request
    (let [username (auth/get-current-user request)]
      (response/response {:calendars (user-storage/get-calendars-for-user username)})))

  (POST "/api/calendars" request
    (let [username (auth/get-current-user request)
          body (:body request)
          name (:name body)
          url (:url body)]
      (if (and (not-empty name) (not-empty url))
        (let [new-entry (user-storage/add-calendar-for-user! username name url)]
          {:status 201
           :body {:message "Calendar added successfully" :id (:id new-entry)}})
        {:status 400
         :body {:error "Name and URL are required"}})))

  (DELETE "/api/calendars/:id" [id :as request]
    (let [username (auth/get-current-user request)
          calendar-id (Integer/parseInt id)]
      (if (user-storage/get-calendar-for-user username calendar-id)
        (do 
          (user-storage/delete-calendar-for-user! username calendar-id)
          {:status 200 :body {:message "Calendar deleted successfully"}})
        {:status 404 :body {:error "Calendar not found"}})))

  (GET "/api/calendar/:id/events" [id :as request]
    (let [username (auth/get-current-user request)
          calendar-id (Integer/parseInt id)]
      (if-let [entry (user-storage/get-calendar-for-user username calendar-id)]
        (let [events (ics/events-for-url (:url entry))]
          (response/response {:events events}))
        {:status 404 :body {:error "Calendar not found"}})))

  (GET "/api/filters" request
    (let [username (auth/get-current-user request)]
      (response/response {:filters (user-storage/get-filters-for-user username)})))

  (POST "/api/filters" request
    (let [username (auth/get-current-user request)
          body (:body request)
          calendar-id (:calendar-id body)
          filter-name (:name body)
          types (:types body)]
      (if (and calendar-id filter-name (seq types))
        (let [new-filter (user-storage/add-filter-for-user! username filter-name calendar-id types)]
          {:status 201
           :body {:message "Filter saved successfully" :id (:id new-filter)}})
        {:status 400
         :body {:error "Calendar ID, name, and types are required"}})))

  (DELETE "/api/filters/:id" [id :as request]
    (let [username (auth/get-current-user request)
          filter-id (Integer/parseInt id)]
      (if (user-storage/get-filter-for-user username filter-id)
        (do
          (user-storage/delete-filter-for-user! username filter-id)
          {:status 200 :body {:message "Filter deleted successfully"}})
        {:status 404 :body {:error "Filter not found"}})))

  ;; Static file serving for all ClojureScript assets
  (GET "/js/*" {uri :uri}
    (let [file-path (str "resources" uri)]
      (if (.exists (java.io.File. file-path))
        (response/file-response file-path)
        {:status 404})))

  ;; Static file serving for CSS assets from frontend
  (GET "/css/*" {uri :uri}
    (let [file-path (str "../frontend/resources/public" uri)]
      (if (.exists (java.io.File. file-path))
        (response/file-response file-path)
        {:status 404})))

  (route/not-found "Page not found"))

(def app 
  (-> routes
      wrap-json-response
      (wrap-json-body {:keywords? true})
      wrap-params
      auth/wrap-user-context))

(defn -main [& _args]
  (let [port (Integer/parseInt (or (System/getenv "PORT") "3000"))]
    (println (str "🚀 iCal Viewer API server starting on port " port))
    (run-jetty app {:port port :join? false})
    (println "✅ Server ready - serving ClojureScript SPA and API endpoints")))

;; For REPL development
(defonce server (atom nil))

(defn start-server! []
  (when @server (.stop @server))
  (reset! server (run-jetty #'app {:port 3000 :join? false})))

(defn stop-server! []
  (when @server (.stop @server))
  (reset! server nil))