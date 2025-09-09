;; === TELEGRAM WEB APP AUTHENTICATION ===
(ns app.auth.telegram
  (:require [clojure.string :as str]
            [clojure.data.json :as json]))

;; Configuration - would be loaded from environment in production
(def telegram-config
  {:bot-token (or (System/getenv "TELEGRAM_BOT_TOKEN") "")
   :webapp-url (or (System/getenv "WEBAPP_URL") "http://localhost:3000")})

(defn validate-telegram-auth [auth-data]
  "Validate Telegram Web App authentication data"
  ;; This is a simplified version - real implementation would:
  ;; 1. Validate the hash using bot token
  ;; 2. Check auth_date is recent (not older than 24 hours)
  ;; 3. Verify all parameters are correctly signed
  
  (when-not (str/blank? (:bot-token telegram-config))
    (try
      (let [{:keys [id first_name username auth_date hash]} auth-data]
        (when (and id auth_date hash)
          {:user-id (str "telegram:" id)
           :name (or first_name username (str "User " id))
           :platform "telegram"
           :auth-time (Long/parseLong auth_date)
           :raw auth-data}))
      (catch Exception e
        (println "Telegram auth validation error:" (.getMessage e))
        nil))))

(defn create-telegram-login-button []
  "Generate HTML for Telegram Login Button"
  (if (str/blank? (:bot-token telegram-config))
    [:div.auth-unavailable
     [:p "Telegram authentication not configured"]
     [:small "Set TELEGRAM_BOT_TOKEN environment variable"]]
    [:div.telegram-auth
     [:script {:async true 
               :src "https://telegram.org/js/telegram-web-app.js"}]
     [:div.telegram-login-button
      {:data-telegram-login "your_bot_username"
       :data-size "large"
       :data-auth-url (str (:webapp-url telegram-config) "/auth/telegram/callback")
       :data-request-access "write"}]
     [:script "
       function initTelegramAuth() {
         if (window.Telegram && window.Telegram.WebApp) {
           const webapp = window.Telegram.WebApp;
           webapp.ready();
           // Send auth data to server when user confirms
           webapp.onEvent('mainButtonClicked', function() {
             const initData = webapp.initData;
             fetch('/auth/telegram/verify', {
               method: 'POST',
               headers: {'Content-Type': 'application/json'},
               body: JSON.stringify({initData: initData})
             }).then(response => response.json())
               .then(data => {
                 if (data.success) {
                   window.location.href = '/';
                 } else {
                   alert('Authentication failed');
                 }
               });
           });
         }
       }
       
       if (document.readyState === 'loading') {
         document.addEventListener('DOMContentLoaded', initTelegramAuth);
       } else {
         initTelegramAuth();
       }
     "]]))

;; Routes for Telegram auth (to be integrated into main server)
(defn telegram-auth-routes []
  "Return auth routes for Telegram integration"
  [
   ;; Telegram callback endpoint
   {:method :post
    :path "/auth/telegram/verify"
    :handler (fn [request]
               (let [body (slurp (:body request))
                     auth-data (json/read-str body :key-fn keyword)
                     user (validate-telegram-auth (:initData auth-data))]
                 (if user
                   {:status 200
                    :headers {"Content-Type" "application/json"}
                    :body (json/write-str {:success true :user user})}
                   {:status 401
                    :headers {"Content-Type" "application/json"}
                    :body (json/write-str {:success false :error "Invalid authentication"})})))}])

;; Session management
(defonce telegram-sessions (atom {}))

(defn create-session [user-data]
  "Create session for authenticated Telegram user"
  (let [session-id (str (java.util.UUID/randomUUID))]
    (swap! telegram-sessions assoc session-id user-data)
    session-id))

(defn get-session [session-id]
  "Get user data from session"
  (get @telegram-sessions session-id))

(defn cleanup-sessions []
  "Clean up expired sessions (older than 7 days)"
  (let [now (System/currentTimeMillis)
        week-ms (* 7 24 60 60 1000)]
    (swap! telegram-sessions
           (fn [sessions]
             (into {} (filter (fn [[_ user]]
                               (< (- now (:auth-time user)) week-ms))
                             sessions))))))