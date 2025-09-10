(ns app.ical-viewer-test
  (:require [clojure.test :refer [deftest is run-tests testing]]
            [app.server :as server]))

(deftest basic-functionality-test
  (testing "Server routes are defined"
    (is (some? server/routes)))
  
  (testing "App handler is defined"  
    (is (some? server/app))))

(defn test-runner []
  (println "Running all tests...")
  (run-tests 'app.ical-viewer-test))
