(ns app.storage
  (:require [clojure.java.io :as io]
            [clojure.edn :as edn]
            [clojure.string :as str]))

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
  (let [entry {:id (next-id)
               :name (str/trim name)
               :url (str/trim url)}]
    (swap! entries conj entry)
    (save!)
    entry))

(defn delete-entry! [id]
  (let [id (if (string? id) (Integer/parseInt id) id)]
    (swap! entries #(vec (remove (fn [e] (= (:id e) id)) %)))
    (save!)))

(defn get-entry [id]
  (let [id (if (string? id) (Integer/parseInt id) id)]
    (first (filter #(= (:id %) id) @entries))))

(defn all-entries []
  @entries)

;; Filter management functions
(defn next-filter-id []
  (inc (apply max (cons 0 (map :id @filters)))))

(defn add-filter! [name calendar-id selected-summaries]
  (let [filter-entry {:id (next-filter-id)
                     :name (str/trim name)
                     :calendar-id calendar-id
                     :selected-summaries (vec selected-summaries)
                     :created-at (System/currentTimeMillis)}]
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
