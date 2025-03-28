import sqlite3

# Initialize database & create tables
def initialize_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Table for patient prescriptions
    cursor.execute('''CREATE TABLE IF NOT EXISTS prescriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        age INTEGER,
                        extracted_text TEXT,
                        medicines TEXT)''')

    # Create medicines table (Added alternative column)
    cursor.execute('''CREATE TABLE IF NOT EXISTS medicines (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        usage TEXT,
                        dosage TEXT,
                        alternative TEXT)''')

    # Create Orders table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_name TEXT,
                        medicine_name TEXT,
                        dosage TEXT,
                        usage TEXT,
                        status TEXT DEFAULT 'Pending')''')

    conn.commit()
    conn.close()

# Save patient data to database
def save_to_database(name, age, extracted_text, medicines):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO prescriptions (name, age, extracted_text, medicines) VALUES (?, ?, ?, ?)",
                   (name, age, extracted_text, medicines))

    conn.commit()
    conn.close()

# Add new medicine (Fixed alternative column)
def add_medicine(name, usage, dosage, alternative):
    conn = sqlite3.connect("database.db") 
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO medicines (name, usage, dosage, alternative) VALUES (?, ?, ?, ?)", 
                       (name, usage, dosage, alternative))
        conn.commit()
        print(f"✅ Medicine '{name}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"⚠️ Medicine '{name}' already exists in the database.")

    conn.close()

# Fetch all medicine names from the database with debugging
def fetch_all_medicines():
    connection = sqlite3.connect("database.db")  # DB path
    cursor = connection.cursor()
    
    # Fetch all medicine data, including alternatives
    cursor.execute("SELECT id, name, usage, dosage, alternative FROM medicines")
    medicines = cursor.fetchall()
    
    connection.close()
    
    print("Fetched Medicines:", medicines)  # Debugging: Check if data is retrieved
    return medicines

# Extract medicines from text
def extract_medicines(text):
    medicine_list = fetch_all_medicines()
    detected_medicines = []
    
    for med in medicine_list:
        id, med_name, usage, dosage, alternative = med  # tuple unpacking
        if med_name.lower() in text.lower():
            detected_medicines.append(f"{med_name} (Alternative: {alternative})" if alternative else med_name)

    return ", ".join(detected_medicines) if detected_medicines else "No medicines found"

# Save extracted medicine orders to Orders table
def save_order(patient_name, medicine_name, dosage, usage):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Orders (patient_name, medicine_name, dosage, usage) VALUES (?, ?, ?, ?)", 
                   (patient_name, medicine_name, dosage, usage))

    conn.commit()
    conn.close()

# Fetch all pending orders
def fetch_pending_orders():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Orders WHERE status = 'Pending'")
    orders = cursor.fetchall()

    conn.close()
    return orders

# Mark an order as confirmed
def confirm_order(order_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE Orders SET status = 'Confirmed' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

# Run database initialization when script runs
if __name__ == "__main__":
    initialize_database()

    # Add initial medicines to the database
    medicines_to_add = [
        ("Paracetamol", "Fever", "500mg", "Acetaminophen, Crocin, Dolo-650"),
        ("Ibuprofen", "Pain Relief", "400mg", "Naproxen, Diclofenac, Aspirin"),
        ("Amoxicillin", "Bacterial Infections", "250mg", "Cephalexin, Azithromycin, Clarithromycin"),
        ("Cetirizine", "Allergy", "10mg", "Loratadine, Fexofenadine, Levocetirizine"),
        ("Azithromycin", "Antibiotic", "500mg", "Clarithromycin, Doxycycline, Erythromycin"),
        ("Cinnarizine", "Vertigo", "50mg", "Betahistine, Dimenhydrinate, Meclizine"),
        ("ORS", "Dehydration", "As directed", "WHO ORS, Electral Powder, Pedialyte" ),
        ("Dextrose IV", "Fluid Replacement", "10-5% IV", "Ringer's Lactate, Normal Saline, Glucose IV"),
        ("Ranitidine", "Acid reflux", "150mg", "Famotidine, Omeprazole, Pantoprazole"),
        ("Domperidone", "Nausea", "10mg", "Metoclopramide, Ondansetron, Prochlorperazine"),
        ("Metformin", "Diabetes", "500mg", "Glimepiride, Sitagliptin, Pioglitazone"),
        ("Amlodipine", "High Blood Pressure", "5mg", "Nifedipine, Lisinopril, Losartan"),
        ("Atorvastatin", "Cholesterol Control", "10mg", "Rosuvastatin, Simvastatin, Pravastatin"),
        ("Pantoprazole", "Acidity", "40mg", "Omeprazole, Esomeprazole, Rabeprazole"),
        ("Augmentin", "Infections", "625mg", "Cefuroxime, Cefpodoxime, Levofloxacin"),
        ("Enzflam", "Tooth Pain", "Ibuprofen, Paracetamol, Diclofenac"),
        ("PanD", "Gastroesophageal reflux", "40mg", "Rabeprazole-D, Omeprazole-D, Esomeprazole-D")
    ]

    for med in medicines_to_add:
        add_medicine(*med)