# Supabase Setup Guide for Fuel Register

This guide will walk you through setting up Supabase as the database backend for your Fuel Register application.

## 📋 Prerequisites

- A Google, GitHub, or email account (for Supabase signup)
- Access to your Streamlit Cloud dashboard (for deployment)

---

## 🚀 Step 1: Create a Supabase Account & Project

1. **Go to [Supabase](https://supabase.com)** and click **"Start your project"**
2. **Sign up** using Google, GitHub, or email
3. **Create a new project**:
   - Organization: Create or select one
   - Project Name: `fuel-register` (or any name you prefer)
   - Database Password: **Save this password securely!**
   - Region: Choose closest to your users
   - Pricing Plan: **Free** (sufficient for this app)
4. Wait 1-2 minutes for project creation

---

## 🗄️ Step 2: Create the Database Table

1. In your Supabase project dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New query"**
3. **Copy and paste** this SQL code:

```sql
-- Create the fuel entries table
CREATE TABLE fuel_entries (
    id BIGSERIAL PRIMARY KEY,
    driver_name TEXT NOT NULL,
    date DATE NOT NULL,
    receipt_no TEXT NOT NULL,
    registration_no TEXT NOT NULL,
    product TEXT NOT NULL,
    quantity NUMERIC DEFAULT 0,
    amount NUMERIC NOT NULL,
    previous_km NUMERIC DEFAULT 0,
    current_km NUMERIC DEFAULT 0,
    distance NUMERIC DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX idx_driver_name ON fuel_entries(driver_name);
CREATE INDEX idx_date ON fuel_entries(date DESC);
CREATE INDEX idx_registration_no ON fuel_entries(registration_no);

-- IMPORTANT: Disable Row Level Security for public access (no authentication)
ALTER TABLE fuel_entries ENABLE ROW LEVEL SECURITY;

-- Allow anonymous users to INSERT data
CREATE POLICY "Allow public insert" ON fuel_entries
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- Allow anonymous users to SELECT (read) data
CREATE POLICY "Allow public select" ON fuel_entries
    FOR SELECT
    TO anon
    USING (true);
```

4. Click **"Run"** (or press `Ctrl+Enter`)
5. You should see: `Success. No rows returned`

---

## 🔑 Step 3: Get Your API Credentials

1. In Supabase dashboard, click **"Settings"** (gear icon, bottom left)
2. Click **"API"** in the settings menu
3. Find these two values:

   - **Project URL** (looks like: `https://xxxxxxxxxxxxx.supabase.co`)
   - **anon/public key** (long string under "Project API keys")

4. **Copy both values** - you'll need them next

---

## 💻 Step 4A: Local Development Setup

### Option 1: Using `.streamlit/secrets.toml` (Recommended)

1. In your project folder, create: `.streamlit/secrets.toml`
2. Add your credentials:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
```

3. **Important**: Add to `.gitignore`:
```
.streamlit/secrets.toml
```

### Option 2: Using Environment Variables

Create a `.env` file:
```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

---

## ☁️ Step 4B: Streamlit Cloud Deployment Setup

1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Connect your GitHub repository
3. Click **"Deploy"** or edit your existing app
4. Click **"Advanced settings"** → **"Secrets"**
5. Add your credentials in TOML format:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
```

6. Click **"Save"** and **"Deploy"**

---

## ✅ Step 5: Test Your Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**:
   ```bash
   streamlit run app.py
   ```

3. **Add a test entry**:
   - Fill out the fuel entry form
   - Click "Add Entry"
   - Confirm submission
   - Check if it appears in the entries viewer

4. **Verify in Supabase**:
   - Go to Supabase dashboard
   - Click "Table Editor"
   - Select `fuel_entries` table
   - You should see your test entry!

---

## 🔍 Troubleshooting

### ❌ "Supabase credentials not found"
- Check that `secrets.toml` exists in `.streamlit/` folder
- Verify the file has correct TOML syntax
- Restart the Streamlit app

### ❌ "Error inserting entry"
- Verify your Supabase project is active (not paused)
- Check that the table was created correctly
- Verify your API key is the **anon/public** key, not service_role

### ❌ "No entries showing"
- Check Supabase Table Editor to confirm data exists
- Clear browser cache and refresh
- Check browser console for JavaScript errors

---

## 📊 Managing Your Data

### View Data in Supabase Dashboard
1. Click **"Table Editor"** in Supabase
2. Select **`fuel_entries`** table
3. View, edit, or delete entries directly

### Export Data
1. In Table Editor, click **"..."** menu
2. Choose **"Export as CSV"**
3. Download your data

### Backup Database
1. Go to **"Database"** → **"Backups"** in Supabase
2. Free tier: Daily automatic backups (7-day retention)
3. Can restore from any backup point

---

## 📈 Free Tier Limits

Supabase Free Tier includes:
- ✅ 500MB database storage
- ✅ 50,000 monthly active users
- ✅ 2GB bandwidth
- ✅ Daily backups (7-day retention)
- ✅ Unlimited API requests

**More than enough for a fuel register app!**

---

## 🔒 Security Notes

- ✅ Never commit `secrets.toml` or `.env` to GitHub
- ✅ **Public access enabled** - Anyone with the app URL can add/view entries (no authentication required)
- ✅ The anon key is safe to use - it's meant for client-side access
- ✅ Supabase automatically protects against SQL injection
- ⚠️ **Note**: This setup allows public read/write access. If you need to restrict access later, you can add authentication

---

## 🆘 Need Help?

- **Supabase Docs**: https://supabase.com/docs
- **Streamlit Docs**: https://docs.streamlit.io
- **Check your Supabase project logs**: Settings → Logs

---

## ✨ Next Steps

Now that Supabase is set up:
1. Your data persists across deployments ✅
2. You can access data from multiple devices ✅
3. Data is automatically backed up ✅
4. You can scale to thousands of entries ✅

**Your fuel register is now production-ready!** 🚀
