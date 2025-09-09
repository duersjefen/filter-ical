(ns app.storage
  (:require [clojure.java.io :as io]
            [clojure.edn :as edn]
            [clojure.string :as str]
            [app.core.types :refer [make-calendar calendar-id calendar-name calendar-url
                                   make-filter]]))

(def data-file "data/entries.edn")
(def filters-file "data/filters.edn")

(defn ensure-file! [file default-content]
  (io/make-parents file)
  (when-not (.exists (io/file file))
    (spit file default-content)))

(ensure-file! data-file "[]")
(ensure-file! filters-file "[]")

(defonce entries
  (let [content (try
                  (slurp data-file)
                  (catch Exception _ "[]"))]
    (atom (if (str/blank? content)
            []
            (edn/read-string content)))))

(defonce filters
  (let [content (try
                  (slurp filters-file)
                  (catch Exception _ "[]"))]
    (atom (if (str/blank? content)
            []
            (edn/read-string content)))))

(defn save! []
  (spit data-file (pr-str @entries)))

(defn save-filters! []
  (spit filters-file (pr-str @filters)))

(defn next-id []
  (inc (apply max (cons 0 (map :id @entries)))))

(defn add-entry! [name url]
  (let [entry (make-calendar (next-id)
                            (str/trim name)
                            (str/trim url)
                            {})]
    (swap! entries conj entry)
    (save!)
    entry))

(defn delete-entry! [id]
  (let [id (if (string? id) (Integer/parseInt id) id)]
    (swap! entries #(vec (remove (fn [e] (= (calendar-id e) id)) %)))
    (save!)))

(defn get-entry [id]
  (let [id (if (string? id) (Integer/parseInt id) id)]
    (first (filter #(= (calendar-id %) id) @entries))))

(defn all-entries []
  @entries)

;; Filter management functions
(defn next-filter-id []
  (inc (apply max (cons 0 (map :id @filters)))))

(defn add-filter! [name calendar-id selected-summaries]
  (let [filter-entry (make-filter (next-filter-id)
                                 (str/trim name)
                                 calendar-id
                                 selected-summaries  ; For now, keep as legacy until we refactor
                                 []                  ; transformers - empty for now
                                 {:created-at (System/currentTimeMillis)
                                  :legacy-summaries (vec selected-summaries)})]
    (swap! filters conj filter-entry)
    (save-filters!)
    filter-entry))

(defn get-filter [id]
  (let [id (if (string? id) (Integer/parseInt id) id)]
    (first (filter #(= (:id %) id) @filters))))

(defn delete-filter! [id]
  (let [id (if (string? id) (Integer/parseInt id) id)]
    (swap! filters #(vec (remove (fn [f] (= (:id f) id)) %)))
    (save-filters!)))

(defn all-filters []
  @filters)

(defn filters-for-calendar [calendar-id]
  (filter #(= (:calendar-id %) calendar-id) @filters))

;; Backward compatibility accessors for filters
(defn filter-selected-summaries [filter]
  "Get selected summaries from filter, handling both old and new format"
  (or (:selected-summaries filter)
      (get-in filter [:metadata :legacy-summaries])
      []))

;; Utility to get calendar URL - needed for caching integration
(defn get-calendar-url [calendar-id]
  (when-let [calendar (get-entry calendar-id)]
    (calendar-url calendar)))
