(ns app.ui-test
  (:require [clojure.test :refer :all]
            [app.ui.components :as ui]
            [app.core.filtering :refer [group-by-summary]]
            [app.core.types :refer [make-event]]))

(def sample-events
  [(make-event "1" "Team Meeting" "2025-01-15" "2025-01-15" nil nil nil)
   (make-event "2" "Project Review" "2025-01-16" "2025-01-16" nil nil nil)
   (make-event "3" "Team Meeting" "2025-01-17" "2025-01-17" nil nil nil)])

(deftest test-event-statistics
  (testing "Event statistics component"
    (let [grouped (group-by-summary sample-events)
          stats (ui/event-statistics sample-events grouped)]
      (is (vector? stats))
      (is (= :div.event-stats (first stats))))))

(deftest test-event-list-view
  (testing "Event list view component"
    (let [grouped (group-by-summary sample-events)
          table-view (ui/event-list-view grouped "table")
          cards-view (ui/event-list-view grouped "cards")]
      (is (vector? table-view))
      (is (vector? cards-view))
      (is (= :table.events-table (first table-view)))
      (is (= :div.event-cards (first cards-view))))))

(deftest test-filter-card
  (testing "Filter card component"
    (let [mock-filter {:id 1 :name "Test Filter" :calendar-id 1 :selected-summaries ["Meeting"]}
          card (ui/filter-card mock-filter "Test Calendar")]
      (is (vector? card))
      (is (= :div.filter-card (first card))))))

(deftest test-smart-filter-builder
  (testing "Smart filter builder component"
    (let [grouped (group-by-summary sample-events)
          builder (ui/smart-filter-builder sample-events 1 ["Team Meeting"])]
      (is (vector? builder))
      (is (= :div.smart-filter-builder (first builder))))))

(defn run-ui-tests []
  (run-tests 'app.ui-test))