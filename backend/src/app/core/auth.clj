(ns app.core.auth
  "Simple authentication middleware for user identification.
   
   This provides basic username-based authentication for demo purposes.
   Can be easily extended with proper authentication mechanisms later.")

;; ============================================================================
;; User Context Extraction
;; ============================================================================

(defn extract-username-from-header
  "Extract username from X-User-ID header (simple demo auth)"
  [request]
  (get-in request [:headers "x-user-id"]))

(defn extract-username-from-session
  "Extract username from session (for future session-based auth)"
  [request]
  (get-in request [:session :username]))

(defn get-current-user
  "Get current user from request context"
  [request]
  (or (extract-username-from-header request)
      (extract-username-from-session request)
      "anonymous"))  ; Default user for demo purposes

;; ============================================================================
;; Middleware 
;; ============================================================================

(defn wrap-user-context
  "Middleware that adds user context to request"
  [handler]
  (fn [request]
    (let [username (get-current-user request)
          request-with-user (assoc request :user username)]
      (handler request-with-user))))

;; ============================================================================
;; Request Helpers
;; ============================================================================

(defn require-user
  "Require a user to be present in request context"
  [request]
  (let [username (:user request)]
    (when (or (nil? username) 
              (= username "anonymous"))
      (throw (ex-info "Authentication required" 
                     {:status 401 :message "User authentication required"})))
    username))