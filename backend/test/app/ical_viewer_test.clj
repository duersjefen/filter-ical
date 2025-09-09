(ns app.ical-viewer-test
  (:require [clojure.test :refer [deftest is run-tests testing]]
            [app.storage :as storage]
            [app.ics :as ics]
            [app.server :as server]))

(deftest storage-tests
  (testing "Storage functionality"

    (testing "add-entry! creates entry with ID"
      (let [entry (storage/add-entry! "Test Calendar" "http://example.com/test.ics")]
        (is (number? (:id entry)))
        (is (= "Test Calendar" (:name entry)))
        (is (= "http://example.com/test.ics" (:url entry)))))

    (testing "get-entry retrieves by ID"
      (let [entry (storage/add-entry! "Another Test" "http://example.com/test2.ics")
            retrieved (storage/get-entry (:id entry))]
        (is (= entry retrieved))))

    (testing "delete-entry! removes entry"
      (let [entry (storage/add-entry! "To Delete" "http://example.com/delete.ics")
            id (:id entry)]
        (storage/delete-entry! id)
        (is (nil? (storage/get-entry id)))))))

(deftest ics-tests
  (testing "iCal parsing functionality"

    (testing "extract-vevents finds event blocks"
      (let [sample-ics "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nUID:1\nSUMMARY:Test Event\nEND:VEVENT\nEND:VCALENDAR"
            events (ics/extract-vevents sample-ics)]
        (is (= 1 (count events)))
        (is (re-find #"BEGIN:VEVENT" (first events)))))

    (testing "extract-property finds properties"
      (let [vevent "BEGIN:VEVENT\nUID:test-123\nSUMMARY:My Event\nEND:VEVENT"]
        (is (= "test-123" (ics/extract-property vevent "UID")))
        (is (= "My Event" (ics/extract-property vevent "SUMMARY")))))

    (testing "parse-vevent creates event map"
      (let [vevent "BEGIN:VEVENT\nUID:test-456\nSUMMARY:Parsed Event\nDTSTART:20250101T120000Z\nEND:VEVENT"
            parsed (ics/parse-vevent vevent)]
        (is (= "test-456" (:uid parsed)))
        (is (= "Parsed Event" (:summary parsed)))
        (is (= "20250101T120000Z" (:dtstart parsed)))
        (is (= vevent (:raw parsed)))))

    (testing "build-calendar creates valid iCal"
      (let [events [{:raw "BEGIN:VEVENT\nUID:1\nSUMMARY:Event 1\nEND:VEVENT"}
                    {:raw "BEGIN:VEVENT\nUID:2\nSUMMARY:Event 2\nEND:VEVENT"}]
            calendar (ics/build-calendar events)]
        (is (re-find #"BEGIN:VCALENDAR" calendar))
        (is (re-find #"END:VCALENDAR" calendar))
        (is (re-find #"Event 1" calendar))
        (is (re-find #"Event 2" calendar))))))

(deftest server-tests
  (testing "Server functionality"

    (testing "group-events-by-summary groups correctly"
      (let [events [{:summary "Meeting" :uid "1"}
                    {:summary "Meeting" :uid "2"}
                    {:summary "Lunch" :uid "3"}]
            grouped (server/group-events-by-summary events)]
        (is (= 2 (count (get grouped "Meeting"))))
        (is (= 1 (count (get grouped "Lunch"))))))

    (testing "layout generates HTML"
      (let [html (server/layout "Test Title" [:h1 "Hello"])]
        (is (re-find #"Test Title" html))
        (is (re-find #"<h1>Hello</h1>" html))))))

(deftest integration-tests
  (testing "Full workflow integration"

    (testing "Can store and retrieve calendar entries"
      (storage/add-entry! "Integration Test" "http://example.com/integration.ics")
      (let [entries (storage/all-entries)]
        (is (some #(= "Integration Test" (:name %)) entries))))

    (testing "Error handling for invalid URLs"
      (let [events (ics/events-for-url "invalid-url")]
        (is (empty? events))))))

(defn test-runner []
  (println "Running all tests...")
  (run-tests 'app.ical-viewer-test))
