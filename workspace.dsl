workspace "EventHub Ticketing" "Updated C4 model of EventHub after Call 5: one modular Flask application, one SQLite database, and two roles (buyer and administrator)." {

    !impliedRelationships false

    model {

        buyer = person "Buyer" "Anyone who registers, browses and searches events, buys tickets and reads their own order history. Students, parents and fans anywhere in the world all hold this one role."
        administrator = person "Administrator" "Signs in to change exchange rates and to read the audit log. Holds a role that no buyer can obtain through the website." "Administrator"

        eventHub = softwareSystem "EventHub Ticketing" "Public ticketing website for version one. Every piece of data that crosses into the system is validated at the boundary before any internal logic trusts it. A buyer can never do what an administrator does." {

            app = container "Flask Web Application" "One deployable Python/Flask application. Serves the buyer-facing pages and the administrator-only pages (all under the /admin path)." "Python / Flask" {

                boundary = component "Boundary Validation" "Checks every value that enters the system (form fields, query strings, quantities, currency codes, search text, return addresses, exchange-rate values) before any other component sees it. Rejects bad input with a specific message." "Python / Flask request hooks"

                identity = component "Identity & Sessions" "Registration (including the preferred currency), sign-in, sign-out, salted password hashes, sessions with an idle timeout, and the buyer or administrator role. Offers no way to change an email address in version one (Q18). Redirects signed-out visitors to the login page and returns them to the page they asked for." "Python / Flask"

                catalog = component "Catalog" "Browsing, search by artist or venue, event pages, the no-match message followed by the full event list, and loading the event setup data." "Python / Flask"

                pricing = component "Pricing" "The only place that computes a price: base price, quantity, USF discount eligibility, currency conversion and rounding, with money held as whole minor units. Also owns the exchange-rate table." "Python"

                eligibility = component "USF Discount Eligibility" "Independent, unit-tested case-normalization and exact-domain classification function; plus-tags allowed, subdomains excluded provisionally pending customer confirmation." "Python (eventhub/eligibility.py)"

                inventory = component "Inventory" "Owns the ticket counts. Checks availability and reduces the count in one indivisible step." "Python / SQL"

                purchase = component "Purchase & Orders" "Runs the purchase path: quick-buy, checkout, simulated payment, order creation, on-screen confirmation, order history and abandoned-checkout handling. Every form carries a one-time purchase token, so a repeated submit returns the original order instead of making a second one." "Python / Flask"

                ratelimit = component "Request Rate Limiter" "Counts each account's purchase requests in a sliding window (numbers still open, Q19) and rejects the excess with a wait time before it reaches the purchase path. Writes one audit entry per blocked period." "Python (eventhub/ratelimit.py)"

                audit = component "Audit Log" "Records every purchase attempt from inside the purchase path, so a route cannot skip it. Also records rate changes and abandoned checkouts." "Python"

                admin = component "Administration" "Administrator-only pages: update exchange rates and read the audit log. Nothing in the buyer-facing flow calls into it." "Python / Flask" "Administrator Only"

            }

            db = container "EventHub Database" "Accounts with roles, sessions, events, ticket counts, orders, exchange rates and audit records." "SQLite (single file, WAL mode)" "Database"

            config = container "Configuration & Setup Files" "Event setup data, the supported-currency list with each currency's minor-unit digits, the first exchange rates (seed only), and application settings such as the session idle timeout." "Local files"

        }

        # Context level
        buyer -> eventHub "Registers, browses, searches, buys tickets, views own orders" "HTTPS"
        administrator -> eventHub "Updates exchange rates and reads the audit log" "HTTPS"

        # Container level
        buyer -> app "Registers, browses, searches, buys tickets, views own orders" "HTTPS"
        administrator -> app "Uses the administrator pages" "HTTPS"
        app -> db "Reads and writes data; ticket check and decrement in one transaction" "SQL"
        app -> config "Loads event setup, currencies and settings at start-up" "File read"

        # Component level: the boundary
        buyer -> boundary "Sends requests" "HTTPS"
        administrator -> boundary "Sends administrator requests" "HTTPS"
        boundary -> identity "Validated sign-in, registration and session requests"
        boundary -> catalog "Validated browse and search requests"
        boundary -> ratelimit "Validated quick-buy and checkout requests, counted per account"
        ratelimit -> purchase "Forwards only requests inside the limit"
        ratelimit -> audit "Records the first rejection of each blocked period"
        boundary -> purchase "Validated order-history requests"
        boundary -> admin "Validated administrator requests"

        # Component level: the purchase path, in order
        purchase -> identity "1. Checks the buyer is signed in"
        purchase -> catalog "2. Loads the event and its base price"
        purchase -> pricing "3. Computes the price in the chosen currency"
        pricing -> eligibility "Checks normalized student email eligibility; returns only a boolean"
        purchase -> inventory "4. Checks availability and reduces the count (one atomic step)"
        purchase -> audit "5. Records the outcome (same transaction on success, after rollback on failure)"

        # Component level: other interactions
        catalog -> inventory "Reads tickets currently available"
        admin -> identity "Requires the administrator role"
        admin -> pricing "Updates exchange rates"
        admin -> audit "Reads the audit log; records rate changes"

        # Component level: data and files
        identity -> db "Accounts, roles and sessions" "SQL"
        catalog -> db "Events" "SQL"
        pricing -> db "Exchange rates" "SQL"
        inventory -> db "Ticket counts" "SQL"
        purchase -> db "Orders" "SQL"
        audit -> db "Audit records" "SQL"
        catalog -> config "Loads event setup data" "File read"
        pricing -> config "Reads supported currencies; seeds first rates" "File read"
        identity -> config "Reads the session idle timeout" "File read"

    }

    views {

        systemContext eventHub "SystemContext" "Context view after Call 3: two human actors, nothing external." {
            title "System Context: EventHub Ticketing (buyer and administrator)"
            include *
            autolayout lr
        }

        container eventHub "Containers" "Container view: one Flask application, one SQLite database, and setup files." {
            title "Container View: EventHub Ticketing"
            include *
            autolayout lr
        }

        component app "Part5Components" "Call 5 component view: adds the request rate limiter in front of the purchase path and the purchase token that makes a repeated submit harmless." {
            title "Call 5: Component Boundaries, Rate Limiter and Idempotent Purchase"
            include *
            autolayout tb 300 220
        }

        dynamic app "PurchasePath" "The purchase path in order. The availability check and the count decrement are one indivisible step." {
            title "Dynamic View: Purchase Path"
            buyer -> boundary "Submits a purchase (form carries a one-time purchase token)"
            boundary -> ratelimit "Passes the validated request"
            ratelimit -> purchase "Forwards it if the account is inside its limit"
            purchase -> identity "Checks the buyer is signed in"
            purchase -> catalog "Loads the event and base price"
            purchase -> pricing "Computes the price"
            purchase -> inventory "Checks availability and reduces the count (atomic)"
            purchase -> audit "Records the outcome (a repeated token is recorded as a duplicate and returns the original order)"
            autolayout lr
        }

        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Administrator" {
                background #8A4B08
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Database" {
                shape cylinder
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Administrator Only" {
                background #F4B183
                color #000000
            }
        }

    }

}
