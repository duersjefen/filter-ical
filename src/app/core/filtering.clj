;; === FUNCTIONAL COMPOSITION ===
;; Following SICP higher-order function principles

(ns app.core.filtering
  (:require [app.core.types :refer [event-summary event-start event-uid]]))

;; Composable filter predicates
(defn by-summary [pattern]
  (fn [event] (re-find (re-pattern pattern) (event-summary event))))

(defn by-date-range [start end]
  (fn [event]
    (let [event-date (event-start event)]
      (and (>= event-date start) (<= event-date end)))))

(defn by-year [year]
  (fn [event]
    (when-let [date-str (event-start event)]
      (.startsWith date-str (str year)))))

(defn by-location [location-pattern]
  (fn [event] (re-find (re-pattern location-pattern) (or (:location event) ""))))

;; Compose filters using higher-order functions
(defn compose-filters [& predicates]
  (fn [event]
    (every? #(% event) predicates)))

(defn any-filter [& predicates]
  (fn [event]
    (some #(% event) predicates)))

;; Event transformers (for sorting, grouping)
(defn sort-by-date [events]
  (sort-by event-start events))

(defn sort-by-frequency [grouped-events]
  (sort-by (comp count second) > grouped-events))

(defn group-by-year [events]
  (group-by #(subs (or (event-start %) "0000") 0 4) events))

(defn group-by-month [events]
  (group-by #(subs (or (event-start %) "0000-00") 0 7) events))

(defn group-by-summary [events]
  (group-by event-summary events))

;; === FILTER ENGINE ===
;; Powerful, composable filtering system

(defn create-filter-engine [calendar-repo filter-repo ical-service]
  {:calendar-repo calendar-repo
   :filter-repo filter-repo
   :ical-service ical-service})

(defn apply-filter [engine filter-spec events]
  (let [{:keys [predicates transformers]} filter-spec
        filtered-events (->> events
                             (filter (apply compose-filters predicates))
                             ((apply comp (reverse transformers))))]
    filtered-events))

;; TODO: Implement when proper service integration is complete
#_(defn create-smart-filter [engine calendar-id options]
  "Creates intelligent filters based on user preferences"
  (let [events (-> engine :ical-service
                   (fetch-events (get-calendar-url calendar-id)))
        grouped (group-by-summary events)

        ;; Analyze patterns to suggest filters
        frequent-summaries (->> grouped
                                (filter #(> (count (second %)) 1))
                                (map first))

        years (->> events
                   (map #(subs (or (event-start %) "0000") 0 4))
                   (distinct)
                   (sort))

        predicates (cond-> []
                     (:year options) (conj (by-year (:year options)))
                     (:summaries options) (conj (apply any-filter
                                                       (map by-summary (:summaries options))))
                     (:location options) (conj (by-location (:location options))))

        transformers (cond-> [identity]
                       (:sort-by-date options) (conj sort-by-date)
                       (:sort-by-frequency options) (conj sort-by-frequency))]

    {:predicates predicates
     :transformers transformers
     :suggestions {:frequent-summaries frequent-summaries
                   :available-years years}}))