# Mini Laundry Order Management System

A lightweight, AI-assisted order management API built for a dry cleaning store. 

## 🚀 Setup Instructions
1. **Clone the repository:** `git clone [your-repo-link]`
2. **Install dependencies:** `pip install -r requirements.txt` *(or `npm install`)*
3. **Run the server:** `uvicorn main:app --reload` *(or `node server.js`)*
4. **Access the API Demo:** Navigate to `http://localhost:8000/docs` to view the interactive API documentation. *(Adjust this if using a different stack)*

## ⚙️ Features Implemented
* **Create Order:** Calculates billing automatically based on predefined garment prices.
* **Status Tracking:** Safely updates order statuses.
* **View/Filter Orders:** Filter by status, customer name, or phone number.
* **Dashboard:** Real-time calculation of total revenue, total orders, and order status breakdown.
* **[Bonus] Database:** Integrated SQLite for persistent storage. *(Remove if you used in-memory)*
* **[Bonus] Frontend:** Built a simple HTML/JS dashboard. *(Remove if you didn't do this)*

## 🤖 AI Usage Report
* **Tools Used:** [e.g., ChatGPT-4, GitHub Copilot]
* **Sample Prompts:**
  * *"Write a FastAPI boilerplate with an SQLite database for a laundry ordering system."*
  * *"How do I implement partial string matching for filtering customer names in my GET request?"*
* **What AI Got Wrong:** [e.g., The AI initially suggested a complex SQLAlchemy setup, which violated the 'keep it simple' constraint. The AI also tried to let the user input the `pricePerItem` directly, which is a security flaw.]
* **What I Improved:** [e.g., I stripped out the complex ORM and used standard library sqlite3 to move faster. I also moved the pricing dictionary to the backend to ensure users couldn't submit $0 orders.]

## ⚖️ Tradeoffs & Future Improvements
* **Skipped Auth:** To optimize for speed and focus on core domain logic, I skipped authentication.
* **Database Choice:** Used [In-Memory/SQLite] to avoid the overhead of setting up a remote Postgres database, fitting the 72-hour constraint perfectly. 
* **If I had more time:** I would add a "Services" database table instead of hardcoding prices, and implement JWT authentication for store clerks.