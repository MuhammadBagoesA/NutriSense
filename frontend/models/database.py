from flask import Flaskimport, sqlite3
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

app = Flask(__name__)

# Fungsi untuk menginisialisasi database SQLite
# Fungsi untuk memeriksa dan memperbarui tabel dengan kolom id
def init_db():
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            makanan TEXT NOT NULL,
            resep TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Fungsi untuk menyimpan resep ke database
def save_recipe(makanan, resep):
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO recipes (makanan, resep) VALUES (?, ?)''', (makanan, resep))
    conn.commit()
    print(f"Resep disimpan: {makanan} - {resep}")  # Debugging: Menampilkan resep yang disimpan
    conn.close()

# Dataset contoh makanan
data = {
    'makanan': ['brokoli', 'tauge', 'kecambah', 'apel', 'pisang'],
    'kategori': ['sayur', 'sayur', 'sayur', 'buah', 'buah'],
    'kalori': [25, 30, 35, 52, 96],
    'resep': [
        'Brokoli Tumis Bawang Putih', 
        'Tauge Tumis', 
        'Kecambah Salad', 
        'Salad Buah', 
        'Smoothie Pisang'
    ]
}

df = pd.DataFrame(data)

# Model KNN
knn = KNeighborsClassifier(n_neighbors=3)

# Menggunakan kategori dan kalori sebagai fitur untuk pelatihan
X = pd.get_dummies(df[['kategori']])  # One-hot encode kategori
X['kalori'] = df['kalori']  # Menambahkan kolom kalori sebagai fitur
y = df['makanan']
knn.fit(X, y)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/how_to_use')
def how_to_use():
    return render_template('how_to_use.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        age = request.form.get('age')
        gender = request.form.get('gender')
        return render_template('data_makanan.html', age=age, gender=gender, makanan=df.to_dict('records'))
    return render_template('form.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    selected_foods = request.form.getlist('food')
    total_calories = sum(df[df['makanan'].isin(selected_foods)]['kalori'])
    
    # Kategori makanan yang dipilih
    kategori_selected = df[df['makanan'].isin(selected_foods)]['kategori'].values
    kategori_df = pd.DataFrame({'kategori': kategori_selected})
    
    # One-hot encode kategori makanan
    kategori_encoded = pd.get_dummies(kategori_df)
    
    # Menambahkan kalori yang dipilih sebagai fitur
    kalori_selected = df[df['makanan'].isin(selected_foods)]['kalori'].values
    kategori_encoded['kalori'] = kalori_selected
    
    # Pastikan kolom prediksi sama dengan kolom pelatihan
    kategori_encoded = align_features(kategori_encoded, X.columns)  # X.columns dari data pelatihan
    
    # Prediksi menggunakan KNN
    rekomendasi = knn.predict(kategori_encoded)
    
    # Ambil resep terkait dari makanan yang dipilih
    resep_terkait = df[df['makanan'].isin(rekomendasi)]['resep'].values.tolist()
    
    return render_template('total_kalori.html', 
                           total_calories=total_calories, 
                           rekomendasi=list(rekomendasi), 
                           resep_terkait=resep_terkait)

# Route untuk menambah resep baru
@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        makanan = request.form['makanan']
        resep = request.form['resep']
        save_recipe(makanan, resep)  # Menyimpan resep ke database
        return redirect(url_for('view_recipes'))  # Setelah resep ditambah, arahkan ke halaman view_recipes
    
    return render_template('add_recipe.html')  # Menampilkan form untuk menambah resep

@app.route('/view_recipes')
def view_recipes():
    # Mengambil semua resep dari database, termasuk ID
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, makanan, resep FROM recipes')  # Ambil id, makanan, dan resep
    recipes = cursor.fetchall()
    conn.close()

    # Menampilkan resep di halaman view_recipes.html
    return render_template('view_recipes.html', recipes=recipes)


@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_recipes'))  # Redirect setelah penghapusan


def align_features(input_data, reference_columns):
    """Ensure input_data has the same columns as reference_columns, filling missing ones with 0."""
    for col in reference_columns:
        if col not in input_data:
            input_data[col] = 0
    return input_data[reference_columns]

if __name__ == '__main__':
    init_db()  # Inisialisasi database saat aplikasi dijalankan
    app.run(debug=True)

