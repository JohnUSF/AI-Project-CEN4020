workspace "EventHub Ticketing - Original (before Call 3)" "Original C4 model produced with GenAI from the Part 2 selected architecture and Calls 1 and 2. The container view is the Part 2 selected container view; the component view was generated from Part 2's module list because Part 2 had no component view." {

    model {

        user = person "User" "Registers, browses/searches, purchases tickets, and views order history."

        eventHub = softwareSystem "EventHub Ticketing - Selected Modular Monolith" "Public ticketing website implemented as one deployable Flask application. All data entering the system is validated at the boundary before internal logic uses it." {

            app = container "Flask Web Application" "Single deployable application containing account/authentication, event browsing/search, pricing/currency, purchase/inventory, order confirmation/history, audit logging, and boundary validation modules." "Python / Flask" {

                validation = component "Boundary Validation" "Validates all data entering the system before any module trusts it." "Python / Flask"
                accounts = component "Accounts & Authentication" "Registration, login, sessions, password hashing, USF email detection." "Python / Flask"
                events = component "Event Browsing & Search" "Browse, search by artist or venue, event details, availability display." "Python / Flask"
                pricing = component "Pricing & Currency" "Discount, supported currencies, static exchange-rate conversion, rounding." "Python"
                purchase = component "Purchase & Inventory" "Quantity checks, ticket availability and the inventory decrement, simulated payment." "Python / Flask"
                orders = component "Order Confirmation & History" "On-screen confirmation and the buyer's order history." "Python / Flask"
                audit = component "Audit Logging" "Records every purchase attempt, success or failure." "Python"

            }

            data = container "EventHub Data Store" "Persists accounts, events, authoritative ticket inventory, orders, sessions, and purchase-audit records." "Technology TBD"

            files = container "Configuration & Setup Files" "Event setup data and static exchange rates." "Local files"

        }

        user -> eventHub "Uses EventHub; validates all incoming data at boundary" "HTTPS"
        user -> app "Uses EventHub; validates all incoming data at boundary" "HTTPS"
        app -> data "Reads/writes data; concurrency-safe inventory updates"
        app -> files "Loads event setup data and static exchange rates"

        user -> validation "Sends requests" "HTTPS"
        validation -> accounts "Validated account requests"
        validation -> events "Validated browse and search requests"
        validation -> purchase "Validated purchase requests"
        validation -> orders "Validated order-history requests"
        purchase -> accounts "Checks the user is logged in"
        purchase -> events "Reads event details"
        purchase -> pricing "Gets the price and currency conversion"
        purchase -> orders "Creates the order and confirmation"
        purchase -> audit "Logs the purchase attempt"
        accounts -> data "Reads/writes accounts and sessions"
        events -> data "Reads events"
        purchase -> data "Atomic inventory check and decrement"
        orders -> data "Reads/writes orders"
        audit -> data "Writes audit records"
        events -> files "Loads event setup data"
        pricing -> files "Reads static exchange rates"

    }

    views {

        systemContext eventHub "Original-SystemContext" "Original context: one human actor." {
            title "Original System Context (Part 2)"
            include *
            autolayout lr
        }

        container eventHub "Original-Containers" "Original container view (Part 2 selected architecture)." {
            title "Original Container View (Part 2)"
            include *
            autolayout lr
        }

        component app "Original-Components" "Original component view generated from Part 2's module list." {
            title "Original Component View (generated from Part 2 modules)"
            include *
            autolayout tb 300 220
        }

        styles {
            element "Person" {
                shape person
                background #08427B
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
            element "Component" {
                background #85BBF0
                color #000000
            }
        }

    }

}
