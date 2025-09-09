;; === INTELLIGENT ICAL SYNCHRONIZATION ===
(ns app.core.sync
  (:require [clojure.java.io :as io])
  (:import [java.time Instant]
           [java.util.concurrent ScheduledThreadPoolExecutor TimeUnit]))

;; Cache with TTL and conditional updates
(defrecord CachedCalendar [url content etag last-modified last-updated ttl])

(def calendar-cache (atom {}))

(defn cache-key [url filter-id]
  (str (hash url) "-" (hash filter-id)))

(defn cache-expired? [cached-calendar]
  (let [now (System/currentTimeMillis)
        age (- now (:last-updated cached-calendar))]
    (> age (:ttl cached-calendar))))

(defn fetch-with-conditional-headers [url cached]
  "Fetch calendar with If-None-Match and If-Modified-Since headers"
  (try
    (let [connection (-> (java.net.URL. url)
                         .openConnection)]
      ;; Add conditional headers if we have cached data
      (when cached
        (when (:etag cached)
          (.setRequestProperty connection "If-None-Match" (:etag cached)))
        (when (:last-modified cached)
          (.setRequestProperty connection "If-Modified-Since" (:last-modified cached))))

      (.connect connection)

      (case (.getResponseCode connection)
        200 ; Fresh content
        {:status :updated
         :content (slurp (.getInputStream connection))
         :etag (.getHeaderField connection "ETag")
         :last-modified (.getHeaderField connection "Last-Modified")}

        304 ; Not modified
        {:status :not-modified
         :content (:content cached)}

        ; Error case
        {:status :error
         :content (or (:content cached) "")}))
    (catch Exception e
      (println "Error fetching calendar:" (.getMessage e))
      {:status :error
       :content (or (:content cached) "")})))

(defn smart-fetch-calendar [url & {:keys [ttl] :or {ttl (* 1000 60 60)}}] ; 1 hour default
  "Intelligently fetch calendar with caching and conditional requests"
  (let [cache-key (str "cal-" (hash url))
        cached (get @calendar-cache cache-key)]

    (if (and cached (not (cache-expired? cached)))
      ;; Return cached content
      (:content cached)

      ;; Fetch with conditional headers
      (let [result (fetch-with-conditional-headers url cached)
            now (System/currentTimeMillis)]
        (case (:status result)
          :updated
          (let [new-cached (->CachedCalendar
                            url
                            (:content result)
                            (:etag result)
                            (:last-modified result)
                            now
                            ttl)]
            (swap! calendar-cache assoc cache-key new-cached)
            (:content result))

          :not-modified
          (do
            ;; Update timestamp but keep content
            (swap! calendar-cache update cache-key assoc :last-updated now)
            (:content result))

          :error
          (:content result))))))

;; Filter-specific caching with dependency tracking
(defrecord FilteredCalendar [filter-id source-url filtered-content source-hash dependencies last-generated])

(def filtered-cache (atom {}))

(defn compute-source-hash [ical-content filter-spec]
  "Create hash from source content + filter specification"
  (hash (str ical-content (pr-str filter-spec))))

;; This function needs to be integrated with the main application later
;; For now, commenting out to avoid dependency issues
#_(defn get-filtered-calendar [filter-id & {:keys [force-refresh]}]
  "Get filtered calendar with intelligent caching"
  (let [filter (get-filter filter-id)
        source-url (get-calendar-url (:calendar-id filter))
        cache-key (str "filtered-" filter-id)
        cached (get @filtered-cache cache-key)]

    ;; Fetch source calendar (this uses its own caching)
    (let [source-content (smart-fetch-calendar source-url)
          source-hash (compute-source-hash source-content filter)]

      (if (and cached
               (not force-refresh)
               (= source-hash (:source-hash cached)))
        ;; Return cached filtered content
        (:filtered-content cached)

        ;; Regenerate filtered calendar
        (let [events (parse-events source-content)
              filtered-events (apply-filter filter events)
              filtered-content (generate-ical filtered-events)

              new-cached (->FilteredCalendar
                          filter-id
                          source-url
                          filtered-content
                          source-hash
                          #{filter-id}
                          (System/currentTimeMillis))]

          (swap! filtered-cache assoc cache-key new-cached)
          filtered-content)))))

;; Background refresh system
(defonce refresh-scheduler (ScheduledThreadPoolExecutor. 2))

(defn schedule-refresh [filter-id interval-minutes]
  "Schedule background refresh of filtered calendar"
  (.scheduleAtFixedRate
   refresh-scheduler
   (fn []
     (try
       (println "Background refresh for filter" filter-id)
       ;; TODO: Re-enable when get-filtered-calendar is properly integrated
       #_(get-filtered-calendar filter-id :force-refresh true)
       (catch Exception e
         (println "Background refresh failed for filter" filter-id ":" (.getMessage e)))))
   interval-minutes
   interval-minutes
   TimeUnit/MINUTES))

;; Webhook support for real-time updates
;; TODO: Implement webhook signature validation
#_(defn create-webhook-handler [filter-id]
  "Create webhook endpoint for calendar providers that support notifications"
  (fn [request]
    (when (valid-webhook-signature? request filter-id)
      ;; Force refresh when webhook is triggered
      (future
        ;; TODO: Re-enable when get-filtered-calendar is properly integrated
        #_(get-filtered-calendar filter-id :force-refresh true))
      {:status 200 :body "OK"})))

;; Subscription URL generation with proper headers
(defn generate-subscription-response [filter-id request]
  "Generate iCal response with proper caching headers"
  ;; TODO: Re-enable when get-filtered-calendar is properly integrated
  ;; Fallback response for now
  {:status 200
   :headers {"Content-Type" "text/calendar"}
   :body "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"})

;; === ADVANCED FUNCTIONALITY TO BE IMPLEMENTED ===
;; TODO: Move to separate namespace files later
;; - Advanced iCal processing with timezone support
;; - Subscription management and analytics
;; - Auto-cleanup for unused filters