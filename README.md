# Fuel Register 🚗⛽

A modern, user-friendly Streamlit web application for digitizing fuel receipt entry and management. Built to replace traditional pen-and-paper forms at the office, making it easy for drivers to log fuel purchases with instant validation and confirmation.

## Features ✨

### Real-Time Input Validation
- **Live feedback** - See your entries confirmed as you type
- **Visual indicators** - Color-coded info boxes for each field
- **Smart validation** - Instant error detection (e.g., current km < previous km)
- **Distance calculation** - Automatic calculation and display

### User-Friendly Form
- **Two-column layout** - Optimized for both desktop and mobile
- **Required field indicators** - Clear `*` marking on mandatory fields
- **Date picker** - Easy calendar selection for receipt dates
- **Vehicle selection** - Dropdown with predefined registration numbers
- **Product categories** - Diesel, Premium, Lubricants, Puncture
- **Receipt upload** - Support for PNG, JPG, JPEG, and PDF files

### Confirmation Workflow
- **Review before submit** - Confirmation dialog shows all entered details
- **Accuracy check** - Users must confirm details are accurate
- **Cancel option** - Easy way to go back and make changes
- **Success page** - Clear confirmation with option to submit another receipt

### Data Management
- **CSV storage** - All entries saved to `fuel_register.csv`
- **Sorted display** - Latest entries shown first
- **Search functionality** - Filter entries by driver name
- **Entry count** - Total number of records displayed
- **Clear filters** - Easy reset button for search

## Installation 🚀

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/JeremyWarui/fuel_register.git
   cd fuel_register
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit pandas
   ```

3. **Configure vehicle registrations** (optional)
   
   Edit `vehicles.py` to add or modify your fleet's registration numbers:
   ```python
   registration_numbers = [
       "GKA 123X",
       "GKA 431V",
       # Add your vehicles here
   ]
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the app**
   
   Open your browser and navigate to `http://localhost:8501`

## Usage 📝

### Adding a Fuel Entry

1. **Fill in driver details**
   - Enter your full name
   - Select the receipt date (defaults to today)
   - Enter the receipt number

2. **Select product and vehicle**
   - Choose product type from dropdown
   - Select vehicle registration number
   - Enter quantity in litres

3. **Enter mileage details**
   - Previous kilometers
   - Current kilometers
   - Distance is calculated automatically

4. **Upload receipt** (optional)
   - Click "Upload Receipt Image"
   - Select image or PDF of the fuel receipt

5. **Review and confirm**
   - Click "Add Entry" button
   - Review all details in confirmation dialog
   - Click "✓ Confirm & Submit" to save

6. **Submit another**
   - After successful submission, click "Submit Another Receipt" to continue

### Viewing Entries

- Scroll down to see all fuel entries
- Latest entries appear at the top
- Use the search box to filter by driver name
- Click "Clear" to reset the filter

## Project Structure 📂

```
fuel_register/
├── app.py                 # Main Streamlit application
├── vehicles.py            # Vehicle registration numbers configuration
├── fuel_register.csv      # Data storage (created automatically)
├── receipts/              # Uploaded receipt images (created automatically)
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Configuration ⚙️

### Customizing Products

Edit the `PRODUCTS` list in `app.py`:
```python
PRODUCTS = ["Diesel", "Premium", "Lubricants", "Puncture"]
```

### Adjusting Font Sizes

Modify these constants in `app.py`:
```python
FONT_SIZE = 18          # General text
FONT_SIZE_TITLE = 50    # Page title
```

### Changing Layout

Toggle between centered and wide layout:
```python
st.set_page_config(page_title="Fuel Register", page_icon="⛽", layout="wide")
# or
st.set_page_config(page_title="Fuel Register", page_icon="⛽", layout="centered")
```

## Data Storage 💾

All fuel entries are stored in `fuel_register.csv` with the following columns:

| Column | Description |
|--------|-------------|
| Driver Name | Full name of the driver |
| Date | Receipt date (ISO format) |
| Receipt No | Receipt number |
| Registration No | Vehicle registration number |
| Product | Fuel/product type |
| Quantity | Amount in litres |
| Amount | Cost in currency |
| Previous Km | Starting odometer reading |
| Current Km | Ending odometer reading |
| Distance | Calculated distance traveled |
| Receipt Image | Path to uploaded receipt file |

## Features in Detail 🔍

### Real-Time Feedback
- 👤 Driver name confirmation
- 📅 Formatted date display
- 🧾 Receipt number echo
- ✓ Product selection confirmation
- ⛽ Quantity display
- ✓ Vehicle confirmation
- 💰 Formatted amount display
- 📍 Kilometer readings with formatting
- 📏 Live distance calculation
- 📎 Uploaded filename display

### Validation Rules
- Driver name is required
- Receipt number is required
- Vehicle must be selected
- Product must be selected
- Current km cannot be less than previous km
- All fields validate before submission

## Browser Support 🌐

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (responsive design)

## Contributing 🤝

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## License 📄

This project is open source and available under the MIT License.

## Author ✍️

**Jeremy Warui**
- GitHub: [@JeremyWarui](https://github.com/JeremyWarui)

## Support 💬

For issues or questions, please open an issue on the GitHub repository.

---

Made with ❤️ using [Streamlit](https://streamlit.io)
