(ns user
  (:require [clojure.tools.namespace.repl :refer [refresh]]
            [ical-viewer.core :as core]))

(defn start [] (core/start!))
(defn stop [] (core/stop!))

(defn reset [] (stop) (refresh :after 'user/start))