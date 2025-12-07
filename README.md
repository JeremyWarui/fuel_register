# Fuel Register ⛽

A Streamlit web application for tracking and managing fuel entries with persistent cloud storage.

## Purpose

Simple, public form where drivers can log fuel purchases including:
- Driver details and date
- Receipt number
- Vehicle registration
- Product type (Diesel, Premium, Lubricants, Puncture)
- Fuel quantity and amount
- Odometer readings with automatic distance calculation

All entries are stored persistently in **Supabase** (free cloud database) - data survives app restarts and is accessible from anywhere.

## Features

- ✅ Mobile-responsive form
- ✅ Real-time input validation
- ✅ Automatic distance calculation
- ✅ Confirmation dialog before submission
- ✅ Filter entries by driver name
- ✅ Cloud database storage (Supabase)
- ✅ No authentication required

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Supabase** (see [SUPABASE_SETUP.md](SUPABASE_SETUP.md))
   - Create free Supabase account
   - Run SQL to create table
   - Add credentials to `.streamlit/secrets.toml`

3. **Run locally**
   ```bash
   streamlit run app.py
   ```

## Deployment

Deploy to **Streamlit Cloud** with your Supabase credentials in the Secrets settings.

Full setup guide: [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
   ```


## Usage

1. Fill in driver name, date, and receipt number
2. Select vehicle registration and product type
3. Enter fuel quantity and amount
4. Add odometer readings (distance auto-calculates)
5. Review and confirm submission
6. Filter entries by driver name to view history

## Configuration

Edit `vehicles.py` to customize vehicle registration numbers:
```python
registration_numbers = ["GKA 123X", "GKA 431V", ...]
```

## License

MIT License

---

Made with Streamlit
