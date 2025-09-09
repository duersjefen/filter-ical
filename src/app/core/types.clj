;; === DATA ABSTRACTION LAYER ===
;; Following SICP Chapter 2 principles

(ns app.core.types)

;; Calendar Entry abstraction
(defn make-calendar [id name url metadata]
  {:id id :name name :url url :metadata metadata})

(defn calendar-id [cal] (:id cal))
(defn calendar-name [cal] (:name cal))
(defn calendar-url [cal] (:url cal))
(defn calendar-metadata [cal] (:metadata cal))

;; Event abstraction
(defn make-event [uid summary dtstart dtend location description raw-data]
  {:uid uid :summary summary :dtstart dtstart :dtend dtend
   :location location :description description :raw raw-data})

(defn event-uid [event] (:uid event))
(defn event-summary [event] (:summary event))
(defn event-start [event] (:dtstart event))
(defn event-end [event] (:dtend event))

;; Filter abstraction - more powerful than current implementation
(defn make-filter [id name calendar-id predicates transformers metadata]
  {:id id :name name :calendar-id calendar-id
   :predicates predicates :transformers transformers :metadata metadata})